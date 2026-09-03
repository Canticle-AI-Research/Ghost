"""Turn the ComfyUI ghost-blob sprite into a GLB (textured card with thickness)."""

from __future__ import annotations

from pathlib import Path

import bpy

ROOT = Path("/mnt/data/projects/Github-Repositories/Canticle-Research/Ghost")
SPRITE = ROOT / "assets/avatar/ghost_blob_sprite.png"
OUT = ROOT / "assets/avatar/ghost_blob.glb"


def main() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    img = bpy.data.images.load(str(SPRITE))
    width, height = img.size
    aspect = width / max(height, 1)

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.0))
    plane = bpy.context.object
    plane.name = "Ghost"
    plane.scale = (aspect, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    mat = bpy.data.materials.new("GhostMat")
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    if "Emission Color" in bsdf.inputs:
        links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 0.35
    plane.data.materials.append(mat)

    solid = plane.modifiers.new("thickness", "SOLIDIFY")
    solid.thickness = 0.14
    bpy.ops.object.convert(target="MESH")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(OUT), export_format="GLB")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
