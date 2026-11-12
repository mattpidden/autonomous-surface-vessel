"""Render the CAD in cad/ to the README images in docs/images/.

Makes:
  cad-*.jpg          views of the full hull and keel (from the STEP files)
  render-water.jpg   the finished boat in ABS orange, floating at its estimated waterline
  print-parts.jpg    each printed part as it sits on the build plate (from the Bambu 3MF)

Setup (once):
    python3 -m venv .venv && .venv/bin/pip install cadquery-ocp pyvista pillow
Run from the repo root:
    .venv/bin/python tools/render_cad.py
"""
import os
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import pyvista as pv
from PIL import Image, ImageChops, ImageDraw, ImageFont
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
PRINT_PROJECT = os.path.join(CAD, "ABS boat settings.3mf")

HULL_COLOUR = "#e9ecef"
KEEL_COLOUR = "#2f6fb0"
ABS_ORANGE = "#ff6a13"

# Estimated all-up mass, used to find the waterline for the water render.
# Battery 1.4, lead + epoxy 2.15, printed ABS ~2.0, thruster 0.2, motors 0.2,
# electronics 0.3, wind sensor 0.3, epoxy coat and hardware 0.5
ESTIMATED_MASS_KG = 7.0
SEAWATER_DENSITY = 1.025  # kg per litre


# ---------- loading ----------

def load_step(path, tolerance=0.3):
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


CORE = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
PROD = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def _transform(text):
    """3MF transforms are 12 numbers applied as [x y z 1] @ M."""
    v = [float(x) for x in text.split()]
    m = np.zeros((4, 3))
    m[:3] = np.array(v[:9]).reshape(3, 3)
    m[3] = v[9:]
    return m


def _apply(points, m):
    return np.c_[points, np.ones(len(points))] @ m


def load_3mf(path):
    """Return {object id: mesh} for each plate object, placed as it sits on the build plate."""
    archive = zipfile.ZipFile(path)
    root = ET.fromstring(archive.read("3D/3dmodel.model"))
    files = {}
    objects = {}
    for obj in root.find(CORE + "resources"):
        pieces = []
        for comp in obj.find(CORE + "components"):
            name = comp.get(PROD + "path").lstrip("/")
            if name not in files:
                files[name] = ET.fromstring(archive.read(name))
            for sub in files[name].iter(CORE + "object"):
                if sub.get("id") == comp.get("objectid"):
                    mesh = sub.find(CORE + "mesh")
                    verts = np.array([[float(v.get(a)) for a in "xyz"]
                                      for v in mesh.find(CORE + "vertices")])
                    tris = np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")]
                                     for t in mesh.find(CORE + "triangles")])
                    pieces.append((_apply(verts, _transform(comp.get("transform"))), tris))
        objects[obj.get("id")] = pieces

    placed = {}
    for item in root.find(CORE + "build"):
        m = _transform(item.get("transform"))
        meshes = [pv.PolyData(_apply(v, m), np.c_[np.full(len(t), 3), t].ravel())
                  for v, t in objects[item.get("objectid")]]
        placed[item.get("objectid")] = meshes[0].merge(meshes[1:]) if len(meshes) > 1 else meshes[0]
    return placed


# ---------- helpers ----------

def plotter(size, background=("#dfe6ee", "#ffffff")):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background(background[0], top=background[1])
    p.enable_anti_aliasing("ssaa")
    p.enable_lightkit()
    return p


def add_part(p, mesh, colour, edge_colour="#5a6470"):
    p.add_mesh(mesh, color=colour, smooth_shading=True, specular=0.3,
               specular_power=25, ambient=0.18, diffuse=0.8)
    edges = mesh.extract_feature_edges(40, boundary_edges=True,
                                       non_manifold_edges=False, manifold_edges=False)
    p.add_mesh(edges, color=edge_colour, line_width=1.2)


