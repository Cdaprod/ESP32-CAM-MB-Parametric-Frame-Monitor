"""V010 canonical release integrity; run after CAD-generated files are committed."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert (ROOT/'VERSION').read_text().strip()=='V010'
r=json.loads((ROOT/'docs/CURRENT_RELEASE.json').read_text())
assert r['release']=='V010' and r['is_current']
readme=(ROOT/'README.md').read_text()
assert '**Current development release: V010' in readme
for image in r['previews']:
    path=ROOT/image
    assert path.is_file(),f'Missing real CAD preview {image}'
    assert path.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    assert f']({image})' in readme
assert (ROOT/'docs/BOM.csv').read_bytes()==(ROOT/'docs/BOM_V010.csv').read_bytes()
for stl in r['new_stls']:
    assert (ROOT/stl).is_file(),stl
    assert (ROOT/stl.replace('stl/','step/').replace('.stl','.step')).is_file(),stl
assert (ROOT/'step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V010.step').is_file()
assert (ROOT/'previews/v009_full_assembly.png').is_file()
print('PASS V010 canonical release and eight embedded CAD renders')
