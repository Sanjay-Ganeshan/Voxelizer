import os
import subprocess
import argparse

rootdir = os.path.dirname(os.path.abspath(__file__))
voxelize_bin = os.path.join(rootdir, 'bin', 'voxelize')
scripts_dir = os.path.join(rootdir, 'vox_scripts')
obj_to_off_py = os.path.join(scripts_dir,'obj_to_off.py')
scale_off_py = os.path.join(scripts_dir, 'scale_off.py')
occ_to_np_py = os.path.join(scripts_dir, 'occ_to_np.py')

def parse_args():
    parser = argparse.ArgumentParser(description="Converts a triangle mesh into a voxel grid")
    parser.add_argument('input', help='directory of input files')
    parser.add_argument('-o', '--output', help='directory of output files')
    parser.add_argument('-d', '--dims', type=lambda s:tuple(map(int, s.split('x'))), default=(32, 32, 32), help='Dimensions WxHxD')
    return parser.parse_args()

def convert_to_off(obj_dir, off_dir):
    subprocess.call([
        "python",
        obj_to_off_py,
        obj_dir,
        off_dir
        ]
    )

def scale_mesh(off_dir, off_scaled_dir, width=32, height=32, depth=32, padding=0.1):
    subprocess.call(
        [
            "python",
            scale_off_py,
            off_dir,
            off_scaled_dir,
            "--width",
            str(width),
            "--height",
            str(height),
            "--depth",
            str(depth),
            "--padding",
            str(padding)
        ]
    )

def voxelize(scaled_inputs, output_h5, width = 32, height = 32, depth = 32):
    subprocess.call(
        [
            voxelize_bin,
            "occ",
            "--input",
            scaled_inputs,
            "--output",
            output_h5,
            "--width",
            str(width),
            "--height",
            str(height),
            "--depth",
            str(depth)
        ]
    )

def convert_to_np(input_h5, output_np):
    subprocess.call(
        [
            "python",
            occ_to_np_py,
            input_h5,
            output_np
        ]
    )

def deletedir(d):
    subprocess.call(
        [
        "rm",
        "-rf",
        d
        ]
    )

def pipeline(input_obj_dir, np_dir = None, width = 32, height = 32, depth = 32, padding = 0.1, clean = True):
    obj_filenames = sorted(os.listdir(input_obj_dir))
    dataroot_dir = os.path.dirname(input_obj_dir)
    off_dir = os.path.join(dataroot_dir, "input_off")
    scaled_dir = os.path.join(dataroot_dir, "input_scaled")
    output_h5 = os.path.join(dataroot_dir, "voxels.h5")
    if np_dir is None:
        np_dir = os.path.join(dataroot_dir, "output")
    output_np = np_dir
    convert_to_off(input_obj_dir, off_dir)
    scale_mesh(off_dir, scaled_dir, width, height, depth, padding)
    voxelize(scaled_dir, output_h5, width, height, depth)
    convert_to_np(output_h5, output_np)
    for i in range(len(obj_filenames)):
        # Rename to original names
        origname = os.path.join(np_dir, '%d.npy' % i)
        newname = os.path.join(np_dir, '%s.npy' % os.path.splitext(obj_filenames[i])[0])
        os.rename(origname, newname)
        print("Renaming %s to %s" % (os.path.basename(origname), os.path.basename(newname)))
    # Clean
    if clean:
        deletedir(off_dir)
        deletedir(scaled_dir)
        os.remove(output_h5)


def main():
    args = parse_args()
    w,h,d = args.dims
    pipeline(args.input, np_dir=args.output, width=w, height=h, depth=d, padding=0.1, clean=True)

if __name__ == "__main__":
    main()

