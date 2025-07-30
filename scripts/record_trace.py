"""Optional: convert saved rgb frames into a video/gif for the Supervisor."""
import imageio
import argparse
import glob
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace_dir", default="data/traces")
    parser.add_argument("--out", default="data/traces/trace.mp4")
    args = parser.parse_args()

    frames = sorted(glob.glob(os.path.join(args.trace_dir, "*.png")))
    imgs = [imageio.imread(f) for f in frames]
    imageio.mimsave(args.out, imgs, fps=4)


if __name__ == "__main__":
    main()