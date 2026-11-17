"""Small dependency-free repository integrity test."""
from pathlib import Path
import re
import zipfile
ROOT = Path(__file__).resolve().parents[1]
readme = (ROOT / "README.md").read_text()
links = re.findall(r"!\[[^]]*\]\(([^)]+)\)", readme)
assert len(links) >= 6, f"Expected embedded CAD screenshots, got {len(links)}"
for link in links:
    image = ROOT / link
    assert image.is_file(), f"Missing rendered preview: {link}"
    assert image.stat().st_size > 1000, f"Empty preview: {link}"
archive = ROOT / "reference" / "V002_original_preserved.zip"
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None, "V002 archive failed CRC integrity check"
for name in ("src/build_v003.py", "src/validate_v003.py", "docs/validation_v003.json", "step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V003.step"):
    assert (ROOT / name).is_file(), f"Missing source artifact: {name}"
print(f"OK: {len(links)} README CAD images, V002 archive and V003 source/model assets")
