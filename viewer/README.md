# Current interactive ESP32-CAM-MB assembly

**[Download/open standalone offline 3D HTML viewer](index.html)** · [Complete GLB](COMPLETE_ASSEMBLY.glb) · [Release integrity manifest](release.json) · [Project README](../README.md)

This viewer is generated from the current parametric CAD assembly by `python src/build.py render`, `python src/build.py viewer`, or `python src/build.py all`. Its Plotly JavaScript is embedded; it needs no external scripts or internet connection after download.

**Controls:** drag to orbit, pinch or scroll to zoom, toggle component groups with the legend. The GLB contains the same assembly as the HTML viewer, and `release.json` tracks the STEP model, all eight PNG previews, and viewer-file SHA-256 checksums.

GitHub README pages cannot host an inline script-powered viewer. The linked image at the top of the root README opens the downloadable standalone HTML. For a browser-hosted live viewer, enable GitHub Pages with the repository root as its publishing source; the stable route is `/viewer/`.

Historical `OPEN_V003_OFFLINE.html` and `COMPLETE_ASSEMBLY_V003.glb` remain for provenance but are not the current viewer. All models are CAD references, not physically qualified.
