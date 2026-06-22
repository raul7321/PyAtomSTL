# PyAtomSTL

An interactive Python GUI application built with `wxPython` and `PyVista` to import molecular structure files (`.xyz` and `.mol`) and generate clean, watertight (manifold) STL meshes optimized for 3D printing and additive manufacturing.

## Features

* **File Support:** Easily parse standard molecular data files (`.xyz` and `.mol`).
* **Interactive 3D Preview:** Real-time molecular visualization powered by `PyVista` and `VTK`.
* **Dynamic Customization:** Adjust individual atomic/bond radius scaling and element visibility via a native `wxPython` graphical interface.
* **Anaglifo 3D Support:** Toggle Stereoscopic Anaglyph Mode (Red/Cyan) for 3D depth perception on standard screens—ideal for educational settings.
* **3D Print Ready:** Automatically merges overlapping atomic spheres and cylinders into a single, closed, watertight (manifold) mesh. Ready to slice in Cura, PrusaSlicer, or LycheeSlicer without manual repairs.

## Installation

### Prerequisites
Make sure you have Python 3.8 or higher installed on your system.

### Automated Installation (Windows)
If you are on Windows, simply double-click the installation script located in the repository:
```bash
install_windows.bat
