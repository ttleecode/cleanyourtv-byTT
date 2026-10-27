"""Turn a photo folder into a CleanYourTV wallpapers/ collection: <=100 images, 1920x1080, no EXIF, ~<=300 KB.

Usage: python -I make_wallpapers.py <photo folder> <theme folder>/wallpapers   (needs: pip install pillow)
Landscape photos are centre-cropped to 16:9; portrait photos are centred on a blurred, darkened copy of themselves.
Re-saving drops all EXIF, including GPS location.
"""
import io, os, sys
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

SRC, DST = sys.argv[1], sys.argv[2]
W, H, LIMIT, MAX_BYTES = 1920, 1080, 100, 300_000

def load(p):
    with Image.open(p) as im:
        return ImageOps.exif_transpose(im).convert("RGB")

def cover(im):
    return ImageOps.fit(im, (W, H), Image.LANCZOS)

def portrait(im):
    bg = cover(im).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg = ImageOps.contain(im, (W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg

def save(im, path):
    for q in (85, 80, 75, 70, 65, 60):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        if buf.tell() <= MAX_BYTES:
            break
    with open(path, "wb") as f:
        f.write(buf.getvalue())
    return buf.tell(), q

names = sorted(n for n in os.listdir(SRC) if n.lower().endswith((".jpg", ".jpeg", ".png")))
land, port = [], []
for n in names:
    with Image.open(os.path.join(SRC, n)) as im:
        w, h = ImageOps.exif_transpose(im).size
    (land if w >= h else port).append(n)
take_port = max(0, LIMIT - len(land))
if len(port) > take_port:
    step = len(port) / take_port if take_port else 0
    port = [port[int(i * step)] for i in range(take_port)]
chosen = sorted(land[:LIMIT] + port)
os.makedirs(DST, exist_ok=True)
sizes = []
for i, n in enumerate(chosen, 1):
    im = load(os.path.join(SRC, n))
    out = cover(im) if n in land else portrait(im)
    size, q = save(out, os.path.join(DST, f"{i:03d}.jpg"))
    sizes.append(size)
print(f"wrote {len(chosen)} ({len([n for n in chosen if n in land])} landscape, {len([n for n in chosen if n not in land])} portrait); "
      f"max {max(sizes)//1024} KB, total {sum(sizes)//1024//1024} MB")