def crop(im, pad=40):
    """Trim a plain or vertical-gradient background."""
    im = im.convert("RGB")
    background = im.crop((0, 0, 1, im.height)).resize(im.size)
    mask = ImageChops.difference(im, background).convert("L").point(lambda v: 255 if v > 12 else 0)
    left, top, right, bottom = mask.getbbox()
    return im.crop((max(left - pad, 0), max(top - pad, 0),
                    min(right + pad, im.width), min(bottom + pad, im.height)))


def save_jpg(im, name, max_size=1400):
    im.thumbnail((max_size, max_size))
    im.save(os.path.join(OUT, name), quality=88)
    print("wrote", f"docs/images/{name}")


def screenshot(p):
    image = Image.fromarray(p.screenshot(return_img=True))
    p.close()
    return image


# ---------- CAD views ----------

def render_cad_views(hull, keel):
    boat = [(hull, HULL_COLOUR), (keel, KEEL_COLOUR)]
    c = np.array(hull.center)
    # +X is the bow, +Y is up
    views = {
        "hero": ([900, 650, 1100], [0, -80, 0], 1.15, (1800, 1100)),
        "top-inside": ([250, 1500, 500], [0, 0, 0], 1.2, (1800, 1100)),
        "side": ([0, -100, 1800], [0, -100, 0], 1.25, (1800, 900)),
        "underside": ([-900, -800, 1000], [0, -120, 0], 1.1, (1800, 1100)),
    }
    for name, (offset, target, zoom, size) in views.items():
        p = plotter(size)
        for mesh, colour in boat:
            add_part(p, mesh, colour)
        p.camera_position = [tuple(c + offset), tuple(c + target), (0, 1, 0)]
        p.camera.zoom(zoom)
        save_jpg(crop(screenshot(p)), f"cad-{name}.jpg")


# ---------- floating render ----------

def waterline(hull, keel, mass_kg):
    """Find the waterline height (mm) where displaced seawater matches the boat's mass.

    Slices the hull every 5 mm along its length and treats everything between the outer
    bottom and the waterline as displaced, which is close for these near-vertical sides.
    """
    boat = hull.merge(keel)
    dz = 2.0
    zs = np.arange(boat.bounds[4], boat.bounds[5], dz)
    bottoms = []
    for x in np.arange(boat.bounds[0] + 1, boat.bounds[1], 5.0):
        section = boat.slice(normal="x", origin=(x, 0, 0))
        if section.n_points == 0:
            continue
        pts = np.array(section.points)
        lines, i, dense = section.lines, 0, [pts]
        while i < len(lines):
            n = lines[i]
            ids = lines[i + 1:i + 1 + n]
            i += 1 + n
            for a, b in zip(ids[:-1], ids[1:]):
                steps = int(np.linalg.norm(pts[b] - pts[a])) + 1
                t = np.linspace(0, 1, steps + 1)[:, None]
                dense.append(pts[a] + (pts[b] - pts[a]) * t)
        pts = np.vstack(dense)
        bins = np.floor((pts[:, 2] - zs[0]) / dz).astype(int)
        row = np.full(len(zs), np.nan)
        for k in range(len(zs)):
            sel = pts[bins == k]
            if len(sel):
                row[k] = sel[:, 1].min()
        bottoms.append(row)
    bottoms = np.array(bottoms)

    target_litres = mass_kg / SEAWATER_DENSITY
    for level in np.arange(np.nanmin(bottoms), boat.bounds[3], 1.0):
        litres = np.nansum(np.clip(level - bottoms, 0, None)) * 5.0 * dz / 1e6
        if litres >= target_litres:
            return level
    return boat.bounds[3]


