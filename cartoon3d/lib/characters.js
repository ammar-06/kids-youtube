// 3D characters for the kids channel, built from smooth rounded shapes (Three.js r149, global THREE).
// Each builder returns { root, parts, setMouth(name), setEyes(name) } where the root's feet are at y = 0,
// facing +z. Mouths: "closed", "smile", "o", "laugh". Eyes: "open", "closed", "happy".
(function () {
  const T = THREE;
  const M = (c, r = 0.55, extra = {}) => new T.MeshStandardMaterial(Object.assign({ color: c, roughness: r, metalness: 0 }, extra));
  const sph = (r = 1, w = 48, h = 32) => new T.SphereGeometry(r, w, h);
  const cap = (r, l) => new T.CapsuleGeometry(r, l, 12, 24);
  function mesh(geo, mat, parent, pos = [0, 0, 0], scale = [1, 1, 1], rot = [0, 0, 0]) {
    const m = new T.Mesh(geo, mat);
    m.position.set(...pos); m.scale.set(...scale); m.rotation.set(...rot);
    m.castShadow = true; m.receiveShadow = true;
    parent.add(m);
    return m;
  }
  function group(parent, pos = [0, 0, 0], rot = [0, 0, 0]) {
    const g = new T.Group(); g.position.set(...pos); g.rotation.set(...rot); parent.add(g); return g;
  }
  function canvasTex(w, h, draw, repeat) {
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    draw(c.getContext("2d"), w, h);
    const t = new T.CanvasTexture(c);
    t.encoding = T.sRGBEncoding;
    if (repeat) { t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(...repeat); }
    return t;
  }

  // ------------------------------------------------------------------ face parts
  function eye(parent, x, y, z, r, lidMat, irisCol = "#5a2f17") {
    const g = group(parent, [x, y, z]);
    const open = group(g);
    mesh(sph(r), M("#ffffff", 0.15), open, [0, 0, 0], [1, 1.1, 0.6]);
    mesh(sph(r * 0.76), M(irisCol, 0.15), open, [0, -r * 0.04, r * 0.34], [1, 1.06, 0.5]);
    mesh(sph(r * 0.38), M("#0e0604", 0.15), open, [0, -r * 0.05, r * 0.55], [1, 1.08, 0.4]);
    mesh(sph(r * 0.2), M("#ffffff", 0.05, { emissive: "#ffffff", emissiveIntensity: 0.7 }), open, [r * 0.27, r * 0.28, r * 0.66]);
    mesh(sph(r * 0.09), M("#ffffff", 0.05, { emissive: "#ffffff", emissiveIntensity: 0.7 }), open, [-r * 0.24, -r * 0.3, r * 0.66]);
    const closed = group(g);
    mesh(sph(r * 1.06), lidMat, closed, [0, 0, -r * 0.05], [1, 1.1, 0.62]);
    mesh(new T.TorusGeometry(r * 0.75, r * 0.09, 8, 24, Math.PI), M("#3a1d10", 0.5), closed, [0, -r * 0.1, r * 0.62], [1, 0.75, 1], [0, 0, Math.PI]);
    const happy = group(g);
    mesh(sph(r * 1.06), lidMat, happy, [0, 0, -r * 0.05], [1, 1.1, 0.62]);
    mesh(new T.TorusGeometry(r * 0.7, r * 0.1, 8, 24, Math.PI), M("#3a1d10", 0.5), happy, [0, -r * 0.2, r * 0.62], [1, 0.9, 1]);
    closed.visible = happy.visible = false;
    g.userData = { open, closed, happy };
    return g;
  }
  function setEyes(eyes, name) { for (const e of eyes) for (const k of ["open", "closed", "happy"]) e.userData[k].visible = k === name; }

  function mouthSet(parent, pos, w, tilt = -0.2, lipCol = "#7c1d24", teeth = true) {
    const g = group(parent, pos, [tilt, 0, 0]);
    const dark = M(lipCol, 0.95), tongue = M("#ff7d8c", 0.9), tooth = M("#ffffff", 0.6);
    const half = (r) => new T.CircleGeometry(r, 32, Math.PI, Math.PI);
    const smile = group(g);
    mesh(half(w), dark, smile, [0, 0, 0], [1, 0.85, 1]);
    mesh(half(w * 0.6), tongue, smile, [0, -w * 0.38, 0.004], [1, 0.6, 1]);
    if (teeth) for (const s of [-1, 1]) mesh(new T.BoxGeometry(w * 0.22, w * 0.2, 0.01), tooth, smile, [s * w * 0.13, -w * 0.08, 0.006]);
    const laugh = group(g);
    mesh(half(w * 1.25), dark, laugh, [0, 0.02, 0], [1, 1.05, 1]);
    mesh(half(w * 0.75), tongue, laugh, [0, -w * 0.6, 0.004], [1, 0.6, 1]);
    if (teeth) for (const s of [-1, 1]) mesh(new T.BoxGeometry(w * 0.24, w * 0.2, 0.01), tooth, laugh, [s * w * 0.14, -w * 0.06, 0.006]);
    const o = group(g);
    mesh(new T.CircleGeometry(w * 0.42, 32), dark, o, [0, -w * 0.3, 0], [1, 1.25, 1]);
    mesh(new T.CircleGeometry(w * 0.24, 32), tongue, o, [0, -w * 0.55, 0.004], [1, 0.6, 1]);
    const closed = group(g);
    mesh(new T.TorusGeometry(w * 0.7, w * 0.07, 8, 24, Math.PI), dark, closed, [0, w * 0.35, 0], [1, 0.7, 1], [0, 0, Math.PI]);
    const all = { smile, laugh, o, closed };
    function set(name) { for (const k in all) all[k].visible = k === name; }
    set("smile");
    return { g, set };
  }

  // ------------------------------------------------------------------ Mo
  function buildMo() {
    const root = new T.Group();
    const body = group(root);
    const skin = M("#c98663", 0.55), shirt = M("#3fae4a", 0.65), shorts = M("#263a86", 0.7), shoe = M("#ff7a2f", 0.5),
      sole = M("#ffffff", 0.5), sock = M("#ffffff", 0.7), hair = M("#141012", 0.75);
    const legs = [];
    for (const s of [-1, 1]) {
      const L = group(body, [s * 0.24, 0.92, 0]);
      mesh(cap(0.15, 0.36), skin, L, [0, -0.32, 0]);
      mesh(new T.CylinderGeometry(0.16, 0.16, 0.16, 24), sock, L, [0, -0.6, 0]);
      mesh(sph(0.24), shoe, L, [0, -0.78, 0.07], [0.85, 0.55, 1.25]);
      mesh(sph(0.25), sole, L, [0, -0.86, 0.07], [0.88, 0.22, 1.28]);
      legs.push(L);
    }
    mesh(sph(0.5), shorts, body, [0, 1.0, 0], [1.08, 0.62, 0.86]);
    for (const s of [-1, 1]) mesh(new T.CylinderGeometry(0.2, 0.22, 0.24, 24), shorts, body, [s * 0.24, 0.84, 0]);
    mesh(sph(0.56), shirt, body, [0, 1.42, 0], [1, 1.0, 0.82]);
    const rocket = canvasTex(256, 256, (x) => {
      x.fillStyle = "#ffffff"; x.translate(128, 128); x.rotate(0.6);
      x.beginPath(); x.moveTo(0, -95); x.quadraticCurveTo(52, -40, 34, 55); x.lineTo(-34, 55); x.quadraticCurveTo(-52, -40, 0, -95); x.fill();
      x.beginPath(); x.moveTo(-34, 20); x.lineTo(-64, 70); x.lineTo(-30, 58); x.fill();
      x.beginPath(); x.moveTo(34, 20); x.lineTo(64, 70); x.lineTo(30, 58); x.fill();
      x.beginPath(); x.moveTo(-18, 62); x.lineTo(0, 100); x.lineTo(18, 62); x.fill();
      x.fillStyle = "#3fae4a"; x.beginPath(); x.arc(0, -25, 16, 0, 7); x.fill();
    });
    mesh(new T.PlaneGeometry(0.42, 0.42), new T.MeshStandardMaterial({ map: rocket, transparent: true, roughness: 0.6 }), body, [0, 1.47, 0.462]);
    const arms = [];
    for (const s of [-1, 1]) {
      const A = group(body, [s * 0.5, 1.72, 0]);
      mesh(sph(0.2), shirt, A, [s * 0.04, -0.06, 0], [1, 1.05, 1]);
      mesh(cap(0.12, 0.4), skin, A, [s * 0.1, -0.38, 0], [1, 1, 1], [0, 0, s * 0.18]);
      mesh(sph(0.15), skin, A, [s * 0.17, -0.66, 0.03], [0.9, 1, 0.8]);
      arms.push(A);
    }
    const head = group(body, [0, 2.55, 0]);
    const lid = M("#c07b58", 0.55);
    mesh(sph(0.9), skin, head, [0, 0.05, 0], [1.02, 0.97, 0.92]);
    mesh(sph(0.74), skin, head, [0, -0.25, 0.16], [1.08, 0.86, 0.95]);      // chubby cheeks
    for (const s of [-1, 1]) mesh(sph(0.18), skin, head, [s * 0.9, 0.0, -0.02], [0.55, 1, 0.85]);
    for (const s of [-1, 1]) mesh(sph(0.16), M("#ff8a80", 0.6, { transparent: true, opacity: 0.35 }), head, [s * 0.5, -0.24, 0.66], [1, 0.62, 0.3], [0, s * 0.6, 0]);
    mesh(sph(0.075), M("#b8744f", 0.5), head, [0, -0.13, 0.93], [1.15, 0.9, 0.9]);
    // hair (from mo-expressions.jpg): tall fluffy top, fringe across the upper forehead, sides over the ear tops,
    // and a tuft sticking up at the top right
    mesh(new T.SphereGeometry(0.97, 48, 32, 0, Math.PI * 2, 0, 1.45), hair, head, [0, 0.16, -0.1], [1.04, 1.02, 1.0], [-0.85, 0, 0]);
    mesh(sph(0.95), hair, head, [0, 0.7, -0.12], [1.06, 0.7, 1.0]);
    mesh(sph(0.78), hair, head, [0.04, 0.8, 0.3], [1.0, 0.36, 0.62], [0.35, 0, -0.06]);
    for (const [x, y, z, r] of [[-0.86, 0.32, -0.02, 0.27], [0.86, 0.32, -0.02, 0.27], [-0.5, 0.86, 0.1, 0.38], [0.45, 0.9, 0.1, 0.38], [0, 0.5, -0.75, 0.45]])
      mesh(sph(r), hair, head, [x, y, z], [1, 0.8, 1]);
    mesh(sph(0.3), hair, head, [0.32, 1.22, 0.05], [0.55, 1.0, 0.55], [0.1, 0, -0.55]);
    mesh(sph(0.24), hair, head, [0.08, 1.2, 0.12], [0.5, 0.85, 0.5], [0.2, 0, -0.25]);
    for (const s of [-1, 1]) mesh(new T.TorusGeometry(0.15, 0.025, 8, 20, Math.PI * 0.8), M("#3a1d10", 0.5), head, [s * 0.36, 0.38, 0.8], [1.0, 0.75, 1], [-0.3, s * 0.35, s * 0.06]);
    const eyes = [eye(head, -0.36, 0.08, 0.72, 0.22, lid), eye(head, 0.36, 0.08, 0.72, 0.22, lid)];
    for (const e of eyes) e.rotation.y = e.position.x * 0.8;
    const mouth = mouthSet(head, [0, -0.38, 0.925], 0.18, -0.32);
    return { root, body, head, arms, legs, eyes, mouth, setMouth: mouth.set, setEyes: (n) => setEyes(eyes, n), height: 3.5 };
  }

  // ------------------------------------------------------------------ Grandpa (Old MacDonald)
  function buildGrandpa() {
    const root = new T.Group();
    const body = group(root);
    const skin = M("#c98663", 0.55), denim = M("#3c62a8", 0.8), boot = M("#7a4a26", 0.6), white = M("#f8f6f2", 0.85),
      straw = M("#e1bf6e", 0.8), band = M("#e0393a", 0.5), gold = M("#f4c430", 0.35);
    const check = canvasTex(64, 64, (x, w, h) => {
      x.fillStyle = "#ffffff"; x.fillRect(0, 0, w, h);
      x.fillStyle = "rgba(220,40,40,0.55)"; x.fillRect(0, 0, w / 2, h); x.fillRect(0, 0, w, h / 2);
      x.fillStyle = "#d42a2a"; x.fillRect(0, 0, w / 2, h / 2);
    }, [6, 6]);
    const shirt = new T.MeshStandardMaterial({ map: check, roughness: 0.75 });
    const legs = [];
    for (const s of [-1, 1]) {
      const L = group(body, [s * 0.36, 1.35, 0]);
      mesh(cap(0.27, 0.5), denim, L, [0, -0.45, 0]);
      mesh(new T.CylinderGeometry(0.31, 0.3, 0.5, 24), boot, L, [0, -0.95, 0]);
      mesh(sph(0.33), boot, L, [0, -1.18, 0.12], [1, 0.5, 1.4]);
      legs.push(L);
    }
    mesh(sph(1.0), shirt, body, [0, 2.45, 0], [1.0, 1.02, 0.82]);
    mesh(sph(1.02), denim, body, [0, 1.95, 0.0], [1.0, 0.85, 0.84]);
    mesh(new T.BoxGeometry(1.1, 0.75, 0.2), denim, body, [0, 2.55, 0.72], [1, 1, 1], [-0.12, 0, 0]);
    mesh(new T.BoxGeometry(0.45, 0.3, 0.05), denim, body, [0, 2.5, 0.84], [1, 1, 1], [-0.12, 0, 0]);
    for (const s of [-1, 1]) {
      mesh(new T.BoxGeometry(0.18, 1.0, 0.08), denim, body, [s * 0.42, 3.05, 0.55], [1, 1, 1], [-0.45, 0, 0]);
      mesh(new T.CylinderGeometry(0.075, 0.075, 0.05, 20), gold, body, [s * 0.42, 2.85, 0.82], [1, 1, 1], [Math.PI / 2 - 0.12, 0, 0]);
    }
    const arms = [];
    for (const s of [-1, 1]) {
      const A = group(body, [s * 0.92, 3.0, 0]);
      mesh(sph(0.32), shirt, A, [0, -0.08, 0]);
      mesh(cap(0.22, 0.45), shirt, A, [s * 0.1, -0.42, 0], [1, 1, 1], [0, 0, s * 0.15]);
      mesh(cap(0.17, 0.35), skin, A, [s * 0.18, -0.85, 0.02], [1, 1, 1], [0, 0, s * 0.12]);
      mesh(sph(0.21), skin, A, [s * 0.24, -1.15, 0.04]);
      arms.push(A);
    }
    const head = group(body, [0, 4.0, 0]);
    const lid = M("#bf7a57", 0.55);
    mesh(sph(0.95), skin, head, [0, 0, 0], [1, 0.98, 0.92]);
    for (const s of [-1, 1]) mesh(sph(0.2), skin, head, [s * 0.95, 0.02, -0.05], [0.55, 1, 0.85]);
    // beard and moustache
    mesh(sph(0.95), white, head, [0, -0.62, 0.32], [1.02, 0.92, 0.72]);
    for (const [x, y, z, r] of [[-0.55, -0.4, 0.4, 0.42], [0.55, -0.4, 0.4, 0.42], [0, -1.15, 0.45, 0.5], [-0.35, -1.0, 0.55, 0.4], [0.35, -1.0, 0.55, 0.4]])
      mesh(sph(r), white, head, [x, y, z]);
    for (const s of [-1, 1]) mesh(sph(0.3), white, head, [s * 0.27, -0.28, 0.86], [1.25, 0.65, 0.7], [0, 0, s * -0.25]);
    for (const s of [-1, 1]) mesh(sph(0.4), white, head, [s * 0.78, 0.35, -0.2], [0.5, 0.8, 0.9]);     // white hair at the sides
    mesh(sph(0.22), M("#e2706a", 0.45), head, [0, -0.05, 0.93], [1.05, 0.95, 0.95]);
    for (const s of [-1, 1]) mesh(sph(0.15), M("#ff8a80", 0.6, { transparent: true, opacity: 0.4 }), head, [s * 0.5, -0.12, 0.72], [1, 0.6, 0.35]);
    const eyes = [eye(head, -0.32, 0.22, 0.8, 0.17, lid), eye(head, 0.32, 0.22, 0.8, 0.17, lid)];
    for (const e of eyes) e.rotation.y = e.position.x * 0.8;
    for (const s of [-1, 1]) mesh(sph(0.2), white, head, [s * 0.34, 0.48, 0.82], [1.3, 0.5, 0.5], [0, 0, s * -0.25]);
    const mouth = mouthSet(head, [0, -0.47, 1.02], 0.17, -0.1, "#7c1d24", false);
    // straw hat
    const hat = group(head, [0, 0.62, -0.05], [-0.12, 0, 0]);
    mesh(new T.CylinderGeometry(1.55, 1.55, 0.07, 48), straw, hat, [0, 0, 0]);
    mesh(new T.TorusGeometry(1.55, 0.06, 10, 64), straw, hat, [0, 0.02, 0], [1, 1, 1], [Math.PI / 2, 0, 0]);
    mesh(new T.CylinderGeometry(0.7, 0.8, 0.55, 48), straw, hat, [0, 0.3, 0]);
    mesh(sph(0.7), straw, hat, [0, 0.55, 0], [1, 0.4, 1]);
    mesh(new T.CylinderGeometry(0.815, 0.83, 0.2, 48), band, hat, [0, 0.15, 0]);
    return { root, body, head, arms, legs, eyes, mouth, setMouth: mouth.set, setEyes: (n) => setEyes(eyes, n), height: 5.3 };
  }

  window.Chars = { buildMo, buildGrandpa, M, mesh, group, sph, cap, eye, mouthSet, setEyes, canvasTex };
})();
