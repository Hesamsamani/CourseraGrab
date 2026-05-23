"""
build_icon.py - turn any image into the app's icon files.

Usage:
    py -3.12 build_icon.py "C:\\path\\to\\your\\image.png"

It writes a square icon/icon.png (512x512) and a multi-size icon/icon.ico
into the icon folder next to this script. After running it, just restart the
app (the new icon shows in the window and top-left), and rebuild the .exe to
update its file icon.
"""

import os
import sys

from PIL import Image


def make(src):
    here = os.path.dirname(os.path.abspath(__file__))
    icon_dir = os.path.join(here, 'icon')
    os.makedirs(icon_dir, exist_ok=True)

    img = Image.open(src).convert('RGBA')

    # center-crop to a square so nothing gets distorted
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    png_path = os.path.join(icon_dir, 'icon.png')
    ico_path = os.path.join(icon_dir, 'icon.ico')

    img.resize((512, 512), Image.LANCZOS).save(png_path)
    img.save(ico_path, format='ICO',
             sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    print('Wrote:')
    print('  ', png_path)
    print('  ', ico_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: py -3.12 build_icon.py "C:\\path\\to\\image.png"')
        sys.exit(1)
    make(sys.argv[1])
