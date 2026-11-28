// The 3D Old MacDonald video. Needs THREE, Chars, Animals and window.CUES (timings written by oldmac3d.py).
// Everything is a pure function of time t (draw(t)), so any frame can be rendered in any order.
(function () {
  const T = THREE, C = window.CUES, { M, mesh, group, sph, cap } = window.Chars;
  T.ColorManagement.legacyMode = false;
  const renderer = new T.WebGLRenderer({ canvas: document.getElementById("c"), antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(1920, 1080, false);
  renderer.outputEncoding = T.sRGBEncoding; renderer.toneMapping = T.NoToneMapping;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap;
  const scene = new T.Scene();
  const camera = new T.PerspectiveCamera(34, 1920 / 1080, 0.1, 900);
  const skyMat = new T.ShaderMaterial({
    side: T.BackSide, depthWrite: false,
    uniforms: { top: { value: new T.Color("#4fb3ff") }, bottom: { value: new T.Color("#d8f3ff") } },
    vertexShader: "varying vec3 p; void main(){ p = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }",
    fragmentShader: "uniform vec3 top; uniform vec3 bottom; varying vec3 p; void main(){ float h = clamp(normalize(p).y*1.8+0.12,0.0,1.0); gl_FragColor = vec4(mix(bottom, top, h),1.0); }"
  });
  const sky = new T.Mesh(new T.SphereGeometry(600, 32, 16), skyMat); scene.add(sky);
  scene.add(new T.HemisphereLight("#eaf6ff", "#5fae45", 0.55));
  const sun = new T.DirectionalLight("#fff6e6", 1.15);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 90 });
  sun.shadow.radius = 5; sun.shadow.bias = -0.0006;
  scene.add(sun); scene.add(sun.target);
  const rim = new T.DirectionalLight("#ffe9f5", 0.45); rim.position.set(30, 20, -40); scene.add(rim);

  const rnd = (() => { let s = 11; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
  const SPACING = 44;
  const LOC = [0, 1, 2, 3, 4, 5].map(v => new T.Vector3(v * SPACING, 0, 0));
  const FINAL = LOC[0];

  // ------------------------------------------------------------------ world
  const ground = mesh(new T.PlaneGeometry(700, 400), M("#5cc23f", 0.95), scene, [110, 0, 0], [1, 1, 1], [-Math.PI / 2, 0, 0]);
  ground.castShadow = false;
  for (let i = 0; i < 26; i++) {      // distant hills all around
    const a = i / 26 * Math.PI * 2, r = 150 + rnd() * 40, s = 30 + rnd() * 25;
    const h = mesh(sph(1, 32, 16), M(["#9fe07a", "#8fd86a", "#a6e383", "#94db70"][i % 4], 0.95), scene,
      [110 + Math.cos(a) * r * 1.4, -s * 0.5, Math.sin(a) * r], [s * 1.5, s, s]);
    h.castShadow = false;
  }
  function tree(x, z, s) {
    const g = group(scene, [x, 0, z]);
    mesh(cap(0.35 * s, 2.2 * s), M("#a8703f", 0.8), g, [0, 1.3 * s, 0]);
    for (const [dx, dy, dz, r] of [[0, 3.4, 0, 1.6], [-1.1, 2.9, 0.3, 1.15], [1.1, 3.0, 0.2, 1.2], [0, 4.4, -0.2, 1.1]])
      mesh(sph(r * s, 24, 16), M("#4cbf4a", 0.75), g, [dx * s, dy * s, dz * s]);
    for (const [dx, dy, dz] of [[-0.8, 3.6, 1.2], [0.9, 3.2, 1.1], [0.2, 4.5, 0.9]]) mesh(sph(0.22 * s, 12, 8), M("#ff4b4b", 0.35), g, [dx * s, dy * s, dz * s]);
  }
  function fence(x0, x1, z, col = "#fff6e8") {
    for (let x = x0; x <= x1; x += 1.1) mesh(new T.BoxGeometry(0.22, 1.2, 0.16), M(col, 0.5), scene, [x, 0.6, z]);
    for (const y of [0.45, 0.95]) mesh(new T.BoxGeometry(x1 - x0, 0.14, 0.1), M(col, 0.5), scene, [(x0 + x1) / 2, y, z + 0.05]);
  }
  function flowers(cx, cz, n, rx, rz, avoid = 0) {
    for (let i = 0; i < n; i++) {
      const x = cx + (rnd() - 0.5) * rx * 2, z = cz + (rnd() - 0.5) * rz * 2;
      if (avoid && Math.hypot(x - cx, (z - cz) * 1.3) < avoid) continue;
      const c = ["#ff6b8b", "#ffd23f", "#ffffff", "#b38bff", "#ff9f43"][Math.floor(rnd() * 5)];
      const f = group(scene, [x, 0.02, z]);
      mesh(new T.CylinderGeometry(0.025, 0.025, 0.3, 6), M("#3c9a2e", 0.8), f, [0, 0.15, 0]);
      for (let p = 0; p < 5; p++) mesh(sph(0.09, 10, 6), M(c, 0.45), f, [Math.cos(p * 1.2566) * 0.11, 0.32, Math.sin(p * 1.2566) * 0.11], [1, 0.45, 1]);
      mesh(sph(0.07, 10, 6), M("#ffb300", 0.4), f, [0, 0.34, 0], [1, 0.6, 1]);
    }
    for (let i = 0; i < n * 1.4; i++) {
      const x = cx + (rnd() - 0.5) * rx * 2, z = cz + (rnd() - 0.5) * rz * 2;
      if (avoid && Math.hypot(x - cx, (z - cz) * 1.3) < avoid) continue;
      const t = mesh(new T.ConeGeometry(0.06, 0.35, 5), M("#3fa52f", 0.9), scene, [x, 0.15, z], [1, 1, 1], [(rnd() - 0.5) * 0.5, 0, (rnd() - 0.5) * 0.5]);
      t.castShadow = false;
    }
  }
  function barn(x, z) {
    const b = group(scene, [x, 0, z]);
    mesh(new T.BoxGeometry(6, 4.2, 5), M("#e8473c", 0.6), b, [0, 2.1, 0]);
    mesh(new T.CylinderGeometry(0.01, 4.1, 2.6, 4, 1), M("#8c2f25", 0.6), b, [0, 5.5, 0], [1.05, 1, 0.88], [0, Math.PI / 4, 0]);
    mesh(new T.BoxGeometry(2.6, 3.0, 0.12), M("#9e2d24", 0.6), b, [0, 1.5, 2.52]);
    for (const r of [0.86, -0.86]) mesh(new T.BoxGeometry(3.8, 0.18, 0.08), M("#fff4e2", 0.5), b, [0, 1.5, 2.6], [1, 1, 1], [0, 0, r]);
    mesh(new T.BoxGeometry(1.2, 1.0, 0.1), M("#7a2a22", 0.6), b, [0, 3.6, 2.52]);
  }
  function stable(x, z) {
    const b = group(scene, [x, 0, z]);
    mesh(new T.BoxGeometry(5.5, 3.6, 4.5), M("#b9783f", 0.75), b, [0, 1.8, 0]);
    mesh(new T.CylinderGeometry(0.01, 3.9, 2.0, 4, 1), M("#7a3d1c", 0.7), b, [0, 4.6, 0], [1.05, 1, 0.85], [0, Math.PI / 4, 0]);
    mesh(new T.BoxGeometry(2.0, 2.6, 0.12), M("#5a3518", 0.6), b, [0, 1.3, 2.27]);
    mesh(new T.BoxGeometry(2.0, 0.14, 0.14), M("#d9a46a", 0.6), b, [0, 1.6, 2.36]);
  }
  function coop(x, z) {
    const b = group(scene, [x, 0, z]);
    for (const [dx, dz] of [[-1.3, -0.9], [1.3, -0.9], [-1.3, 0.9], [1.3, 0.9]]) mesh(new T.BoxGeometry(0.2, 1.3, 0.2), M("#a8703f", 0.7), b, [dx, 0.65, dz]);
    mesh(new T.BoxGeometry(3.0, 1.8, 2.2), M("#ffcf6b", 0.6), b, [0, 2.2, 0]);
    mesh(new T.CylinderGeometry(0.01, 2.4, 1.3, 4, 1), M("#e0473c", 0.6), b, [0, 3.75, 0], [1.05, 1, 0.8], [0, Math.PI / 4, 0]);
    mesh(new T.CylinderGeometry(0.45, 0.45, 0.1, 24), M("#6b3d18", 0.7), b, [0, 2.1, 1.12], [1, 1, 1], [Math.PI / 2, 0, 0]);
    mesh(new T.BoxGeometry(0.8, 0.08, 2.4), M("#a8703f", 0.7), b, [0, 0.65, 1.9], [1, 1, 1], [-0.45, 0, 0]);
  }
  function hay(x, z, s = 1) { mesh(new T.CylinderGeometry(0.8 * s, 0.8 * s, 1.1 * s, 24), M("#f2cf5b", 0.9), scene, [x, 0.8 * s, z], [1, 1, 1], [0, 0, Math.PI / 2]); }

  // place each animal's home
  barn(LOC[0].x - 7, -6); hay(LOC[0].x + 6, -4); fence(LOC[0].x - 3, LOC[0].x + 12, -4.5);
  const mud = mesh(new T.CircleGeometry(3.4, 48), M("#7a4f2c", 0.9), scene, [LOC[1].x + 2.2, 0.03, 0.3], [1, 0.7, 1], [-Math.PI / 2, 0, 0]);
  mud.castShadow = false;
  fence(LOC[1].x - 8, LOC[1].x + 10, -4.5, "#d9a46a"); hay(LOC[1].x - 6, -3, 0.8);
  const pondRing = mesh(new T.CylinderGeometry(4.6, 4.6, 0.25, 64), M("#8a7a6a", 0.9), scene, [LOC[2].x + 2.4, 0.0, 0.2], [1, 1, 0.65]);
  const water = mesh(new T.CircleGeometry(4.4, 64), M("#3fa6e0", 0.15, { metalness: 0.1 }), scene, [LOC[2].x + 2.4, 0.14, 0.2], [1, 0.65, 1], [-Math.PI / 2, 0, 0]);
  water.castShadow = false;
  for (const [dx, dz] of [[-1.5, 1.2], [3.6, -0.6], [1.2, -1.6]]) mesh(new T.CylinderGeometry(0.45, 0.45, 0.04, 20), M("#59c24a", 0.6), scene, [LOC[2].x + 2.4 + dx, 0.17, 0.2 + dz]);
  for (const dx of [-4.8, -4.5, 7.3, 7.6]) { mesh(new T.CylinderGeometry(0.04, 0.04, 2.2, 6), M("#3c8a2e", 0.8), scene, [LOC[2].x + 2.4 + dx, 1.1, -0.8]); mesh(cap(0.12, 0.4), M("#8a5a30", 0.7), scene, [LOC[2].x + 2.4 + dx, 2.2, -0.8]); }
  const hill = mesh(sph(1, 48, 24), M("#7fd65e", 0.95), scene, [LOC[3].x + 1, -6, -9], [16, 9, 9]);
  hill.castShadow = false;
  for (let i = 0; i < 12; i++) mesh(sph(0.6, 16, 10), M("#c9c2b8", 0.9), scene, [LOC[3].x - 8 + i * 1.3, 0.4, -4.5], [1, 0.75, 0.8]);
  stable(LOC[4].x - 6, -6); hay(LOC[4].x + 6, -4.2); hay(LOC[4].x + 7.5, -3, 0.7); fence(LOC[4].x - 2, LOC[4].x + 12, -4.8, "#d9a46a");
  coop(LOC[5].x - 6, -5);
  const nest = mesh(new T.TorusGeometry(0.55, 0.25, 12, 24), M("#f2cf5b", 0.9), scene, [LOC[5].x + 4.5, 0.2, -1.5], [1, 1, 0.6], [Math.PI / 2, 0, 0]);
  for (const dx of [-0.25, 0, 0.25]) mesh(sph(0.2, 16, 12), M("#fff7ea", 0.5), scene, [LOC[5].x + 4.5 + dx, 0.35, -1.5], [1, 1.3, 1]);
  fence(LOC[5].x - 2, LOC[5].x + 12, -4.5);
  for (let v = 0; v < 6; v++) {
    const L = LOC[v];
    tree(L.x - 14, -12, 1.4); tree(L.x + 14, -11, 1.2); tree(L.x + 20, -16, 1.5);
    flowers(L.x + 1, 3, 70, 13, 6, v === 1 ? 4.2 : v === 2 ? 5.4 : 0);
  }

  // ------------------------------------------------------------------ cast
  const grandpa = Chars.buildGrandpa(), mo = Chars.buildMo(), dog = Animals.biscuit();
  for (const c of [grandpa, mo, dog]) scene.add(c.root);
  const KINDS = ["cow", "pig", "duck", "sheep", "horse", "hen"];
  const animals = KINDS.map(k => { const a = Animals[k](); scene.add(a.root); return a; });
  const minis = KINDS.map(k => [0, 1, 2, 3, 4, 5, 6, 7].map(() => { const a = Animals[k](); a.root.visible = false; scene.add(a.root); return a; }));
  const MINI_POS = [[-1.5, 2.2], [5.6, 1.8], [-3.5, 3.4], [6.8, -1.2], [0.5, -2.4], [3.4, -2.8], [-2.6, -1.0], [8.0, 2.6]];

  // ------------------------------------------------------------------ helpers
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
  const lerp = (a, b, k) => a + (b - a) * k;
  const beatPh = t => (t - C.b0) / C.beat;
  const bounce = (t, amp) => Math.abs(Math.sin(Math.PI * beatPh(t))) * amp;
  const inWord = (words, t) => words.some(w => t >= w.s && t < Math.max(w.e, w.s + 0.16));
  function blinkAt(t, seed) { const p = (t + seed * 1.37) % 3.3; return p < 0.12; }
  function face(c, t, mouth, seed, happy = false) {
    c.setEyes(blinkAt(t, seed) ? "closed" : happy ? "happy" : "open");
    c.setMouth(mouth);
  }
  function walkLegs(c, phase, amp) { c.legs.forEach((L, i) => L.rotation.x = Math.sin(phase + (i % 2 === (i < 2 ? 0 : 1) ? 0 : Math.PI)) * amp); }
  function restLegs(c) { c.legs.forEach(L => L.rotation.x = 0); }
  function place(c, loc, x, z, ry, y = 0) { c.root.position.set(loc.x + x, y, loc.z + z); c.root.rotation.set(0, ry, 0); }
  function lookAt(c, x, z) { c.root.rotation.y = Math.atan2(x - c.root.position.x, z - c.root.position.z); }

  // which verse/phase are we in?
  function verseAt(t) {
    let v = -1;
    for (let i = 0; i < 6; i++) if (t >= C.verses[i].L[0].start - 0.6) v = i;
    return v;
  }
  // ------------------------------------------------------------------ the frame
  function draw(t) {
    const v = verseAt(t);
    const outro = t >= C.last + 0.3;
    const V = v >= 0 ? C.verses[v] : null;
    const loc = outro ? FINAL : LOC[Math.max(v, 0)];
    // sun follows the action so shadows are always sharp near the camera
    sun.position.set(loc.x - 12, 24, 16); sun.target.position.set(loc.x + 1, 0, 0);

    // --- the family (Grandpa, Mo, Biscuit)
    const L0 = V ? V.L[0] : null, L4 = V ? V.L[4] : null;
    const singing = V && (inWord(L0.words, t) || inWord(L4.words, t));
    const eieio = V && [V.L[0], V.L[1], V.L[4]].some(l => inWord(l.words.slice(-5), t));
    place(grandpa, loc, -2.6, 0.4, 0.45);
    place(mo, loc, -0.9, 1.6, 0.3);
    place(dog, loc, -4.3, 1.9, 0.5);
    if (v < 0) {          // intro: Mo and Biscuit run in, Grandpa waves
      const k = smooth((t - 1.0) / 3.0);
      place(mo, loc, lerp(-9, -0.9, k), 1.6, k < 1 ? Math.PI / 2 : 0.3);
      place(dog, loc, lerp(-12, -4.3, k), 1.9, k < 1 ? Math.PI / 2 : 0.5);
      if (k < 1) { walkLegs(mo, t * 14, 0.7); walkLegs(dog, t * 16, 0.7); mo.body.position.y = Math.abs(Math.sin(t * 14)) * 0.12; dog.body.position.y = Math.abs(Math.sin(t * 16)) * 0.1; }
      else { restLegs(mo); restLegs(dog); }
    } else { restLegs(mo); restLegs(dog); restLegs(grandpa); }
    const dance = outro || (V && t > L4.start - 0.2) || eieio;
    for (const [c, amp, seed] of [[grandpa, 0.08, 1], [mo, 0.16, 2], [dog, 0.14, 3]]) {
      if (!(v < 0 && t < 4.0 && c !== grandpa)) c.body.position.y = bounce(t, dance ? amp * 1.6 : amp * 0.6);
      c.body.rotation.z = Math.sin(Math.PI * beatPh(t)) * (dance ? 0.07 : 0.03);
    }
    // Grandpa: sings, waves on line 0, arms up on E-I-E-I-O
    face(grandpa, t, singing ? (Math.floor(t * 6) % 2 ? "smile" : "o") : "smile", 1);
    const gw = V && t >= L0.start && t < L0.end;
    grandpa.arms[1].rotation.z = eieio || outro ? 2.5 + Math.sin(t * 8) * 0.2 : gw ? 2.2 + Math.sin(t * 9) * 0.35 : 0.1;
    grandpa.arms[0].rotation.z = eieio || outro ? -2.5 - Math.sin(t * 8) * 0.2 : -0.1;
    grandpa.head.rotation.z = Math.sin(Math.PI * beatPh(t)) * 0.06;
    // Mo: sings E-I-E-I-O, copies the animal's sound, claps
    const sounding = V && inWord(V.sounds, t);
    face(mo, t, eieio || sounding ? "o" : dance ? "laugh" : "smile", 2, dance && !eieio && Math.floor(beatPh(t)) % 4 === 1);
    const clap = V && t > V.L[1].start && t < V.L[2].start;
    if (eieio || outro) { mo.arms[0].rotation.z = -2.6 + Math.sin(t * 9) * 0.25; mo.arms[1].rotation.z = 2.6 - Math.sin(t * 9) * 0.25; mo.arms[0].rotation.x = mo.arms[1].rotation.x = 0; }
    else if (clap) { const c = Math.abs(Math.sin(t * 7)); mo.arms[0].rotation.set(-1.2, 0, -0.5 + c * 0.45); mo.arms[1].rotation.set(-1.2, 0, 0.5 - c * 0.45); }
    else if (sounding) { mo.arms[0].rotation.set(0, 0, -1.6); mo.arms[1].rotation.set(0, 0, 1.6); }
    else { mo.arms[0].rotation.set(0, 0, -0.15); mo.arms[1].rotation.set(0, 0, 0.15); }
    mo.head.rotation.z = Math.sin(Math.PI * beatPh(t)) * 0.08;
    face(dog, t, eieio ? "o" : "smile", 3);
    dog.tail.rotation.z = Math.sin(t * 14) * 0.5;
    dog.ears.forEach((e, i) => e.rotation.x = Math.sin(t * 6 + i) * 0.15);

    // --- the animals
    animals.forEach((a, i) => {
      a.root.visible = false;
      if (v < i && !outro) return;
      const A = C.verses[i];
      const mine = v === i && !outro;
      a.root.visible = true;
      if (a.tail) a.tail.rotation.y = Math.sin(t * 5 + i) * 0.4;
      if (mine) {
        // entrance during line 1: walk in from the right, land on its name
        const t0 = A.L[1].start - 0.7, t1 = A.name, k = smooth((t - t0) / Math.max(0.8, t1 - t0));
        const home = [2.6, 0.2];
        if (t < t0) { a.root.visible = false; return; }
        const y = i === 1 ? -0.12 : i === 2 ? -0.75 : 0;
        place(a, loc, lerp(10, home[0], k), home[1], k < 1 ? -Math.PI / 2 : -0.55, y);
        if (i === 3 && k < 1) a.root.position.y = Math.abs(Math.sin(k * Math.PI * 4)) * 1.2;   // sheep bounces in
        if (k < 1 && i !== 2) { walkLegs(a, t * (i === 4 ? 18 : 12), i === 4 ? 0.9 : 0.6); a.body.position.y = Math.abs(Math.sin(t * 12)) * 0.08; }
        else { restLegs(a); a.body.position.y = i === 2 ? Math.sin(t * 3) * 0.05 : bounce(t, 0.08); }
        if (i === 2 && a.wings) a.wings.forEach((w, j) => w.rotation.z = (j ? -1 : 1) * (k < 1 ? Math.abs(Math.sin(t * 14)) * 0.8 : 0));
        // the sound (lines 2-3)
        const snd = inWord(A.sounds, t);
        a.head.rotation.x = snd ? -0.28 : 0;
        a.setMouth(snd ? (i <= 1 ? "o" : "smile") : "closed");
        a.setEyes(blinkAt(t, 4 + i) ? "closed" : snd ? "happy" : "open");
        if (a.ears) a.ears.forEach((e, j) => e.rotation.x = snd ? Math.sin(t * 20) * 0.3 : 0);
        if (a.wings && snd) a.wings.forEach((w, j) => w.rotation.z = (j ? -1 : 1) * Math.abs(Math.sin(t * 16)) * 0.9);
        if (i === 4 && snd) a.body.rotation.x = -0.2;    // horse rears a little
        else a.body.rotation.x = 0;
        // line 4: walks to the group at the back
        if (t > A.L[4].start) {
          const k2 = smooth((t - A.L[4].start) / 1.4);
          const back = backSpot(i);
          place(a, loc, lerp(home[0], back[0], k2), lerp(home[1], back[1], k2), k2 < 1 ? Math.atan2(back[0] - home[0], back[1] - home[1]) : 0.1, i === 2 ? lerp(-0.75, 0, k2) : 0);
          if (k2 < 1) walkLegs(a, t * 12, 0.6); else restLegs(a);
        }
      } else {
        // part of the group, standing at the back; everyone sings E-I-E-I-O and dances at the end of a verse
        const back = backSpot(i);
        place(a, loc, back[0], back[1], 0.15 + (i % 2) * 0.1);
        if (v === 2 && !outro) { /* keep the pond clear */ }
        restLegs(a);
        a.body.position.y = bounce(t + i * 0.1, dance ? 0.2 : 0.06);
        a.body.rotation.x = 0;
        a.head.rotation.x = 0;
        a.setMouth(eieio ? "o" : "closed");
        a.setEyes(blinkAt(t, 4 + i) ? "closed" : "open");
        if (outro) a.root.position.y = Math.abs(Math.sin(Math.PI * (beatPh(t) + i * 0.25))) * 0.9;
      }
    });
    // --- here, there, everywhere: little copies pop up around the animal
    minis.forEach((set, i) => set.forEach((m, j) => {
      m.root.visible = false;
      if (v !== i || outro) return;
      const A = C.verses[i], tp = A.pops[j];
      if (tp === undefined || t < tp || t > A.L[4].start + 0.3) return;
      const k = clamp((t - tp) / 0.35), out = clamp((t - A.L[4].start) / 0.3);
      const s = 0.42 * (k < 1 ? Math.sin(k * Math.PI * 0.5) * 1.15 : 1) * (1 - out);
      m.root.visible = s > 0.01;
      const [x, z] = MINI_POS[j];
      place(m, loc, x, z, Math.atan2(-x, 12 - z), i === 2 ? -0.3 : 0);
      m.root.scale.setScalar(Math.max(0.001, s));
      m.body.position.y = bounce(t + j * 0.13, 0.15);
      const snd = inWord(A.sounds, t);
      m.setMouth(snd ? (i <= 1 ? "o" : "smile") : "closed");
      m.setEyes("open");
    }));

    // --- camera: one shot per phrase
    shot(t, v, V, loc, outro);
    renderer.render(scene, camera);
  }
  function backSpot(i) { return [-5.2 + i * 1.9, -2.6 - (i % 2) * 0.6]; }

  const SHOTS = {
    wide: { p: [1.2, 4.2, 15.5], q: [0.6, 4.0, 13.8], tgt: [0.4, 2.0, 0] },
    family: { p: [-1.8, 3.9, 12.0], q: [-2.2, 3.8, 10.8], tgt: [-2.2, 3.0, 0.8] },
    entrance: { p: [4.6, 3.0, 11.5], q: [4.2, 2.8, 10.4], tgt: [3.6, 1.9, 0.2] },
    closeAnimal: { p: [4.4, 2.7, 6.8], q: [4.0, 2.6, 6.0], tgt: [2.6, 2.1, 0.2] },
    closeMo: { p: [0.4, 3.0, 8.6], q: [0.1, 2.9, 7.8], tgt: [-0.8, 2.3, 1.4] },
    everywhere: { p: [2.0, 5.5, 17.0], q: [2.4, 5.0, 15.5], tgt: [2.2, 1.6, 0] },
  };
  function shot(t, v, V, loc, outro) {
    let s, t0, t1;
    if (outro) { s = SHOTS.wide; t0 = C.last + 0.3; t1 = C.D; }
    else if (v < 0) {          // intro: sweep down from the sky
      const k = smooth(t / Math.max(1, C.verses[0].L[0].start - 0.6));
      const p = [lerp(-10, 1.2, k), lerp(22, 4.2, k), lerp(34, 15.5, k)];
      camera.position.set(loc.x + p[0], p[1], loc.z + p[2]); camera.lookAt(loc.x + 0.4, lerp(6, 2.0, k), 0);
      return;
    } else {
      const L = V.L;
      const cuts = [[L[0].start - 0.6, "family"], [L[1].start - 0.4, "entrance"], [L[2].start - 0.2, "closeAnimal"],
        [(L[2].start + L[2].end) / 2, "closeMo"], [L[3].start - 0.1, "everywhere"], [L[4].start - 0.2, "wide"]];
      const end = v < 5 ? C.verses[v + 1].L[0].start - 0.6 : C.last + 0.3;
      for (let i = 0; i < cuts.length; i++) if (t >= cuts[i][0]) { s = SHOTS[cuts[i][1]]; t0 = cuts[i][0]; t1 = i + 1 < cuts.length ? cuts[i + 1][0] : end; }
    }
    const k = smooth((t - t0) / Math.max(0.5, t1 - t0));
    const p = s.p.map((x, i) => lerp(x, s.q[i], k));
    camera.position.set(loc.x + p[0], p[1], loc.z + p[2]);
    camera.lookAt(loc.x + s.tgt[0], s.tgt[1], loc.z + s.tgt[2]);
  }

  // drive from the Hyperframes/GSAP timeline
  let cur = 0;
  window.Scene3D = { draw, clock: { t: function (val) { if (val === undefined) return cur; cur = val; draw(val); } } };
})();
