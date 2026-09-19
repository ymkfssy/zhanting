import zlib, struct, os

OUT = r"C:\Users\gaolin\WorkBuddy\展厅控制\assets\icons"
os.makedirs(OUT, exist_ok=True)


def in_rr(x, y, x0, y0, x1, y1, r):
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    if x < x0 + r and y < y0 + r:
        return (x - (x0 + r)) ** 2 + (y - (y0 + r)) ** 2 <= r * r
    if x > x1 - r and y < y0 + r:
        return (x - (x1 - r)) ** 2 + (y - (y0 + r)) ** 2 <= r * r
    if x < x0 + r and y > y1 - r:
        return (x - (x0 + r)) ** 2 + (y - (y1 - r)) ** 2 <= r * r
    if x > x1 - r and y > y1 - r:
        return (x - (x1 - r)) ** 2 + (y - (y1 - r)) ** 2 <= r * r
    return True


def make_icon(size, maskable=False):
    buf = bytearray([0, 0, 0, 0]) * (size * size)
    pad = int(size * 0.10) if maskable else int(size * 0.06)

    def setpx(x, y, rgba):
        if 0 <= x < size and 0 <= y < size:
            i = (y * size + x) * 4
            buf[i] = rgba[0]; buf[i + 1] = rgba[1]; buf[i + 2] = rgba[2]; buf[i + 3] = rgba[3]

    def roundrect(x0, y0, x1, y1, r, color):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                if in_rr(x, y, x0, y0, x1, y1, r):
                    setpx(x, y, color)

    brand = (15, 32, 39, 255)
    white = (255, 255, 255, 255)
    accent = (45, 212, 191, 255)

    roundrect(pad, pad, size - pad, size - pad, int(size * 0.16), brand)
    ins = int(size * 0.26)
    roundrect(ins, ins, size - ins, int(size * 0.66), int(size * 0.06), white)
    a = int(size * 0.32)
    roundrect(a, a, size - a, int(size * 0.60), int(size * 0.04), accent)
    cx = size // 2
    sw = int(size * 0.10)
    for y in range(int(size * 0.66), int(size * 0.78) + 1):
        for x in range(cx - sw, cx + sw + 1):
            setpx(x, y, white)
    bx0 = cx - int(size * 0.18); bx1 = cx + int(size * 0.18)
    by0 = int(size * 0.78); by1 = int(size * 0.84)
    roundrect(bx0, by0, bx1, by1, int(size * 0.03), white)
    return buf


def write_png(path, size, buf):
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        raw.extend(buf[y * size * 4:(y + 1) * size * 4])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


for sz in (192, 512):
    write_png(os.path.join(OUT, f"icon-{sz}.png"), sz, make_icon(sz, False))
write_png(os.path.join(OUT, "icon-maskable-512.png"), 512, make_icon(512, True))

with open(os.path.join(OUT, "_done.txt"), "w") as f:
    f.write("ok")
print("icons generated")