def render_water(hull, keel):
    level = waterline(hull, keel, ESTIMATED_MASS_KG)
    print(f"waterline at y = {level:.0f} mm for {ESTIMATED_MASS_KG} kg")

    xs = np.linspace(-3000, 3000, 400)
    X, Z = np.meshgrid(xs, xs)
    Y = (level + 3.0 * np.sin(X / 55 + Z / 90) + 2.0 * np.sin(X / 23 - Z / 41)
         + 1.2 * np.sin(Z / 17))
    water = pv.StructuredGrid(X, Y, Z).extract_surface(algorithm="dataset_surface").compute_normals()

    p = plotter((2000, 1200), background=("#9cc7e4", "#eaf4fb"))
    p.enable_depth_peeling(10)
    for mesh in (hull, keel):
        p.add_mesh(mesh, color=ABS_ORANGE, smooth_shading=True, specular=0.35,
                   specular_power=30, ambient=0.2, diffuse=0.8)
    p.add_mesh(water, color="#1f6f8b", opacity=0.72, smooth_shading=True,
               specular=0.9, specular_power=60, ambient=0.25, diffuse=0.6)
    c = np.array([20.0, level - 70, 0.0])
    p.camera_position = [tuple(c + [1050, 330, 1150]), tuple(c), (0, 1, 0)]
    p.camera.view_angle = 30
    image = screenshot(p)
    w, h = image.size
    save_jpg(image.crop((200, 150, w - 200, h - 120)), "render-water.jpg", max_size=1600)


# ---------- printed parts ----------

def render_print_parts():
    placed = load_3mf(PRINT_PROJECT)
    # Object ids from the 3MF: 2 bow, 13 middle section, 4 keel, 6-9 dowels
    dowels = placed["6"].merge([placed["7"], placed["8"], placed["9"]])
    parts = [("Bow", placed["2"]), ("Middle section", placed["13"]),
             ("Keel", placed["4"]), ("Dowels ×4", dowels)]

    bed = 256  # P1S build plate, mm
    tiles = []
    for label, mesh in parts:
        mesh = mesh.compute_normals(split_vertices=True, feature_angle=35)
        lo, hi = np.array(mesh.bounds[::2]), np.array(mesh.bounds[1::2])
        centre = (lo + hi) / 2
        p = plotter((900, 1000), background=("#ffffff", "#ffffff"))
        add_part(p, mesh, ABS_ORANGE, edge_colour="#8a3a0a")
        small = label.startswith("Dowels")
        plate_size = 60 if small else bed
        plate = pv.Plane(center=(centre[0], centre[1], lo[2] - 0.6), direction=(0, 0, 1),
                         i_size=plate_size, j_size=plate_size)
        p.add_mesh(plate, color="#33373b", ambient=0.45)
        if not small:
            # outline of the 256 mm build volume, to show the parts use the full height
            box = pv.Box((centre[0] - bed / 2, centre[0] + bed / 2,
                          centre[1] - bed / 2, centre[1] + bed / 2, lo[2], lo[2] + bed))
            p.add_mesh(box.extract_all_edges(), color="#b8bec5", line_width=1.0)
        d = plate_size * 2.4
        target = centre if small else np.array([centre[0], centre[1], lo[2] + bed / 2])
        p.camera_position = [tuple(target + [d * 0.85, -d * 1.05, d * 0.7]), tuple(target), (0, 0, 1)]
        tiles.append((label, crop(screenshot(p), pad=20)))

    # One labelled strip, tiles scaled to the same height
    height = 420
    tiles = [(label, im.resize((round(im.width * height / im.height), height))) for label, im in tiles]
    gap, label_h = 30, 60
    sheet = Image.new("RGB", (sum(im.width for _, im in tiles) + gap * (len(tiles) - 1),
                              height + label_h), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except OSError:
        font = ImageFont.load_default()
    x = 0
    for label, im in tiles:
        sheet.paste(im, (x, 0))
        tw = draw.textlength(label, font=font)
        draw.text((x + (im.width - tw) / 2, height + 14), label, fill="#333333", font=font)
        x += im.width + gap
    save_jpg(sheet, "print-parts.jpg", max_size=1800)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hull = load_step(os.path.join(CAD, "scowhull.step"))
    keel = load_step(os.path.join(CAD, "keel.step"))
    render_cad_views(hull, keel)
    render_water(hull, keel)
    render_print_parts()
