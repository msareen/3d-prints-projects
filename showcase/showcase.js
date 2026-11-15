/* Showcase page: reads projects.json (written by showcase/build.py) and renders a
 * gallery (#/) and one page per project (#/<project>). Text from the repository is
 * only ever placed with textContent; file paths come from the generator and are
 * URL-encoded per segment. */
(function () {
  'use strict';

  var COLORS = ['#e07a2f', '#3b82c4', '#4aa564', '#c4508a', '#8a6fd1', '#c9a227', '#3fb0b0', '#d0574e'];
  var SLUG = /^[a-z0-9][a-z0-9-]{0,63}$/;
  var app = document.getElementById('app');
  var data = null;
  var viewer = null;
  var viewerToken = 0;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = String(text);
    return e;
  }
  function add(parent) { for (var i = 1; i < arguments.length; i++) if (arguments[i]) parent.appendChild(arguments[i]); return parent; }
  function url(path) { return String(path).split('/').map(encodeURIComponent).join('/'); }
  function bytes(n) {
    if (n >= 1e6) return (n / 1e6).toFixed(1) + ' MB';
    if (n >= 1e3) return Math.round(n / 1e3) + ' kB';
    return n + ' B';
  }
  function mm(v) { return (Math.round(Number(v) * 10) / 10).toString(); }
  function date(iso) {
    var d = iso ? new Date(iso) : null;
    return d && !isNaN(d) ? d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : '';
  }
  function link(href, text, opts) {
    var a = el('a', opts && opts.cls, text);
    a.href = href;
    if (opts && opts.download) a.setAttribute('download', '');
    if (opts && opts.blank) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    return a;
  }
  function img(path, alt, cls) {
    var i = el('img', cls);
    i.src = url(path);
    i.alt = alt || '';
    i.loading = 'lazy';
    i.decoding = 'async';
    return i;
  }
  function section(title, cls) {
    var s = el('section', 'block ' + (cls || ''));
    add(s, el('h2', null, title));
    return s;
  }
  function chip(text, cls) { return el('span', 'chip ' + (cls || ''), text); }

  function closeViewer() {
    viewerToken++;
    if (viewer) { viewer.dispose(); viewer = null; }
  }

  // ------------------------------------------------------------------ gallery
  function renderGallery() {
    document.title = '3D prints showcase';
    var wrap = el('div');
    var intro = el('section', 'intro');
    add(intro,
      el('h1', null, 'What has been built'),
      el('p', null, data.projects.length + ' part(s), each designed from photos and measurements. ' +
        'Open one to see what it started from, turn the model in 3D, and download the files to print it.'));
    var grid = el('div', 'grid');
    data.projects.forEach(function (p) {
      var card = link('#/' + p.slug, null, { cls: 'card' });
      var fig = el('div', 'cover');
      if (p.cover) add(fig, img(p.cover, p.title));
      else add(fig, el('span', 'nocover', 'No preview'));
      var body = el('div', 'card-body');
      var chips = el('div', 'chips');
      p.materials.forEach(function (m) { add(chips, chip(m)); });
      add(chips, chip('rev ' + p.revision, 'muted'));
      if (p.printed.length) add(chips, chip('printed', 'ok'));
      add(body, el('h2', null, p.title), el('p', 'summary', p.summary), chips);
      add(card, fig, body);
      add(grid, card);
    });
    if (!data.projects.length) add(grid, el('p', 'empty', 'No released projects yet.'));
    add(wrap, intro, grid);
    return wrap;
  }

  // ------------------------------------------------------------------ project page
  function facts(p) {
    var dl = el('dl', 'facts');
    function row(k, v) { if (v) add(dl, add(el('div', k === 'Orientation' ? 'wide' : null), el('dt', null, k), el('dd', null, v))); }
    var env = p.envelope;
    row('Size', env && env.x ? mm(env.x) + ' x ' + mm(env.y) + ' x ' + mm(env.z) + ' mm' : '');
    row('Parts', String(p.parts.length));
    row('Materials', p.materials.join(', '));
    row('Spec revision', String(p.revision));
    row('Released', date(p.released_utc));
    row('Print', [p.nozzle ? p.nozzle + ' mm nozzle' : '', p.layer ? p.layer + ' mm layers' : ''].filter(Boolean).join(', '));
    row('Orientation', p.orientation);
    return dl;
  }

  function inputsBlock(p) {
    var s = section('What it started from', 'inputs');
    if (p.brief) {
      add(s, el('h3', null, 'Brief'), el('pre', 'brief', p.brief.replace(/^#[^\n]*\n+/, '').trim()));
    }
    if (p.parts.length) {
      var ul = el('ul', 'parts');
      p.parts.forEach(function (part) {
        var li = el('li');
        add(li, el('strong', null, part.name), part.description ? el('span', null, ': ' + part.description) : null);
        add(ul, li);
      });
      add(s, el('h3', null, 'Parts'), ul);
    }
    if (p.inputs.length) {
      add(s, el('h3', null, 'Photos, sketches and drawings'));
      var g = el('div', 'thumbs');
      p.inputs.forEach(function (f) {
        var fig = el('figure');
        var a = link(url(f.path), null, { blank: true });
        if (f.kind === 'image') add(a, img(f.path, f.notes || f.name));
        else add(a, el('span', 'file-tile', f.name));
        add(fig, a);
        if (f.notes) add(fig, el('figcaption', null, f.notes));
        add(g, fig);
      });
      add(s, g);
    }
    return s;
  }

  function previewBlock(p) {
    var s = section('Built preview', 'preview');
    var mats = p.downloads.filter(function (d) { return d.files.some(function (f) { return f.kind === 'stl'; }); });
    if (mats.length) {
      var bar = el('div', 'toolbar');
      var select = null;
      if (mats.length > 1) {
        var lab = el('label', null, 'Material ');
        select = el('select');
        mats.forEach(function (d, i) { var o = el('option', null, d.material); o.value = String(i); add(select, o); });
        add(lab, select);
        add(bar, lab);
      }
      var views = el('div', 'views');
      ['iso', 'front', 'right', 'top'].forEach(function (v) {
        var b = el('button', null, v === 'iso' ? '3D' : v.charAt(0).toUpperCase() + v.slice(1));
        b.type = 'button';
        b.addEventListener('click', function () { if (viewer) viewer.setView(v); });
        add(views, b);
      });
      add(bar, views);
      var toggles = el('div', 'toggles');
      var stage = el('div', 'stage');
      var status = el('p', 'status');
      add(s, bar, stage, toggles, status);

      var load = function (d) {
        closeViewer();
        var token = viewerToken;
        var stls = d.files.filter(function (f) { return f.kind === 'stl'; });
        toggles.textContent = '';
        stage.textContent = '';
        var parts = stls.map(function (f, i) {
          return { url: url(f.path), name: f.part, color: COLORS[i % COLORS.length] };
        });
        if (stls.length > 1) {
          stls.forEach(function (f, i) {
            var lab = el('label');
            var cb = el('input');
            cb.type = 'checkbox';
            cb.checked = true;
            cb.addEventListener('change', function () { if (viewer) viewer.show(i, cb.checked); });
            var sw = el('span', 'swatch');
            sw.style.background = parts[i].color;
            add(lab, cb, sw, el('span', null, f.part));
            add(toggles, lab);
          });
        }
        window.ShowcaseViewer.mount(stage, parts, function (t) { if (token === viewerToken) status.textContent = t; })
          .then(function (v) {
            if (token !== viewerToken) { v.dispose(); return; }
            viewer = v;
          })
          .catch(function (err) {
            if (token !== viewerToken) return;
            stage.classList.add('failed');
            status.textContent = 'No 3D view: ' + err.message + '. The pictures below show the model.';
          });
      };
      if (select) select.addEventListener('change', function () { load(mats[Number(select.value)]); });
      load(mats[0]);
    }
    var pics = p.renders.slice();
    var drawing = p.shared.filter(function (f) { return f.kind === 'drawing'; })[0];
    if (pics.length) {
      add(s, el('h3', null, 'Renders'));
      var g = el('div', 'thumbs wide');
      pics.forEach(function (f) {
        var fig = el('figure');
        add(fig, add(link(url(f.path), null, { blank: true }), img(f.path, f.name)));
        add(g, fig);
      });
      add(s, g);
    }
    if (drawing) {
      add(s, el('h3', null, 'Drawing sheet'));
      var fig = el('figure', 'sheet');
      add(fig, add(link(url(drawing.path), null, { blank: true }), img(drawing.path, 'Drawing sheet: elevations and plan section')));
      add(fig, el('figcaption', null, 'Front, side and top elevations plus a plan section, checked against the spec.'));
      add(s, fig);
    }
    return s;
  }

  function printedBlock(p) {
    var s = section('The print', 'printed');
    if (p.printed.length) {
      var g = el('div', 'thumbs wide');
      p.printed.forEach(function (f) {
        var fig = el('figure');
        add(fig, add(link(url(f.path), null, { blank: true }), img(f.path, 'Printed ' + p.title)));
        add(g, fig);
      });
      add(s, g);
    } else {
      add(s, el('p', 'empty', 'No photo of the printed part yet.'));
    }
    return s;
  }

  function downloadsBlock(p) {
    var s = section('Download', 'downloads');
    var cols = el('div', 'dl-grid');
    p.downloads.forEach(function (d) {
      var card = el('div', 'dl-card');
      add(card, el('h3', null, d.material));
      var ul = el('ul');
      d.files.forEach(function (f) {
        var li = el('li', f.kind === '3mf' ? 'main' : null);
        var label = {
          '3mf': 'Slicer project (3MF)', stl: f.part + ' (STL)', sheet: 'Print sheet', plates: 'Plate layout'
        }[f.kind] || f.name;
        add(li, link(url(f.path), label, { download: true }));
        var meta = [bytes(f.bytes)];
        if (f.kind === 'stl' && f.size_mm) meta.unshift(f.size_mm.map(mm).join(' x ') + ' mm');
        if (f.kind === 'stl' && f.mass_g) meta.push('max ' + mm(f.mass_g) + ' g');
        add(li, el('span', 'meta', meta.join(' · ')));
        add(ul, li);
      });
      add(card, ul);
      add(cols, card);
    });
    if (p.shared.length) {
      var card = el('div', 'dl-card');
      add(card, el('h3', null, 'Design records'));
      var ul = el('ul');
      p.shared.forEach(function (f) {
        var label = { drawing: 'Drawing sheet (SVG)', spec: 'Specification', release: 'Release record (checksums)' }[f.kind];
        var li = el('li');
        add(li, link(url(f.path), label || f.name, { download: true }), el('span', 'meta', bytes(f.bytes)));
        add(ul, li);
      });
      add(card, ul);
      add(cols, card);
    }
    add(s, cols);
    add(s, el('p', 'note', 'Open the 3MF in PrusaSlicer, Bambu Studio, OrcaSlicer or Cura. The print sheet lists the ' +
      'slicer settings and fits used for that material.'));
    return s;
  }

  function renderProject(p) {
    document.title = p.title + ' · 3D prints showcase';
    var wrap = el('article', 'project');
    var head = el('header', 'project-head');
    add(head, link('#/', '← All projects', { cls: 'back' }), el('h1', null, p.title), el('p', 'lead', p.summary));
    if (data.repo) add(head, link(data.repo + '/tree/main/' + url(p.source), 'Project folder on GitHub', { cls: 'src', blank: true }));
    add(wrap, head, facts(p), inputsBlock(p), previewBlock(p), printedBlock(p), downloadsBlock(p));
    return wrap;
  }

  // ------------------------------------------------------------------ routing
  function route() {
    if (!data) return;
    closeViewer();
    var slug = decodeURIComponent((location.hash || '').replace(/^#\/?/, ''));
    var p = SLUG.test(slug) ? data.projects.filter(function (x) { return x.slug === slug; })[0] : null;
    app.textContent = '';
    if (slug && !p) {
      add(app, el('p', 'empty', 'No project called "' + slug + '".'), link('#/', '← All projects', { cls: 'back' }));
    } else {
      add(app, p ? renderProject(p) : renderGallery());
    }
    window.scrollTo(0, 0);
  }

  fetch('projects.json').then(function (r) {
    if (!r.ok) throw new Error('projects.json: HTTP ' + r.status);
    return r.json();
  }).then(function (d) {
    data = d;
    data.projects = Array.isArray(d.projects) ? d.projects : [];
    if (/^https:\/\/github\.com\//.test(d.repo || '')) {
      var a = document.getElementById('repo-link');
      a.href = d.repo;
      a.hidden = false;
    } else {
      data.repo = '';
    }
    if (d.generated_utc) document.getElementById('generated').textContent = 'Updated ' + date(d.generated_utc) + '.';
    window.addEventListener('hashchange', route);
    route();
  }).catch(function (err) {
    app.textContent = '';
    add(app, el('p', 'empty', 'Could not load the project list (' + err.message + ').'));
  });
})();
