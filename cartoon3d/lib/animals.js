// Biscuit the puppy and the six farm animals, matched to character/farm-animals.jpg and biscuit-turnaround.jpg.
// Same conventions as characters.js: feet at y = 0, facing +z, returns { root, body, head, legs, tail, ears, setMouth, setEyes }.
(function () {
  const T = THREE;
  const { M, mesh, group, sph, cap, eye, mouthSet, setEyes } = window.Chars;

  function legs4(body, mat, hoofMat, xs, zs, top, len, r, hoofH = 0.16) {
    const out = [];
    for (const x of xs) for (const z of zs) {
      const L = group(body, [x, top, z]);
      mesh(cap(r, len - r * 2), mat, L, [0, -len / 2, 0]);
      if (hoofMat) mesh(new T.CylinderGeometry(r * 1.05, r * 1.12, hoofH, 24), hoofMat, L, [0, -len + hoofH / 2 - 0.02, 0]);
      out.push(L);
    }
    return out;    // order: [front-left, front-right, back-left, back-right] when xs = [front, back]... used as alternating pairs
  }
  function faceEyes(head, x, y, z, r, lid, spread = 0.9) {
    const e = [eye(head, -x, y, z, r, lid), eye(head, x, y, z, r, lid)];
    for (const k of e) k.rotation.y = k.position.x * spread;
    return e;
  }
  function blush(head, x, y, z, r = 0.14) {
    for (const s of [-1, 1]) mesh(sph(r), M("#ff8a9a", 0.7, { transparent: true, opacity: 0.4 }), head, [s * x, y, z], [1, 0.6, 0.3], [0, s * 0.6, 0]);
  }
  // animals face +z; their bodies run along z (front at +z)
  function cow() {
    const root = new T.Group(), body = group(root);
    const white = M("#ffffff", 0.7), black = M("#1f1a1a", 0.7), pink = M("#ffb3c1", 0.6), hoof = M("#6b4a3a", 0.6), horn = M("#efe0b0", 0.5);
    const legs = legs4(body, white, hoof, [-0.42, 0.42], [0.5, -0.5], 0.85, 0.85, 0.2);
    mesh(cap(0.72, 0.8), white, body, [0, 1.25, 0], [1, 0.95, 1], [Math.PI / 2, 0, 0]);
    for (const [x, y, z, r] of [[0.55, 1.45, -0.2, 0.42], [-0.6, 1.2, 0.3, 0.38], [0.2, 1.9, -0.55, 0.36], [-0.3, 1.75, 0.65, 0.3]])
      mesh(sph(r), black, body, [x, y, z], [0.5, 0.9, 1]);
    const tail = group(body, [0, 1.6, -1.1]);
    mesh(cap(0.05, 0.7), white, tail, [0, -0.4, -0.12], [1, 1, 1], [0.3, 0, 0]);
    mesh(sph(0.12), black, tail, [0, -0.82, -0.25], [1, 1.5, 1]);
    const head = group(body, [0, 2.2, 0.75]);
    const lid = M("#f2f2f2", 0.7);
    mesh(sph(0.8), white, head, [0, 0.05, 0], [1, 0.95, 0.92]);
    for (const s of [-1, 1]) mesh(sph(0.62), black, head, [s * 0.42, 0.22, -0.05], [0.62, 0.85, 0.85]);      // the black patches
    const ears = [];
    for (const s of [-1, 1]) {
      const E = group(head, [s * 0.8, 0.3, -0.1], [0, 0, s * -0.5]);
      mesh(sph(0.3), black, E, [s * 0.18, 0, 0], [1, 0.45, 0.7]);
      mesh(sph(0.2), pink, E, [s * 0.2, 0, 0.08], [1, 0.4, 0.5]);
      ears.push(E);
      mesh(cap(0.07, 0.18), horn, head, [s * 0.32, 0.82, -0.1], [1, 1, 1], [0, 0, s * -0.35]);
    }
    const eyes = faceEyes(head, 0.32, 0.18, 0.62, 0.17, lid);
    mesh(sph(0.55), pink, head, [0, -0.38, 0.4], [1.05, 0.72, 0.85]);
    for (const s of [-1, 1]) mesh(sph(0.08), M("#c05a72", 0.6), head, [s * 0.2, -0.3, 0.86], [1, 1.3, 0.6]);
    const mouth = mouthSet(head, [0, -0.58, 0.83], 0.17, -0.5, "#7c1d24", false);
    mesh(new T.TorusGeometry(0.62, 0.06, 10, 40), M("#e0393a", 0.5), body, [0, 1.62, 0.55], [1, 1, 0.8], [Math.PI / 2 - 0.4, 0, 0]);
    mesh(sph(0.15), M("#f4c430", 0.3, { metalness: 0.4 }), body, [0, 1.4, 1.05], [1, 1.1, 1]);
    return { root, body, head, legs, tail, ears, eyes, setMouth: mouth.set, setEyes: (n) => setEyes(eyes, n), height: 3.0 };
  }
  function pig() {
    const root = new T.Group(), body = group(root);
    const pink = M("#f7a8bb", 0.6), dark = M("#e98aa2", 0.6);
    const legs = legs4(body, pink, dark, [-0.38, 0.38], [0.42, -0.42], 0.6, 0.6, 0.2, 0.12);
    mesh(sph(0.85), pink, body, [0, 1.15, 0], [1, 0.92, 1.12]);
    const tail = group(body, [0, 1.25, -0.95]);
    mesh(new T.TorusGeometry(0.12, 0.04, 8, 20, Math.PI * 1.6), pink, tail, [0, 0, -0.08], [1, 1, 1], [0, Math.PI / 2, 0]);
    const head = group(body, [0, 2.0, 0.55]);
    const lid = M("#f29ab0", 0.6);
    mesh(sph(0.78), pink, head, [0, 0, 0], [1.05, 0.95, 0.95]);
    const ears = [];
    for (const s of [-1, 1]) {
      const E = group(head, [s * 0.5, 0.62, 0.05], [0.5, 0, s * -0.3]);
      mesh(new T.ConeGeometry(0.22, 0.4, 24), pink, E, [0, 0.12, 0], [1, 1, 0.45]);
      ears.push(E);
    }
    const eyes = faceEyes(head, 0.3, 0.15, 0.64, 0.15, lid);
    blush(head, 0.48, -0.15, 0.62);
    mesh(new T.CylinderGeometry(0.28, 0.3, 0.22, 32), M("#f592ab", 0.55), head, [0, -0.18, 0.74], [1.1, 1, 0.85], [Math.PI / 2, 0, 0]);
    for (const s of [-1, 1]) mesh(sph(0.06), M("#b84f6b", 0.6), head, [s * 0.1, -0.17, 0.86], [1, 1.4, 0.5]);
    const mouth = mouthSet(head, [0, -0.5, 0.68], 0.16, -0.45, "#7c1d24", false);
    return { root, body, head, legs, tail, ears, eyes, setMouth: mouth.set, setEyes: (n) => setEyes(eyes, n), height: 2.8 };
  }
  function duck() {
    const root = new T.Group(), body = group(root);
    const yel = M("#ffd93b", 0.7), org = M("#ff9a1f", 0.5);
    const legs = [];
    for (const s of [-1, 1]) {
      const L = group(body, [s * 0.28, 0.55, 0]);
      mesh(cap(0.06, 0.35), org, L, [0, -0.3, 0]);
      mesh(sph(0.2), org, L, [0, -0.52, 0.12], [1, 0.25, 1.3]);
      legs.push(L);
    }
    mesh(sph(0.75), yel, body, [0, 1.15, 0], [1, 0.95, 1.05]);
    const tail = group(body, [0, 1.35, -0.75]);
    mesh(new T.ConeGeometry(0.2, 0.4, 16), yel, tail, [0, 0.1, -0.05], [1, 1, 0.6], [-0.9, 0, 0]);
    const wings = [];
    for (const s of [-1, 1]) {
      const Wg = group(body, [s * 0.68, 1.35, 0]);
      mesh(sph(0.32), yel, Wg, [s * 0.05, -0.2, 0], [0.4, 0.9, 0.8]);
      wings.push(Wg);
    }
    const head = group(body, [0, 2.2, 0.1]);
    const lid = M("#ffd02b", 0.7);
    mesh(sph(0.68), yel, head, [0, 0, 0]);
    for (const [x, z, r] of [[0, 0, 0.12], [0.08, -0.08, 0.1], [-0.08, -0.06, 0.1]]) mesh(sph(r), yel, head, [x, 0.7, z], [0.8, 1.6, 0.8]);
    const eyes = faceEyes(head, 0.26, 0.12, 0.57, 0.14, lid);
    const billTop = mesh(sph(0.3), org, head, [0, -0.15, 0.62], [1.1, 0.35, 0.95]);
    const jaw = group(head, [0, -0.2, 0.45]);
    mesh(sph(0.26), org, jaw, [0, -0.04, 0.15], [1.0, 0.3, 0.9]);
    const setMouth = (n) => { jaw.rotation.x = n === "closed" ? 0 : n === "o" ? 0.35 : 0.5; };
    return { root, body, head, legs, tail, wings, ears: [], eyes, setMouth, setEyes: (n) => setEyes(eyes, n), height: 2.9 };
  }
  function sheep() {
    const root = new T.Group(), body = group(root);
    const wool = M("#fbfaf6", 0.95), face = M("#55505a", 0.6), pinkIn = M("#d9a0ad", 0.6);
    const legs = legs4(body, face, null, [-0.35, 0.35], [0.4, -0.4], 0.7, 0.7, 0.13);
    const rnd = (() => { let s = 3; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
    mesh(sph(0.85), wool, body, [0, 1.2, 0], [1.05, 0.92, 1.1]);
    for (let i = 0; i < 26; i++) {
      const a = rnd() * Math.PI * 2, b = (rnd() - 0.3) * 1.5;
      mesh(sph(0.3 + rnd() * 0.08), wool, body, [Math.cos(a) * Math.cos(b) * 0.85, 1.2 + Math.sin(b) * 0.72, Math.sin(a) * Math.cos(b) * 0.92]);
    }
    const head = group(body, [0, 2.05, 0.6]);
    const lid = M("#4a4550", 0.6);
    mesh(sph(0.55), face, head, [0, -0.05, 0.1], [1.02, 0.95, 0.95]);
    for (let i = 0; i < 9; i++) { const a = (i / 9) * Math.PI * 2; mesh(sph(0.24), wool, head, [Math.cos(a) * 0.4, 0.5 + Math.sin(a) * 0.1, Math.sin(a) * 0.3 - 0.05]); }
    const ears = [];
    for (const s of [-1, 1]) {
      const E = group(head, [s * 0.55, 0.05, 0], [0, 0, s * -0.2]);
      mesh(sph(0.22), face, E, [s * 0.15, 0, 0], [1, 0.45, 0.7]);
      mesh(sph(0.14), pinkIn, E, [s * 0.17, 0, 0.06], [1, 0.4, 0.5]);
      ears.push(E);
    }
    const eyes = faceEyes(head, 0.22, 0.05, 0.53, 0.14, lid);
    blush(head, 0.35, -0.2, 0.5, 0.1);
    mesh(sph(0.07), M("#2a2228", 0.5), head, [0, -0.2, 0.62], [1.3, 0.8, 0.8]);
    const mouth = mouthSet(head, [0, -0.36, 0.58], 0.12, -0.4, "#5a1d24", false);
    const tail = group(body, [0, 1.3, -1.0]); mesh(sph(0.22), wool, tail);
    return { root, body, head, legs, tail, ears, eyes, setMouth: mouth.set, setEyes: (n) => setEyes(eyes, n), height: 2.7 };
  }
  function horse() {
    const root = new T.Group(), body = group(root);
    const brown = M("#b8622c", 0.6), mane = M("#4a2414", 0.7), hoof = M("#2a1a12", 0.6), muzzle = M("#8a5038", 0.6), blaze = M("#fff7ee", 0.6);
    const legs = legs4(body, brown, hoof, [-0.38, 0.38], [0.5, -0.5], 1.05, 1.05, 0.18, 0.2);
    mesh(cap(0.6, 0.8), brown, body, [0, 1.45, 0], [1, 0.95, 1], [Math.PI / 2, 0, 0]);
    const neck = mesh(cap(0.38, 0.6), brown, body, [0, 2.05, 0.6], [1, 1, 1], [0.55, 0, 0]);
    const tail = group(body, [0, 1.75, -1.0]);
    mesh(cap(0.14, 0.7), mane, tail, [0, -0.38, -0.15], [1, 1, 1], [0.35, 0, 0]);
    const head = group(body, [0, 2.75, 0.85]);
    const lid = M("#a8551f", 0.6);
    mesh(sph(0.62), brown, head, [0, 0, 0], [1, 1.05, 1]);
    mesh(sph(0.42), muzzle, head, [0, -0.42, 0.42], [1.05, 0.8, 0.9]);
    mesh(sph(0.22), blaze, head, [0, 0.25, 0.5], [0.45, 1.3, 0.4]);
    for (const s of [-1, 1]) mesh(sph(0.06), M("#3a1d10", 0.6), head, [s * 0.14, -0.4, 0.8], [1, 1.3, 0.6]);
    const ears = [];
    for (const s of [-1, 1]) {
      const E = group(head, [s * 0.3, 0.6, -0.05], [0, 0, s * -0.2]);
      mesh(new T.ConeGeometry(0.14, 0.38, 20), brown, E, [0, 0.15, 0], [1, 1, 0.6]);
      ears.push(E);
    }
    const maneG = group(body);
    for (let i = 0; i < 6; i++) mesh(sph(0.2), mane, maneG, [0, 3.35 - i * 0.22, 0.6 - i * 0.18], [0.7, 1, 1]);
    mesh(sph(0.22), mane, head, [0.08, 0.62, 0.2], [1, 0.8, 1]);
    const eyes = faceEyes(head, 0.27, 0.1, 0.48, 0.15, lid);
    const mouth = mouthSet(head, [0, -0.66, 0.68], 0.15, -0.6, "#5a1d24", false);
    return { root, body, head, legs, tail, ears, mane: maneG, eyes, setMouth: mouth.set, setEyes: (n) => setEyes(eyes, n), height: 3.4 };
  }
  function hen() {
    const root = new T.Group(), body = group(root);
    const white = M("#ffffff", 0.75), red = M("#ec3a32", 0.5), yel = M("#ffc21f", 0.5);
    const legs = [];
    for (const s of [-1, 1]) {
      const L = group(body, [s * 0.24, 0.45, 0]);
      mesh(cap(0.05, 0.3), yel, L, [0, -0.25, 0]);
      for (const a of [-0.5, 0, 0.5]) mesh(cap(0.035, 0.16), yel, L, [Math.sin(a) * 0.1, -0.44, Math.cos(a) * 0.1], [1, 1, 1], [Math.PI / 2, 0, -a]);
      legs.push(L);
    }
    mesh(sph(0.7), white, body, [0, 1.05, 0], [1, 0.95, 1.05]);
    const tail = group(body, [0, 1.35, -0.6]);
    for (const [y, r] of [[0.2, 0.25], [0, 0.22], [0.35, 0.2]]) mesh(sph(r), white, tail, [0, y, -0.1 - y * 0.3], [0.6, 1, 0.8]);
    const wings = [];
    for (const s of [-1, 1]) { const Wg = group(body, [s * 0.62, 1.2, 0]); mesh(sph(0.3), white, Wg, [s * 0.05, -0.18, 0], [0.4, 0.9, 0.8]); wings.push(Wg); }
    const head = group(body, [0, 1.95, 0.25]);
    const lid = M("#f2f2f2", 0.7);
    mesh(sph(0.55), white, head);
    for (const [z, y, r] of [[0.2, 0.55, 0.14], [0, 0.62, 0.16], [-0.2, 0.55, 0.13]]) mesh(sph(r), red, head, [0, y, z]);
    const eyes = faceEyes(head, 0.22, 0.12, 0.46, 0.12, lid);
    mesh(new T.ConeGeometry(0.1, 0.22, 16), yel, head, [0, -0.02, 0.6], [1, 1, 0.7], [Math.PI / 2, 0, 0]);
    const jaw = group(head, [0, -0.08, 0.5]);
    mesh(new T.ConeGeometry(0.08, 0.16, 16), yel, jaw, [0, -0.02, 0.08], [1, 1, 0.6], [Math.PI / 2, 0, 0]);
    mesh(sph(0.08), red, head, [0, -0.25, 0.52], [0.8, 1.4, 0.8]);
    const setMouth = (n) => { jaw.rotation.x = n === "closed" ? 0 : 0.45; };
    return { root, body, head, legs, tail, wings, ears: [], eyes, setMouth, setEyes: (n) => setEyes(eyes, n), height: 2.5 };
  }
  function biscuit() {   // stands upright like a toddler, as in biscuit-turnaround.jpg
    const root = new T.Group(), body = group(root);
    const fur = M("#d99a4e", 0.8), cream = M("#fbecd3", 0.8), nose = M("#2a1e1c", 0.3), red = M("#e0393a", 0.5), gold = M("#f4c430", 0.35);
    const legs = [];
    for (const s of [-1, 1]) {
      const L = group(body, [s * 0.25, 0.7, 0]);
      mesh(cap(0.18, 0.3), fur, L, [0, -0.35, 0]);
      mesh(sph(0.22), fur, L, [0, -0.62, 0.08], [1, 0.6, 1.25]);
      legs.push(L);
    }
    mesh(sph(0.55), fur, body, [0, 1.15, 0], [1, 1.05, 0.9]);
    mesh(sph(0.35), cream, body, [0, 1.1, 0.3], [1, 1.1, 0.6]);
    const arms = [];
    for (const s of [-1, 1]) { const A = group(body, [s * 0.5, 1.45, 0.05]); mesh(cap(0.13, 0.35), fur, A, [s * 0.05, -0.28, 0]); mesh(sph(0.15), fur, A, [s * 0.07, -0.55, 0.04]); arms.push(A); }
    const tail = group(body, [0, 1.0, -0.45]); mesh(cap(0.08, 0.35), fur, tail, [0, 0.2, -0.1], [1, 1, 1], [-0.6, 0, 0]);
    const head = group(body, [0, 2.15, 0.05]);
    const lid = M("#cf8f45", 0.8);
    mesh(sph(0.68), fur, head, [0, 0, 0], [1.05, 0.95, 0.95]);
    mesh(sph(0.3), cream, head, [0.25, 0.15, 0.48], [1, 1.1, 0.5]);            // white patch over one eye
    mesh(sph(0.33), fur, head, [0, -0.25, 0.5], [1.05, 0.75, 0.75]);
    mesh(sph(0.11), nose, head, [0, -0.15, 0.78], [1.3, 0.9, 0.8]);
    const ears = [];
    for (const s of [-1, 1]) {
      const E = group(head, [s * 0.58, 0.25, -0.05], [0, 0, s * 0.35]);
      mesh(sph(0.3), fur, E, [s * 0.08, -0.28, 0], [0.45, 1, 0.75]);
      mesh(sph(0.2), cream, E, [s * 0.12, -0.3, 0.05], [0.35, 0.8, 0.6]);
      ears.push(E);
    }
    const eyes = faceEyes(head, 0.25, 0.1, 0.55, 0.15, lid);
    const mouth = mouthSet(head, [0, -0.42, 0.66], 0.14, -0.4, "#7c1d24", false);
    mesh(new T.TorusGeometry(0.4, 0.06, 10, 36), red, body, [0, 1.62, 0], [1, 1, 0.9], [Math.PI / 2, 0, 0]);
    mesh(new T.BoxGeometry(0.2, 0.08, 0.04), gold, body, [0, 1.48, 0.42]);
    return { root, body, head, legs, arms, tail, ears, eyes, setMouth: mouth.set, setEyes: (n) => setEyes(eyes, n), height: 2.9 };
  }
  window.Animals = { cow, pig, duck, sheep, horse, hen, biscuit };
})();
