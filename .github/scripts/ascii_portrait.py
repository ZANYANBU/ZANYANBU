"""Turn a cut-out portrait (PNG/WebP with a transparent background) into ASCII art.

Run once by hand when the photo changes:
    python3 .github/scripts/ascii_portrait.py photo.webp > .github/profile/ascii.txt
    python3 .github/scripts/ascii_portrait.py photo.webp --light > .github/profile/ascii-light.txt
The --light version flips the shading so the face still reads right on a white background.
"""
import sys
from PIL import Image, ImageOps

COLS = 64
RAMP = " .:-=+*#%@"  # light to dense; brighter parts of the photo get denser characters

def main(path, light=False):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    w, h = im.size
    rows = int(h / w * COLS * 0.5)  # a character is about twice as tall as it is wide
    big = im.resize((COLS * 4, rows * 4), Image.LANCZOS)
    mask = big.getchannel("A").point(lambda a: 255 if a > 110 else 0)
    grey = ImageOps.equalize(big.convert("L"), mask=mask).resize((COLS, rows), Image.LANCZOS)
    alpha = im.resize((COLS, rows), Image.LANCZOS).getchannel("A")
    for y in range(rows):
        line = ""
        for x in range(COLS):
            if alpha.getpixel((x, y)) < 110:
                line += " "
                continue
            v = grey.getpixel((x, y)) / 255
            if light:
                v = 1 - v
            line += RAMP[max(1, min(len(RAMP) - 1, round(v * (len(RAMP) - 1))))]
        print(line.rstrip())

if __name__ == "__main__":
    main(sys.argv[1], "--light" in sys.argv[2:])
