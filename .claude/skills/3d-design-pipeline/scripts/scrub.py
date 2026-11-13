#!/usr/bin/env python3
"""scrub.py: strip location and device metadata from the photos in a project's input/ (stdlib only).

Phone photos carry GPS coordinates, a timestamp, the phone model and sometimes a
thumbnail in EXIF/XMP. A repo that is pushed publishes all of that. This removes it
without re-encoding: the pixels are byte-identical.

JPEG: every APP1 (EXIF, XMP), APP13 (Photoshop/IPTC), COM segment and every byte after
the end-of-image marker (Samsung/Google motion-photo and "SEF" trailers) is dropped. The
EXIF orientation is kept as a minimal EXIF block so the photo still shows upright.
PNG: eXIf, tEXt, zTXt, iTXt and tIME chunks are dropped.
Other image types (HEIC, TIFF, WebP, ...) are not rewritten; `find_gps` only reports
them as "unchecked".

    python scrub.py <folder-or-file> ...      scrub in place, print what changed
    python scrub.py --check <folder> ...      report only; exit 1 if any file has GPS
"""
from __future__ import annotations

import os
import stat
import struct
import sys
from pathlib import Path

JPEG_EXT = {".jpg", ".jpeg", ".jpe"}
PNG_EXT = {".png"}
OTHER_IMAGE_EXT = {".heic", ".heif", ".tif", ".tiff", ".webp", ".avif", ".dng", ".gif", ".bmp"}
GPS_IFD_TAG = 0x8825
ORIENTATION_TAG = 0x0112
XMP_GPS_MARKERS = (b"GPSLatitude", b"GPSLongitude", b"exif:GPS", b"GPSPosition")
PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_DROP = {b"eXIf", b"tEXt", b"zTXt", b"iTXt", b"tIME"}


# --------------------------------------------------------------------------
# minimal TIFF/EXIF reader: only what is needed to find GPS and orientation
def _read_ifd0(tiff: bytes):
    """Returns (has_gps, orientation) from a TIFF block; (False, 1) if it cannot be parsed."""
    if len(tiff) < 8 or tiff[:2] not in (b"II", b"MM"):
        return False, 1
    e = "<" if tiff[:2] == b"II" else ">"
    try:
        (off,) = struct.unpack(e + "I", tiff[4:8])
        (count,) = struct.unpack(e + "H", tiff[off:off + 2])
        has_gps, orient = False, 1
        for i in range(min(count, 512)):
            ent = tiff[off + 2 + 12 * i: off + 14 + 12 * i]
            tag, typ, _n = struct.unpack(e + "HHI", ent[:8])
            if tag == GPS_IFD_TAG:
                has_gps = True
            elif tag == ORIENTATION_TAG and typ == 3:
                (orient,) = struct.unpack(e + "H", ent[8:10])
        return has_gps, orient
    except struct.error:
        return False, 1


