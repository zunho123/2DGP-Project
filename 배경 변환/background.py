
import argparse, os, statistics
from PIL import Image

def parse_color(s):
    s = s.strip()
    if s.lower() == "auto":
        return None
    if s.startswith("#") and len(s) == 7:
        return tuple(int(s[i:i+2], 16) for i in (1,3,5))
    if "," in s:
        p = s.split(",")
        return (int(p[0]), int(p[1]), int(p[2]))
    raise ValueError

def auto_key(img):
    w, h = img.size
    px = img.load()
    c = [px[0,0], px[w-1,0], px[0,h-1], px[w-1,h-1]]
    r = int(statistics.median([t[0] for t in c]))
    g = int(statistics.median([t[1] for t in c]))
    b = int(statistics.median([t[2] for t in c]))
    return (r, g, b)

def process(img, key, tol, soft, despill):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    kr, kg, kb = key
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            dr = r - kr; dg = g - kg; db = b - kb
            d = (dr*dr + dg*dg + db*db) ** 0.5
            if d <= tol:
                a2 = 0
            elif d < tol + soft:
                t = (d - tol) / soft
                a2 = int(a * t)
            else:
                a2 = a
                if despill and g > max(r, b):
                    m = max(r, b)
                    g = int((g + m) / 2)
            px[x, y] = (r, g, b, a2)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--key", default="auto")
    ap.add_argument("--tol", type=float, default=60.0)
    ap.add_argument("--soft", type=float, default=25.0)
    ap.add_argument("--despill", action="store_true")
    args = ap.parse_args()

    img = Image.open(args.input).convert("RGBA")
    key = parse_color(args.key)
    if key is None:
        key = auto_key(img)
    out = process(img, key, args.tol, args.soft, args.despill)
    out_path = args.output if args.output else os.path.join(os.path.dirname(args.input) or ".", os.path.splitext(os.path.basename(args.input))[0] + "_transparent.png")
    out.save(out_path)

if __name__ == "__main__":
    main()
