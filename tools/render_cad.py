"""Render the STEP files in cad/ to the README images in docs/images/.

Setup (once):
    python3 -m venv .venv && .venv/bin/pip install cadquery-ocp pyvista pillow
Run from the repo root:
    .venv/bin/python tools/render_cad.py
"""
import os
import numpy as np
import pyvista as pv
from PIL import Image, ImageChops
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAD = os.path.join(ROOT, "cad")
OUT = os.path.join(ROOT, "docs", "images")

HULL_COLOUR = "#e9ecef"
KEEL_COLOUR = "#2f6fb0"


def load_mesh(path, tolerance=0.3):
    """Read a STEP file and tessellate it into a PyVista mesh."""
    reader = STEPControl_Reader()
    assert reader.ReadFile(path) == 1, path
    reader.TransferRoots()
    shape = reader.OneShape()
    BRepMesh_IncrementalMesh(shape, tolerance, False, 0.3, True)

    points, faces, offset = [], [], 0
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face(explorer.Current())
        location = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, location)
        if tri is not None:
            trsf = location.Transformation()
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(trsf)
                points.append((p.X(), p.Y(), p.Z()))
            reversed_face = face.Orientation() == TopAbs_REVERSED
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                if reversed_face:
                    b, c = c, b
                faces.append((3, a - 1 + offset, b - 1 + offset, c - 1 + offset))
            offset += tri.NbNodes()
        explorer.Next()
    mesh = pv.PolyData(np.array(points), np.array(faces).ravel())
    return mesh.compute_normals(split_vertices=True, feature_angle=35)


def crop(path, pad=40, max_size=1400):
    """Trim the gradient background, shrink, and save as JPEG."""
    im = Image.open(path).convert("RGB")
    background = im.crop((0, 0, 1, im.height)).resize(im.size)
    mask = ImageChops.difference(im, background).convert("L").point(lambda v: 255 if v > 12 else 0)
    left, top, right, bottom = mask.getbbox()
    im = im.crop((max(left - pad, 0), max(top - pad, 0),
                  min(right + pad, im.width), min(bottom + pad, im.height)))
    im.thumbnail((max_size, max_size))
    im.save(path.replace(".png", ".jpg"), quality=88)
    os.remove(path)


def shot(name, parts, offset, target_offset, centre, zoom=1.0, size=(1800, 1100)):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("#dfe6ee", top="#ffffff")
    p.enable_anti_aliasing("ssaa")
    p.enable_lightkit()
    for mesh, colour in parts:
        p.add_mesh(mesh, color=colour, smooth_shading=True, specular=0.25,
                   specular_power=20, ambient=0.15, diffuse=0.8)
        edges = mesh.extract_feature_edges(40, boundary_edges=True,
                                           non_manifold_edges=False, manifold_edges=False)
        p.add_mesh(edges, color="#5a6470", line_width=1.2)
    p.camera_position = [tuple(centre + offset), tuple(centre + target_offset), (0, 1, 0)]
    p.camera.zoom(zoom)
    path = os.path.join(OUT, f"cad-{name}.png")
    p.screenshot(path)
    p.close()
    crop(path)
    print("wrote", f"docs/images/cad-{name}.jpg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hull = load_mesh(os.path.join(CAD, "scowhull.step"))
    keel = load_mesh(os.path.join(CAD, "keel.step"))
    boat = [(hull, HULL_COLOUR), (keel, KEEL_COLOUR)]
    c = np.array(hull.center)
    # +X is the bow, +Y is up
    shot("hero", boat, [900, 650, 1100], [0, -80, 0], c, zoom=1.15)
    shot("top-inside", boat, [250, 1500, 500], [0, 0, 0], c, zoom=1.2)
    shot("side", boat, [0, -100, 1800], [0, -100, 0], c, zoom=1.25, size=(1800, 900))
    shot("underside", boat, [-900, -800, 1000], [0, -120, 0], c, zoom=1.1)