def _jpeg_segments(data: bytes):
    """Yields (marker, start, end) for each segment up to and including SOS.
    `end` is the offset after the segment's header+payload; for SOS it is where the
    entropy-coded data starts. Raises ValueError on a malformed file."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    pos = 2
    while pos < len(data):
        if data[pos] != 0xFF:
            raise ValueError(f"bad marker at {pos}")
        while pos < len(data) and data[pos] == 0xFF:        # fill bytes
            pos += 1
        marker = data[pos]
        pos += 1
        if marker == 0xD9:
            return
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:       # standalone markers
            continue
        (length,) = struct.unpack(">H", data[pos:pos + 2])
        start, end = pos - 2, pos + length
        yield marker, start, end
        if marker == 0xDA:                                   # SOS: entropy data follows
            return
        pos = end


def _jpeg_eoi(data: bytes, scan_start: int) -> int:
    """Offset just after the first EOI in the entropy-coded data (inside it an FF is
    always followed by 00 or an RSTn, so the first FF D9 is the real end)."""
    i = scan_start
    while True:
        i = data.find(b"\xff", i)
        if i < 0 or i + 1 >= len(data):
            return len(data)
        nxt = data[i + 1]
        if nxt == 0xD9:
            return i + 2
        i += 2 if nxt in (0x00, 0xFF) or 0xD0 <= nxt <= 0xD7 else 1


def _orientation_app1(orient: int) -> bytes:
    """A minimal EXIF APP1 holding only the orientation tag (big-endian)."""
    tiff = b"MM\x00\x2a" + struct.pack(">I", 8) + struct.pack(">H", 1) \
        + struct.pack(">HHI", ORIENTATION_TAG, 3, 1) + struct.pack(">H", orient) + b"\x00\x00" \
        + struct.pack(">I", 0)
    body = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + struct.pack(">H", len(body) + 2) + body


def inspect_jpeg(data: bytes) -> dict:
    """{'gps': bool, 'meta': [segment names found], 'orientation': int, 'trailer': bytes}"""
    gps, orient, meta = False, 1, []
    scan_start = 0
    for marker, start, end in _jpeg_segments(data):
        payload = data[start + 4:end]
        if marker == 0xE1 and payload.startswith(b"Exif\x00\x00"):
            meta.append("EXIF")
            g, o = _read_ifd0(payload[6:])
            gps, orient = gps or g, o
        elif marker == 0xE1:
            meta.append("XMP")
            gps = gps or any(m in payload for m in XMP_GPS_MARKERS)
        elif marker == 0xED:
            meta.append("IPTC")
        elif marker == 0xFE:
            meta.append("comment")
        if marker == 0xDA:
            scan_start = end
    trailer = len(data) - _jpeg_eoi(data, scan_start) if scan_start else 0
    if trailer > 0:
        meta.append(f"{trailer} trailing bytes")
        gps = gps or any(m in data[_jpeg_eoi(data, scan_start):] for m in XMP_GPS_MARKERS)
    return {"gps": gps, "meta": meta, "orientation": orient}


def scrub_jpeg(data: bytes) -> bytes:
    info = inspect_jpeg(data)
    out = [b"\xff\xd8"]
    scan_start = 0
    keep_orient = info["orientation"] not in (0, 1)
    for marker, start, end in _jpeg_segments(data):
        if marker in (0xE1, 0xED, 0xFE):
            continue
        if marker == 0xDA:
            scan_start = end
            out.append(data[start:end])
            break
        out.append(data[start:end])
        if marker == 0xE0 and keep_orient:                   # after JFIF, before the tables
            out.append(_orientation_app1(info["orientation"]))
            keep_orient = False
    if keep_orient:
        out.insert(1, _orientation_app1(info["orientation"]))
    out.append(data[scan_start:_jpeg_eoi(data, scan_start)])
    return b"".join(out)


# --------------------------------------------------------------------------
def _png_chunks(data: bytes):
    pos = 8
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        typ = data[pos + 4:pos + 8]
        yield typ, pos, pos + 12 + length
        pos += 12 + length
        if typ == b"IEND":
            return


def inspect_png(data: bytes) -> dict:
    gps, meta = False, []
    for typ, start, end in _png_chunks(data):
        if typ in PNG_DROP:
            meta.append(typ.decode())
            gps = gps or any(m in data[start:end] for m in XMP_GPS_MARKERS)
            if typ == b"eXIf":
                gps = gps or _read_ifd0(data[start + 8:end - 4])[0]
    return {"gps": gps, "meta": meta}


def scrub_png(data: bytes) -> bytes:
    out = [data[:8]]
    for typ, start, end in _png_chunks(data):
        if typ not in PNG_DROP:
            out.append(data[start:end])
    return b"".join(out)


# --------------------------------------------------------------------------
def find_gps(path: Path):
    """Returns 'gps', 'meta' (metadata but no GPS), 'clean', or 'unchecked' (an image type
    this module cannot read). Returns None for files that are not images."""
    ext = path.suffix.lower()
    try:
        if ext in JPEG_EXT:
            info = inspect_jpeg(path.read_bytes())
        elif ext in PNG_EXT:
            data = path.read_bytes()
            if data[:8] != PNG_SIG:
                return "unchecked"
            info = inspect_png(data)
        elif ext in OTHER_IMAGE_EXT:
            return "unchecked"
        else:
            return None
    except (ValueError, struct.error):
        return "unchecked"
    return "gps" if info["gps"] else ("meta" if info["meta"] else "clean")


def scrub_file(path: Path) -> str:
    """Scrubs one file in place. Returns 'scrubbed', 'clean', 'unchecked' or 'skipped'."""
    ext = path.suffix.lower()
    if ext not in JPEG_EXT | PNG_EXT:
        return "unchecked" if ext in OTHER_IMAGE_EXT else "skipped"
    data = path.read_bytes()
    try:
        if ext in JPEG_EXT:
            new = scrub_jpeg(data)
            if inspect_jpeg(new)["meta"] and any(m != "EXIF" for m in inspect_jpeg(new)["meta"]):
                raise ValueError("metadata survived the scrub")
        else:
            if data[:8] != PNG_SIG:
                return "unchecked"
            new = scrub_png(data)
    except (ValueError, struct.error):
        return "unchecked"
    if new == data:
        return "clean"
    tmp = path.with_name(path.name + ".scrub.tmp")
    tmp.write_bytes(new)
    if not os.access(path, os.W_OK):                      # photos copied from a phone are often read-only
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    tmp.replace(path)
    return "scrubbed"


def iter_images(root: Path):
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in JPEG_EXT | PNG_EXT | OTHER_IMAGE_EXT:
            yield p


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check" in args
    paths = [Path(a) for a in args if a != "--check"]
    if not paths:
        print(__doc__)
        return 2
    bad = 0
    for root in paths:
        for f in iter_images(root):
            if check_only:
                state = find_gps(f)
                if state in ("gps", "unchecked"):
                    print(f"  {state:9} {f}")
                bad += state == "gps"
            else:
                state = scrub_file(f)
                if state != "clean":
                    print(f"  {state:9} {f}")
    if check_only:
        print("GPS found" if bad else "no GPS found")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
