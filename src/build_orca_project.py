"""Build a native, arranged Orca project from the active printed-part BOM.

Uses installed profiles without modifying them. Never uploads or starts a print.
Run with the repository Python environment; OrcaSlicer must be installed.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    ('V010_first_arm', 1), ('V010_second_arm', 1),
    ('V010_scalloped_thumbwheel', 4), ('V010_relieved_camera_shell', 1),
    ('V010_wrist_adapter', 1), ('V004_removable_camera_bezel', 1),
    ('V004_mount_plate', 1), ('V004_recessed_alignment_key', 1),
]
OUTPUT = ROOT / 'orca' / 'V010_printed_parts.3mf'


def installed_profiles():
    base = Path.home() / 'Library/Application Support/OrcaSlicer'
    if not base.is_dir():
        base = Path.home() / '.config/OrcaSlicer'
    profiles = {}
    for folder in ('system', 'user'):
        for path in (base / folder).rglob('*.json'):
            try:
                data = json.loads(path.read_text())
                profiles[data.get('name', path.stem)] = data
            except (ValueError, UnicodeError):
                continue

    def resolve(name, chain=()):
        if name in chain:
            raise ValueError(f'Circular profile inheritance: {name}')
        data = profiles[name]
        result = resolve(data['inherits'], chain + (name,)) if data.get('inherits') else {}
        result.update(data)
        result.pop('inherits', None)
        # No device connection credentials belong in a shareable print project.
        for key in list(result):
            if any(token in key.lower() for token in ('api_key', 'password', 'print_host', 'printhost')):
                result.pop(key)
        return result
    return resolve


def verify_project(path):
    """Check native settings, individual build items and actual transformed bounds."""
    import numpy as np
    import trimesh
    with zipfile.ZipFile(path) as archive:
        assert 'Metadata/project_settings.config' in archive.namelist()
        model = ET.fromstring(archive.read('3D/3dmodel.model'))
        ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
        items = model.findall('m:build/m:item', ns)
        assert len(items) == sum(qty for _, qty in PARTS), len(items)
    scene = trimesh.load(path, force='scene')
    from shapely.geometry import MultiPoint
    bounds = []
    footprints = []
    for node in scene.graph.nodes_geometry:
        transform, geometry = scene.graph[node]
        mesh = scene.geometry[geometry].copy()
        # The 3MF loader repeats shared-volume faces for cloned build items.
        mesh.process(validate=True)
        mesh.apply_transform(transform)
        assert mesh.is_watertight and mesh.is_volume, node
        low, high = mesh.bounds
        assert abs(low[2]) < .02, (node, 'not grounded', low)
        assert np.all(low[:2] >= 5) and np.all(high[:2] <= 230), (node, 'outside bed margin')
        bounds.append((low, high))
        footprints.append(MultiPoint(mesh.vertices[:, :2]).convex_hull)
    assert len(bounds) == 11, len(bounds)
    minimum = min(a.distance(b) for i,a in enumerate(footprints) for b in footprints[i+1:])
    assert minimum >= 5.9, ('Insufficient part spacing', minimum)
    print(f'Verified {len(bounds)} independent grounded objects; minimum projected-hull gap {minimum:.2f} mm')


def build():
    executable = os.environ.get('ORCASLICER_PATH', '/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer')
    assert Path(executable).is_file(), executable
    OUTPUT.parent.mkdir(exist_ok=True)
    resolve = installed_profiles()
    with tempfile.TemporaryDirectory(prefix='frame-monitor-orca-') as temporary:
        temporary = Path(temporary)
        settings = []
        for kind, name in [('machine', 'Elegoo Neptune 2 0.4 nozzle - Copy'),
                           ('process', 'Elegoo Neptune 2 0.20 mm Balanced'),
                           ('filament', 'Panchroma PLA Matte - Neptune 2')]:
            data = resolve(name)
            if kind == 'process':
                data.update(wall_loops='4', sparse_infill_density='30%',
                            enable_support='1', support_type='normal(auto)',
                            support_on_build_plate_only='0', brim_type='no_brim',
                            duplicate_distance='8')
            path = temporary / f'{kind}.json'
            path.write_text(json.dumps(data))
            settings.append(str(path))
        command = [executable, '--load-settings', ';'.join(settings[:2]),
                   '--load-filaments', settings[2], '--load-defaultfila',
                   '--clone-objects', ','.join(str(qty) for _, qty in PARTS),
                   '--ground-largest-face', '--orient', '0', '--arrange', '1',
                   '--allow-rotations', '--ensure-on-bed',
                   '--export-3mf', str(OUTPUT)]
        command.extend(str(ROOT / 'stl' / f'{name}.stl') for name, _ in PARTS)
        subprocess.run(command, check=True, timeout=180)
    verify_project(OUTPUT)
    print(OUTPUT)


if __name__ == '__main__':
    build()
