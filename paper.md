---
title: 'PyAtomSTL: An Interactive Python Tool for Generating
Watertight (Manifold) Molecular Meshes Optimized for 3D Printing'
tags: 
  - Python 
  - Molecular Visualization 
  - 3D Printing 
  - Additive Manufacturing 
  - Computational Chemistry
authors:
 - name: Raúl Arturo Espejel Morales 
   orcid: 0000-0003-2156-5396 
   affiliation: Facultad de Ciencias, Universidad Nacional Autónoma de México 
 - name: Sebastián Pérez Patricio
   affiliation: Facultad de Ciencias, Universidad Nacional Autónoma de México 
date: 22 June 2026
version: 1.0.0 
bibliography: paper.bib 
---

# Summary 
'PyAtomSTL' is an interactive Python application designed to streamline the workflow between computational chemistry data and physical manufacturing. It features a graphical user interface (GUI) built with 'wxPython' and utilizes 'PyVista' as its 3D rendering engine. The software allows users to import standard chemical structure files, such as '.xyz' and '.mol' formats, and dynamically customize the visual representation of atoms and bonds. Crucially, 'PyAtomSTL' compiles these visual representations into a single, unified, and watertight STL mesh optimized specifically for 3D printing and additive manufacturing.

# Statement of Need 
While multiple robust molecular visualization tools exist---such as PyMOL, VMD, and Chimera---they are primarily engineered for digital rendering, analysis, and high-quality image exports. Translating these digital models into physical objects via 3D printing often introduces significant technical bottlenecks. For instance, exporting intersecting spheres (representing atoms) and cylinders (representing bonds) often results in internal overlaps and non-manifold structures that cause slicing software to fail.

'PyAtomSTL' directly bridges this gap by offering an intuitive, lightweight solution targeted at chemical educators, researchers, and hobbyists. By leveraging the geometric Boolean operations and mesh
merging capabilities of 'PyVista' and 'VTK', the software unifies intersecting atomic spheres and bond cylinders into a clean, single-shell surface. This ensures that the generated '.stl' files are completely watertight and ready for direct consumption by commercial 3D printer slicers (such as Cura or PrusaSlicer) without requiring manual repairs in external mesh-editing software like Blender or MeshLab.

# Features and Architecture 
The core application is divided into three interconnected modules:

1. **'ChemFun.py'**: Manages the core chemical informatics lookup tables, storing universal CPK color standards and covalent radii for a wide range of chemical elements. 
2. **'Atom_panel.py'**: Controls the native cross-platform GUI layout via 'wxPython'. It provides sliders and checkboxes for selective rendering, adjusting individual atomic/bond radius scaling metrics, and altering the visual environment (such as toggling perspective views and setting background colors). 
3. **'PyAtomSTL.py'**: Serves as the main orchestrator and rendering pipeline. It handles file parsing, tracks coordinate matrices, generates 3D geometries via 'PyVista', and wraps the secure dialog cleanup blocks
to handle GUI events smoothly.

Furthermore, 'PyAtomSTL' allows users to dynamically filter which specific element groups or individual bonds are included in the final export, making it highly adaptable for creating custom teaching models of complex crystal lattices or macro-molecular fragments.

# Acknowledgements 
We acknowledge the open-source communities behind 'PyVista', 'wxPython', and 'VTK', whose robust libraries made the development of this tool possible.