#!/usr/bin/env python

import pywavefront as waves
import argparse
import os
import io
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Converts a .obj file to a .off file")
    parser.add_argument("input", type=os.path.abspath, help="The input .obj file")
    parser.add_argument("output", type = os.path.abspath, help="The output .off file")
    return parser.parse_args()

def get_vertices_and_faces(objpath):
    scene = waves.Wavefront(objpath, collect_faces=True, parse=True)
    vertices = scene.vertices[:]
    faces = []
    for each_mesh in scene.mesh_list:
        faces.extend(each_mesh.faces)
    return vertices, faces

def output_off(offpath, vertices, faces):
    nvertices = len(vertices)
    nfaces = len(faces)
    nnormals = 0
    out = io.StringIO()
    print("OFF", file=out)
    print("%d %d %d" % (nvertices, nfaces, nnormals), file=out)
    for each_vertex in vertices:
        print(' '.join(map(str, each_vertex)), file=out)
    for each_face in faces:
        print('%d %s' % (len(each_face), ' '.join(map(str, each_face))), file=out)
    
    out.seek(0)
    with open(offpath, 'w') as f:
        f.write(out.read())


def convert(objpath, offpath):
    verts, tris = get_vertices_and_faces(objpath)
    output_off(offpath, verts, tris)
    print("Converted %s to %s" % (os.path.relpath(objpath, os.path.abspath('.')), os.path.relpath(offpath, os.path.abspath('.'))))

def convert_dir(objdir, offdir):
    obj_fns = [fn for fn in os.listdir(objdir) if fn.lower().endswith('.obj')]
    if not os.path.exists(offdir):
        os.makedirs(offdir)
    elif os.path.isdir(offdir):
        # All good
        pass
    else:
        raise IOError("Cannot output, path exists but isn't a dir!\n%s" % offdir)
    for each_obj_fn in obj_fns:
        objpath = os.path.join(objdir, each_obj_fn)
        off_fn = os.path.join(os.path.dirname(each_obj_fn), '%s.off' % os.path.splitext(os.path.basename(each_obj_fn))[0])
        offpath = os.path.join(offdir, off_fn)
        convert(objpath, offpath)



def main():
    args = parse_args()
    if os.path.isdir(args.input):
        convert_dir(args.input, args.output)
    elif os.path.isfile(args.input):
        convert(args.input, args.output)
    else:
        print("Could not find file or dir: %s" % args.input, file=sys.stderr)


if __name__ == "__main__":
    main()