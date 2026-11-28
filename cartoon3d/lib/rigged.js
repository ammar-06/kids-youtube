// Rigged image-to-3D characters (GLB from tools/autorig.py, Mixamo bone names) + procedural actions.
// Every pose is a pure function of time t, so Hyperframes can seek to any frame.
// Body frame of the model: +X = character's left, +Y up, +Z = towards the camera (the way it faces).
(function () {
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const AX = { x: V(1, 0, 0), y: V(0, 1, 0), z: V(0, 0, 1) };
  const NAMES = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
    "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand", "RightShoulder", "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"];

  function b64buf(s) { const bin = atob(s), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; }

  // parse a base64 GLB; texture comes from an <img> already in the page (no async image decode)
  function load(b64, img, height, done, roughImg) {
    new THREE.GLTFLoader().parse(b64buf(b64), "", (g) => {
      const root = new THREE.Group(), model = g.scene;
      const tex = new THREE.Texture(img); tex.flipY = false; tex.encoding = THREE.sRGBEncoding; tex.needsUpdate = true;
      tex.anisotropy = 4;
      let skinned = null;
      model.traverse((o) => {
        if (o.isMesh) {
          const mp = { map: tex, roughness: 1, metalness: 0 };
          if (roughImg) { const rt = new THREE.Texture(roughImg); rt.flipY = false; rt.needsUpdate = true; mp.roughnessMap = rt; }
          else mp.roughness = 0.75;
          o.material = new THREE.MeshStandardMaterial(mp);
          o.castShadow = true; o.receiveShadow = false; o.frustumCulled = false; if (o.isSkinnedMesh) skinned = o;
        }
      });
      const box = new THREE.Box3().setFromObject(model), h = box.max.y - box.min.y;
      const k = height / h; model.scale.multiplyScalar(k); model.position.y = -box.min.y * k;
      root.add(model);
      model.updateMatrixWorld(true);
      const bones = {};
      model.traverse((o) => { if (o.isBone) { const n = o.name.replace(/^mixamorig:?/, ""); bones[n] = o; } });
      const rest = {};
      for (const n of NAMES) {
        const b = bones[n]; if (!b) continue;
        const wp = new THREE.Quaternion(); if (b.parent) b.parent.getWorldQuaternion(wp);
        const mq = new THREE.Quaternion(); model.getWorldQuaternion(mq);
        rest[n] = { q: b.quaternion.clone(), p: b.position.clone(), wp: mq.clone().invert().multiply(wp) };
      }
      done({ root, model, bones, rest, skinned, height });
    }, (e) => { throw e; });
  }

  // apply body-frame rotations: rot = {Bone: [[axis, angle], ...]}
  const tq = new THREE.Quaternion(), dq = new THREE.Quaternion(), iq = new THREE.Quaternion();
  function apply(c, rot, hipLift, hipShift) {
    for (const n in c.rest) {
      const r = c.rest[n], b = c.bones[n];
      dq.identity();
      const list = rot[n];
      if (list) for (const [ax, ang] of list) { tq.setFromAxisAngle(AX[ax], ang); dq.premultiply(tq); }
      // local = Wp^-1 * D * Wp * Qrest
      iq.copy(r.wp).invert();
      b.quaternion.copy(iq).multiply(dq).multiply(r.wp).multiply(r.q);
      b.position.copy(r.p);
    }
    const hb = c.bones.Hips;
    if (hb && (hipLift || hipShift)) {
      // world offset (in character heights) -> hips' parent space
      const w = V((hipShift || 0) * c.height, (hipLift || 0) * c.height, 0);
      const inv = new THREE.Matrix4().copy(hb.parent.matrixWorld).invert();
      const p0 = V(0, 0, 0).applyMatrix4(c.root.matrixWorld).applyMatrix4(inv);
      const p1 = w.applyMatrix4(c.root.matrixWorld).applyMatrix4(inv);
      hb.position.add(p1.sub(p0));
    }
  }

  const S = Math.sin, C = Math.cos, PI = Math.PI;
  const ease = (x) => x < 0 ? 0 : x > 1 ? 1 : x * x * (3 - 2 * x);

  // ---- actions: (t, amt) -> {rot, lift}; t in seconds, all looping and smooth
  const A = {
    idle(t) {
      const b = S(t * 2.2);
      return { rot: {
        Spine: [["z", 0.025 * S(t * 1.1)]], Head: [["z", 0.06 * S(t * 1.1 + 0.6)], ["x", 0.03 * b]],
        LeftArm: [["z", 0.04 + 0.03 * b]], RightArm: [["z", -0.04 - 0.03 * b]],
      }, lift: 0.004 * b };
    },
    wave(t) {  // right hand up, waving
      const w = S(t * 9);
      return { rot: {
        RightArm: [["z", -1.75], ["x", -0.2]], RightForeArm: [["z", -0.75 + 0.4 * w]], RightHand: [["z", 0.2 * w]],
        LeftArm: [["z", 0.05]], Head: [["z", -0.12], ["y", -0.1]], Spine: [["z", 0.05]],
      }, lift: 0.006 * S(t * 4.5) };
    },
    wave2(t) {  // both hands
      const w = S(t * 9);
      return { rot: {
        RightArm: [["z", -1.75]], RightForeArm: [["z", -0.75 + 0.4 * w]],
        LeftArm: [["z", 1.75]], LeftForeArm: [["z", 0.75 - 0.4 * w]], Head: [["z", 0.08 * w]],
      }, lift: 0.01 * Math.abs(S(t * 4.5)) };
    },
    walk(t, speed) {
      const f = t * (speed || 7), s = S(f);
      return { rot: {
        LeftUpLeg: [["x", -0.8 * s]], RightUpLeg: [["x", 0.8 * s]],
        LeftLeg: [["x", 0.9 * Math.max(0, C(f))]], RightLeg: [["x", 0.9 * Math.max(0, -C(f))]],
        LeftFoot: [["x", -0.3 * s]], RightFoot: [["x", 0.3 * s]],
        LeftArm: [["z", 0.12], ["x", 0.75 * s]], RightArm: [["z", -0.12], ["x", -0.75 * s]],
        LeftForeArm: [["x", -0.25]], RightForeArm: [["x", -0.25]],
        Spine: [["y", 0.08 * s]], Head: [["y", -0.06 * s], ["z", 0.04 * s]],
      }, lift: 0.03 * Math.abs(C(f)) };
    },
    clap(t) {
      const c = 0.5 + 0.5 * S(t * 11);
      return { rot: {
        LeftArm: [["x", -1.05], ["y", -0.15 - 0.35 * c], ["z", 0.35]], RightArm: [["x", -1.05], ["y", 0.15 + 0.35 * c], ["z", -0.35]],
        LeftForeArm: [["y", -0.6 - 0.2 * c]], RightForeArm: [["y", 0.6 + 0.2 * c]],
        Head: [["x", 0.08 * S(t * 5.5)]],
      }, lift: 0.008 * Math.abs(S(t * 5.5)) };
    },
    jump(t) {  // one hop per 1.1 s: crouch, fly with arms up, land
      const p = (t % 1.1) / 1.1;
      const air = p > 0.25 && p < 0.8 ? S((p - 0.25) / 0.55 * PI) : 0;
      const crouch = p < 0.25 ? S(p / 0.25 * PI) : p > 0.8 ? S((p - 0.8) / 0.2 * PI) * 0.7 : 0;
      const up = air;
      return { rot: {
        LeftUpLeg: [["x", -0.6 * crouch]], RightUpLeg: [["x", -0.6 * crouch]], LeftLeg: [["x", 1.1 * crouch]], RightLeg: [["x", 1.1 * crouch]],
        LeftFoot: [["x", -0.5 * crouch]], RightFoot: [["x", -0.5 * crouch]],
        LeftArm: [["z", 0.2 + 1.8 * up]], RightArm: [["z", -0.2 - 1.8 * up]], Spine: [["x", 0.25 * crouch]],
      }, lift: 0.22 * air - 0.05 * crouch };
    },
    cheer(t) {
      const b = Math.abs(S(t * 5));
      return { rot: {
        LeftArm: [["z", 2.0 + 0.15 * S(t * 10)]], RightArm: [["z", -2.0 - 0.15 * S(t * 10 + 1)]],
        LeftForeArm: [["z", 0.2]], RightForeArm: [["z", -0.2]], Head: [["x", -0.15]],
      }, lift: 0.05 * b };
    },
    dance(t) {
      const f = t * 5.2, s = S(f), s2 = S(f * 2);
      return { rot: {
        Hips: [["z", 0.12 * s]], Spine: [["z", -0.18 * s]], Head: [["z", 0.15 * s]],
        LeftArm: [["z", 1.0 + 0.7 * s], ["x", -0.3]], RightArm: [["z", -1.0 + 0.7 * s], ["x", -0.3]],
        LeftForeArm: [["z", 0.8 * Math.max(0, s)]], RightForeArm: [["z", -0.8 * Math.max(0, -s)]],
        LeftUpLeg: [["z", 0.1 * Math.max(0, s)], ["x", -0.3 * Math.max(0, s2)]], RightUpLeg: [["z", 0.1 * Math.min(0, s)], ["x", -0.3 * Math.max(0, -s2)]],
        LeftLeg: [["x", 0.5 * Math.max(0, s2)]], RightLeg: [["x", 0.5 * Math.max(0, -s2)]],
      }, lift: 0.015 * Math.abs(s2) };
    },
    point(t) {
      return { rot: {
        RightArm: [["z", -0.9], ["x", -0.9]], RightForeArm: [["z", -0.1]], LeftArm: [["z", 0.05]],
        Head: [["y", -0.25], ["z", -0.05 * S(t * 3)]], Spine: [["y", -0.12]],
      }, lift: 0.004 * S(t * 3) };
    },
  };

  // blend two actions: mix in [0,1]
  function lerpRot(a, b, m) {
    const out = {}, names = new Set([...Object.keys(a.rot), ...Object.keys(b.rot)]);
    for (const n of names) {
      const la = a.rot[n] || [], lb = b.rot[n] || [];
      out[n] = la.map(([ax, v]) => [ax, v * (1 - m)]).concat(lb.map(([ax, v]) => [ax, v * m]));
    }
    return { rot: out, lift: (a.lift || 0) * (1 - m) + (b.lift || 0) * m };
  }

  // pose(c, t, plan): plan = [[startTime, action], ...] sorted; 0.35 s crossfade between actions
  function pose(c, t, plan, fade) {
    fade = fade || 0.35;
    let i = 0;
    while (i + 1 < plan.length && plan[i + 1][0] <= t) i++;
    const cur = A[plan[i][1]](t - plan[i][0]);
    let res = cur;
    if (i > 0 && t - plan[i][0] < fade) res = lerpRot(A[plan[i - 1][1]](t - plan[i - 1][0]), cur, ease((t - plan[i][0]) / fade));
    apply(c, res.rot, res.lift);
  }

  window.Rigged = { load, apply, pose, actions: A };
})();
