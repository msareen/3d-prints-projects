/* Showcase STL viewer. Adapted from the 3d-print-design skill's local viewer (MIT):
 * three.js r128 (core only) is loaded on demand from cdnjs with an integrity hash;
 * the STL parser and the Z-up orbit control are small built-ins, so nothing else is fetched.
 *
 *   ShowcaseViewer.mount(container, [{ url, name, color }], onStatus) -> Promise<{ setView, show, dispose }>
 */
(function () {
  'use strict';

  var THREE_URL = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
  var THREE_SRI = 'sha512-dLxUelApnYxpLt6K2iomGngnHO83iUvZytA3YjDUCjT0HDOHKXnVYdf3hU4JjM8uEhxf9nD1/ey98U3t2vZ0qQ==';
  var MAX_TRIS = 5000000;
  var VIEWS = {
    iso: [-Math.PI / 3, Math.PI / 3],
    top: [-Math.PI / 2, 0.0001],
    front: [-Math.PI / 2, Math.PI / 2],
    right: [0, Math.PI / 2]
  };
  var threePromise = null;

  function loadThree() {
    if (window.THREE) return Promise.resolve(window.THREE);
    if (threePromise) return threePromise;
    threePromise = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = THREE_URL;
      s.integrity = THREE_SRI;
      s.crossOrigin = 'anonymous';
      s.referrerPolicy = 'no-referrer';
      s.onload = function () { window.THREE ? resolve(window.THREE) : reject(new Error('three.js did not load')); };
      s.onerror = function () { threePromise = null; reject(new Error('three.js could not be loaded (offline or blocked)')); };
      document.head.appendChild(s);
    });
    return threePromise;
  }

  function parseSTL(buf) {
    var dv = new DataView(buf);
    if (buf.byteLength >= 84) {
      var n = dv.getUint32(80, true);
      if (84 + n * 50 === buf.byteLength) {
        if (n > MAX_TRIS) throw new Error('too many triangles');
        var out = new Float32Array(n * 9);
        for (var i = 0; i < n; i++) {
          var o = 84 + i * 50 + 12;
          for (var k = 0; k < 9; k++) out[i * 9 + k] = dv.getFloat32(o + k * 4, true);
        }
        return out;
      }
    }
    var text = new TextDecoder('ascii').decode(new Uint8Array(buf));
    var num = '([-+]?[\\d.]+(?:[eE][-+]?\\d+)?)';
    var re = new RegExp('vertex\\s+' + num + '\\s+' + num + '\\s+' + num, 'g');
    var vals = [];
    var m;
    while ((m = re.exec(text)) !== null) {
      vals.push(parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3]));
      if (vals.length > MAX_TRIS * 9) throw new Error('too many triangles');
    }
    return new Float32Array(vals.slice(0, vals.length - (vals.length % 9)));
  }

  function webglOK() {
    try {
      var c = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (c.getContext('webgl') || c.getContext('experimental-webgl')));
    } catch (e) { return false; }
  }

  function mount(container, parts, onStatus) {
    var status = onStatus || function () {};
    if (!webglOK()) return Promise.reject(new Error('WebGL is not available in this browser'));
    status('Loading the 3D viewer...');
    return loadThree().then(function (THREE) {
      var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      var renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      container.appendChild(renderer.domElement);

      var scene = new THREE.Scene();
      scene.background = new THREE.Color(dark ? 0x161a21 : 0xf3f4f6);
      var camera = new THREE.PerspectiveCamera(35, 1, 0.1, 50000);
      camera.up.set(0, 0, 1);
      scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 0.75));
      scene.add(new THREE.AmbientLight(0xffffff, 0.18));
      var sun = new THREE.DirectionalLight(0xffffff, 0.7);
      var fill = new THREE.DirectionalLight(0xffffff, 0.3);
      scene.add(sun, sun.target, fill, fill.target);

      var group = new THREE.Group();
      scene.add(group);
      var meshes = [];
      var disposed = false;
      var framePending = false;
      function render() {
        if (framePending || disposed) return;
        framePending = true;
        window.requestAnimationFrame(function () { framePending = false; if (!disposed) renderer.render(scene, camera); });
      }

      status('Loading ' + parts.length + ' part(s)...');
      var jobs = parts.map(function (p) {
        return fetch(p.url).then(function (r) {
          if (!r.ok) throw new Error(p.name + ': HTTP ' + r.status);
          return r.arrayBuffer();
        }).then(function (buf) {
          var pos = parseSTL(buf);
          if (pos.length < 9) throw new Error(p.name + ': no triangles');
          var geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
          geom.computeVertexNormals();
          var mesh = new THREE.Mesh(geom, new THREE.MeshStandardMaterial({
            color: p.color, roughness: 0.6, metalness: 0.05, side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1
          }));
          mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geom, 35),
            new THREE.LineBasicMaterial({ color: dark ? 0x0b0e13 : 0x1d2430, transparent: true, opacity: 0.35 })));
          return mesh;
        });
      });

      return Promise.allSettled(jobs).then(function (results) {
        var failed = 0;
        results.forEach(function (res, i) {
          if (res.status === 'fulfilled') { meshes[i] = res.value; group.add(res.value); } else { failed++; }
        });
        if (failed === parts.length) {
          renderer.dispose();
          container.removeChild(renderer.domElement);
          throw new Error('the STL files could not be loaded');
        }
        var box = new THREE.Box3().setFromObject(group);
        var size = box.getSize(new THREE.Vector3());
        // a floor grid under the parts, 10 mm squares
        var span = Math.ceil(Math.max(size.x, size.y, 20) * 1.4 / 10) * 10;
        var grid = new THREE.GridHelper(span, span / 10, dark ? 0x3a4250 : 0xb8bec8, dark ? 0x262c36 : 0xd9dde3);
        grid.rotation.x = Math.PI / 2;
        grid.position.set((box.min.x + box.max.x) / 2, (box.min.y + box.max.y) / 2, box.min.z - 0.05);
        scene.add(grid);

        // orbit control (Z up) -----------------------------------------------------
        var orbit = { target: new THREE.Vector3(), r: 200, theta: VIEWS.iso[0], phi: VIEWS.iso[1] };
        function updateCamera() {
          var sp = Math.sin(orbit.phi);
          camera.position.set(
            orbit.target.x + orbit.r * sp * Math.cos(orbit.theta),
            orbit.target.y + orbit.r * sp * Math.sin(orbit.theta),
            orbit.target.z + orbit.r * Math.cos(orbit.phi));
          camera.lookAt(orbit.target);
          sun.position.copy(camera.position).add(new THREE.Vector3(0, 0, orbit.r * 0.6));
          sun.target.position.copy(orbit.target);
          fill.position.copy(orbit.target).sub(camera.position).add(orbit.target);
          fill.position.z = orbit.target.z + orbit.r * 0.4;
          fill.target.position.copy(orbit.target);
          sun.target.updateMatrixWorld();
          fill.target.updateMatrixWorld();
          render();
        }
        function frame() {
          var b = new THREE.Box3().setFromObject(group);
          var sphere = b.getBoundingSphere(new THREE.Sphere());
          orbit.target.copy(sphere.center);
          var fov = camera.fov * Math.PI / 180;
          orbit.r = Math.max(10, sphere.radius / Math.sin(Math.min(fov, fov * camera.aspect) / 2)) * 0.9;
        }
        function setView(name) {
          var v = VIEWS[name] || VIEWS.iso;
          orbit.theta = v[0];
          orbit.phi = v[1];
          frame();
          updateCamera();
        }
        function resize() {
          var w = container.clientWidth || 400, h = container.clientHeight || 300;
          renderer.setSize(w, h, false);
          renderer.domElement.style.width = '100%';
          renderer.domElement.style.height = '100%';
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          render();
        }

        var c = renderer.domElement;
        var pointers = {}, mode = null, pinchStart = 1, rStart = 0;
        c.addEventListener('contextmenu', function (e) { e.preventDefault(); });
        c.addEventListener('pointerdown', function (e) {
          c.setPointerCapture(e.pointerId);
          pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
          var ids = Object.keys(pointers);
          if (ids.length === 2) {
            var a = pointers[ids[0]], b = pointers[ids[1]];
            pinchStart = Math.hypot(a.x - b.x, a.y - b.y) || 1;
            rStart = orbit.r;
            mode = 'pinch';
          } else {
            mode = (e.button === 2 || e.shiftKey) ? 'pan' : 'rotate';
          }
        });
        c.addEventListener('pointermove', function (e) {
          var p = pointers[e.pointerId];
          if (!p) return;
          var dx = e.clientX - p.x, dy = e.clientY - p.y;
          p.x = e.clientX; p.y = e.clientY;
          if (mode === 'rotate') {
            orbit.theta -= dx * 0.008;
            orbit.phi = Math.min(Math.PI - 0.001, Math.max(0.0001, orbit.phi - dy * 0.008));
          } else if (mode === 'pan') {
            var scale = 2 * orbit.r * Math.tan(camera.fov * Math.PI / 360) / c.clientHeight;
            var right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);
            var up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1);
            orbit.target.addScaledVector(right, -dx * scale).addScaledVector(up, dy * scale);
          } else if (mode === 'pinch') {
            var ids = Object.keys(pointers);
            if (ids.length === 2) {
              var a = pointers[ids[0]], b = pointers[ids[1]];
              orbit.r = Math.max(1, rStart * pinchStart / (Math.hypot(a.x - b.x, a.y - b.y) || 1));
            }
          }
          updateCamera();
        });
        function up(e) { delete pointers[e.pointerId]; if (!Object.keys(pointers).length) mode = null; }
        c.addEventListener('pointerup', up);
        c.addEventListener('pointercancel', up);
        c.addEventListener('wheel', function (e) {
          e.preventDefault();
          orbit.r = Math.max(1, Math.min(40000, orbit.r * Math.exp(e.deltaY * 0.001)));
          updateCamera();
        }, { passive: false });

        var ro = window.ResizeObserver ? new ResizeObserver(resize) : null;
        if (ro) ro.observe(container); else window.addEventListener('resize', resize);
        resize();
        setView('iso');
        status(parts.length - failed + ' part(s) shown' + (failed ? ', ' + failed + ' failed to load' : '') +
          '. Drag to rotate, right-drag or shift-drag to pan, scroll or pinch to zoom.');

        return {
          setView: setView,
          show: function (i, on) { if (meshes[i]) { meshes[i].visible = on; render(); } },
          dispose: function () {
            disposed = true;
            if (ro) ro.disconnect(); else window.removeEventListener('resize', resize);
            scene.traverse(function (o) {
              if (o.geometry) o.geometry.dispose();
              if (o.material) o.material.dispose();
            });
            renderer.dispose();
            if (renderer.forceContextLoss) renderer.forceContextLoss();
            if (c.parentNode) c.parentNode.removeChild(c);
          }
        };
      });
    });
  }

  window.ShowcaseViewer = { mount: mount };
})();
