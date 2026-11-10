#!/usr/bin/env python3
"""bambu.py: the Bambu Studio project settings (Metadata/project_settings.config) for a 3MF.

Bambu Studio applies a 3MF's plate list (Metadata/model_settings.config) only when the
file also carries a project config. Without one it sets load_config = false and loads
the geometry only, all on one plate (Plater::priv::load_files, "load_config &&
config_loaded.empty()"). A partial config is not an option either: Bambu Studio fills
every missing key with its generic defaults and makes those the project's presets.

So this module builds the full config from the Bambu Lab system profiles installed with
Bambu Studio: the printer, process and filament profiles, each flattened through its
`inherits` chain and `include` templates, exactly the system presets. The project then
opens with unmodified system presets (printer, process, filament).

    printer  : machine profile whose bed (printable_area, printable_height) and nozzle match
               spec print.printer_bed / print.nozzle; print.printer (e.g. "Bambu Lab A1 mini")
               picks one when several printers share a bed size
    process  : the printer's default process if its layer height = print.layer, else a
               compatible process with that layer height ("Standard" first)
    filament : the printer's default filament if its type = the material, else
               "Bambu <MAT> Basic", else "Generic <MAT>", else the first compatible one

Profile folders searched (first with BBL/machine wins): $BAMBU_PROFILES (a BBL folder),
the user's updated copy (Windows %APPDATA%\\BambuStudio\\system\\BBL, macOS
~/Library/Application Support/BambuStudio/system/BBL, Linux ~/.config/BambuStudio/system/BBL),
then the install (C:\\Program Files\\Bambu Studio\\resources\\profiles\\BBL,
/Applications/BambuStudio.app/Contents/Resources/profiles/BBL).

    python -P bambu.py --bed 180x180x180 --nozzle 0.4 --layer 0.2 --material PLA
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# keys that describe a profile file, not a setting; Bambu's own project configs leave them out
META_KEYS = {"name", "inherits", "instantiation", "setting_id", "type", "include", "description", "from",
             "compatible_printers", "compatible_printers_condition", "compatible_prints",
             "compatible_prints_condition", "filament_id", "version", "renamed_from", "base_id", "is_custom_defined"}


def profile_dirs() -> list[Path]:
    out = []
    env = os.environ.get("BAMBU_PROFILES")
    if env:
        out.append(Path(env))
    home = Path.home()
    if os.environ.get("APPDATA"):
        out.append(Path(os.environ["APPDATA"]) / "BambuStudio" / "system" / "BBL")
    out += [home / "Library" / "Application Support" / "BambuStudio" / "system" / "BBL",
            home / ".config" / "BambuStudio" / "system" / "BBL"]
    for pf in (os.environ.get("ProgramFiles"), r"C:\Program Files"):
        if pf:
            out.append(Path(pf) / "Bambu Studio" / "resources" / "profiles" / "BBL")
    out.append(Path("/Applications/BambuStudio.app/Contents/Resources/profiles/BBL"))
    return [p for p in out if (p / "machine").is_dir()]


class Profiles:
    def __init__(self, root: Path):
        self.root = root
        self.idx: dict[tuple[str, str], dict] = {}
        for kind in ("machine", "process", "filament"):
            for p in sorted((root / kind).rglob("*.json")):
                try:
                    d = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                if isinstance(d, dict) and isinstance(d.get("name"), str):
                    self.idx[(kind, d["name"])] = d
        self._flat: dict[tuple[str, str], dict] = {}
        bundle = root.parent / "BBL.json"
        try:
            self.version = json.loads(bundle.read_text(encoding="utf-8")).get("version", "")
        except (OSError, ValueError):
            self.version = ""

    def flat(self, kind: str, name: str, depth: int = 0) -> dict:
        """Profile `name` with its inherits chain and include templates resolved (parent, includes, own keys)."""
        key = (kind, name)
        if key in self._flat:
            return self._flat[key]
        if depth > 20 or key not in self.idx:
            raise LookupError(f"Bambu profile not found: {kind}/{name}")
        d = self.idx[key]
        out = dict(self.flat(kind, d["inherits"], depth + 1)) if d.get("inherits") else {}
        for inc in d.get("include") or []:
            out.update({k: v for k, v in self.flat(kind, inc, depth + 1).items() if k not in META_KEYS})
        out.update(d)
        self._flat[key] = out
        return out

    def names(self, kind: str) -> list[str]:
        return sorted(n for k, n in self.idx if k == kind and str(self.idx[(k, n)].get("instantiation")) == "true")


def _first(v):
    return v[0] if isinstance(v, list) and v else v


def _f(v) -> float:
    try:
        return float(_first(v))
    except (TypeError, ValueError):
        return float("nan")


def _bed_of(m: dict):
    pts = [tuple(float(c) for c in s.split("x")) for s in (m.get("printable_area") or [])]
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(xs) - min(xs), max(ys) - min(ys), _f(m.get("printable_height"))


def pick_presets(prof: Profiles, bed, nozzle: float, layer: float, material: str, printer: str | None = None):
    """(machine name, process name, filament name) or LookupError with the reason."""
    machines = []
    for n in prof.names("machine"):
        m = prof.flat("machine", n)
        b = _bed_of(m)
        if not b or abs(_f(m.get("nozzle_diameter")) - nozzle) > 1e-6:
            continue
        if printer and m.get("printer_model") != printer:
            continue
        if abs(b[0] - bed[0]) > 0.5 or abs(b[1] - bed[1]) > 0.5 or (len(bed) > 2 and abs(b[2] - bed[2]) > 0.5):
            continue
        machines.append(n)
    if not machines:
        raise LookupError(f"no Bambu printer profile with a {'x'.join(f'{x:g}' for x in bed)} bed and a "
                          f"{nozzle:g} mm nozzle" + (f" for printer {printer!r}" if printer else ""))
    if len(machines) > 1:
        models = sorted({prof.flat("machine", n).get("printer_model") for n in machines})
        raise LookupError(f"several Bambu printers have this bed ({', '.join(models)}): set spec print.printer")
    mname = machines[0]
    m = prof.flat("machine", mname)

    procs = [n for n in prof.names("process")
             if mname in (prof.flat("process", n).get("compatible_printers") or [])
             and abs(_f(prof.flat("process", n).get("layer_height")) - layer) < 1e-6]
    if not procs:
        raise LookupError(f"no Bambu process profile for {mname} with a {layer:g} mm layer")
    default_p = m.get("default_print_profile")
    pname = default_p if default_p in procs else (sorted(p for p in procs if "Standard" in p) or procs)[0]

    mat = material.upper()
    fils = [n for n in prof.names("filament")
            if mname in (prof.flat("filament", n).get("compatible_printers") or [])
            and str(_first(prof.flat("filament", n).get("filament_type"))).upper() == mat]
    if not fils:
        raise LookupError(f"no Bambu filament profile of type {mat} for {mname}")
    pref = [n for n in (m.get("default_filament_profile") or []) if n in fils]
    pref += [n for n in fils if n.startswith(f"Bambu {mat} Basic")] + [n for n in fils if n.startswith(f"Generic {mat}")]
    fname = (pref or fils)[0]
    return mname, pname, fname


def project_config(bed, nozzle: float, layer: float, material: str, printer: str | None = None,
                   root: Path | None = None) -> tuple[dict, str, str]:
    """(config, application string for the 3MF, one-line summary). LookupError if it cannot be built."""
    roots = [root] if root else profile_dirs()
    if not roots:
        raise LookupError("Bambu Studio profiles not found (install Bambu Studio or set BAMBU_PROFILES)")
    prof = Profiles(roots[0])
    mname, pname, fname = pick_presets(prof, bed, nozzle, layer, material, printer)
    cfg = {}
    for kind, n in (("machine", mname), ("process", pname), ("filament", fname)):
        cfg.update({k: v for k, v in prof.flat(kind, n).items() if k not in META_KEYS})
    m, p, f = prof.flat("machine", mname), prof.flat("process", pname), prof.flat("filament", fname)
    ver = prof.version.split(".")
    app_ver = f"{ver[0]}.{ver[1]}.00.00" if len(ver) >= 2 else "02.00.00.00"
    cfg.update({
        "name": "project_settings",
        "from": "project",
        "version": app_ver,
        "printer_settings_id": mname,
        "print_settings_id": pname,
        "filament_settings_id": [fname],
        "filament_ids": [str(f.get("filament_id", ""))],
        "print_compatible_printers": list(p.get("compatible_printers") or []),
        "different_settings_to_system": ["", "", ""],
    })
    # the build plate type lives in the printer-model file (machine/<printer_model>.json), not the preset
    bed_type = m.get("default_bed_type") or prof.idx.get(("machine", str(m.get("printer_model"))), {}).get("default_bed_type")
    if bed_type:
        cfg["curr_bed_type"] = bed_type
    return cfg, f"BambuStudio-{app_ver}", f"{mname} | {pname} | {fname} (profiles {prof.version}, {roots[0]})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Show which Bambu presets a 3MF project config would use.")
    ap.add_argument("--bed", required=True, help="XxY[xZ], e.g. 180x180x180")
    ap.add_argument("--nozzle", type=float, default=0.4)
    ap.add_argument("--layer", type=float, default=0.2)
    ap.add_argument("--material", default="PLA")
    ap.add_argument("--printer", default=None, help='printer model, e.g. "Bambu Lab A1 mini"')
    a = ap.parse_args(argv)
    bed = [float(x) for x in a.bed.lower().split("x")]
    try:
        cfg, app, summary = project_config(bed, a.nozzle, a.layer, a.material, a.printer)
    except LookupError as exc:
        print(f"bambu: {exc}", file=sys.stderr)
        return 1
    print(summary)
    print(f"{len(cfg)} keys, application {app}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
