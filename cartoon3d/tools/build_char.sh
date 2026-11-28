#!/bin/sh
# retouch -> rig -> copy into the rig test page.   usage: sh cartoon3d/tools/build_char.sh mo
set -e
N=$1; M=character/2-3d-models/$N; B=$(ls -d /d/tools/blender-4.2*/)blender.exe
python cartoon3d/tools/retouch.py $M/$N-for-mixamo.zip character/1-apose-images/$N-apose.jpg $M/$N-retouched.zip $M/retouch.json
"$B" -b -P cartoon3d/tools/autorig.py -- $M/$N-retouched.zip $M/joints.json $M/$N-rigged.glb 2>&1 | grep -E "RIG: v|rror" || true
python - <<PY
import base64,zipfile
z=zipfile.ZipFile('$M/$N-retouched.zip')
open('cartoon3d/rigtest/$N.png','wb').write(z.read('$N.png')); open('cartoon3d/rigtest/${N}_rough.png','wb').write(z.read('${N}_rough.png'))
open('cartoon3d/rigtest/${N}_glb.js','w').write('window.GLB=window.GLB||{};window.GLB.$N="'+base64.b64encode(open('$M/$N-rigged.glb','rb').read()).decode()+'";')
PY
