"""icon.ico dosyasını üretir: her boyut ayrı çizilir, küçük boyutlarda çizgiler kalınlaşır."""

import math

from PIL import Image, ImageDraw

INK, RED, YELLOW = "#1c1b1f", "#f2605d", "#ffe066"
SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)


def draw_icon(size, ss=8):
    S = size * ss
    u = S / 64  # 64'lük ızgara birimi
    # küçük boyutlarda kenar ve gölge en az ~1.5 piksel olsun
    border = max(3 * u, 1.5 * ss)
    shadow = max(4 * u, 1.5 * ss)
    pad = 1.5 * u
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = (pad, pad, S - pad - shadow, S - pad - shadow)
    r = 13 * u
    d.rounded_rectangle([v + shadow for v in box], r, fill=INK)
    d.rounded_rectangle(box, r, fill=RED, outline=INK, width=round(border))
    cx = cy = (box[0] + box[2]) / 2
    outer, inner = 21 * u, 8.5 * u
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rad = outer if i % 2 == 0 else inner
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    d.polygon(pts, fill=YELLOW, outline=INK, width=round(max(2 * u, 0.8 * ss)))
    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    images = [draw_icon(s) for s in SIZES]
    images[-1].save("icon.ico", sizes=[(s, s) for s in SIZES], append_images=images[:-1])
    print("icon.ico yazıldı:", ", ".join(map(str, SIZES)))
