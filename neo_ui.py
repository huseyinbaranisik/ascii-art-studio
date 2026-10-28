"""Tkinter için küçük bir Neo Brutalism bileşen seti.

Kalın siyah kenarlar, sert (bulanıksız) gölgeler ve canlı renkler. Şekiller Pillow ile
3 kat büyük çizilip küçültülerek yumuşak kenarlı (antialiased) görüntüler olarak basılır.
"""

import tkinter as tk
import tkinter.font as tkfont

from PIL import Image, ImageDraw, ImageTk

THEMES = {
    # CREAM: zemin, WHITE: kart yüzeyi, INK: kenar/gölge (ve renkli butonlardaki yazı),
    # TEXT: yüzey üzerindeki yazı, PAPER: ikincil yüzey
    "light": dict(CREAM="#fbf1e8", WHITE="#fffdf9", INK="#1c1b1f", TEXT="#1c1b1f",
                  MUTED="#6e6861", PAPER="#f4e9df"),
    "dark": dict(CREAM="#26232d", WHITE="#33303b", INK="#060508", TEXT="#f6efe6",
                 MUTED="#a59eb0", PAPER="#3f3a49"),
}
CREAM, WHITE, INK, TEXT, MUTED, PAPER = (THEMES["light"][k] for k in
                                         ("CREAM", "WHITE", "INK", "TEXT", "MUTED", "PAPER"))
LIGHT = "#fffdf9"  # temadan bağımsız açık renk (topuzlar)
RED = "#f2605d"
PURPLE = "#9d80ef"
TEAL = "#3fc5b4"
YELLOW = "#ffe066"
ORANGE = "#f5a066"
PINK = "#ffcbc2"
TERMINAL = "#1f1d24"

SCALE = 1.0
FONTS = {}
_cache = {}


def set_theme(name):
    globals().update(THEMES[name])


def _watch(widget, variable, callback):
    """Değişkeni izler; widget yok edilince izlemeyi bırakır (tema değişiminde UI yeniden kurulur)."""
    tid = variable.trace_add("write", lambda *_: callback())
    widget.bind("<Destroy>", lambda e: e.widget is widget and variable.trace_remove("write", tid),
                add="+")


def px(v):
    return max(1, round(v * SCALE))


def setup(root):
    """Ekran ölçeğini ve yazı tiplerini hazırlar; widget'lardan önce çağrılmalı."""
    global SCALE
    SCALE = float(root.tk.call("tk", "scaling")) / (96 / 72)
    families = set(tkfont.families(root))

    def pick(*names):
        return next((n for n in names if n in families), "Segoe UI")

    bold = pick("Bahnschrift SemiBold", "Segoe UI Semibold")
    regular = pick("Bahnschrift", "Segoe UI")
    FONTS.update(
        title=tkfont.Font(root, family=bold, size=17),
        sub=tkfont.Font(root, family=regular, size=9),
        button=tkfont.Font(root, family=bold, size=10),
        small=tkfont.Font(root, family=bold, size=9),
        label=tkfont.Font(root, family=bold, size=8),
        body=tkfont.Font(root, family=regular, size=10),
        icon=tkfont.Font(root, family="Segoe UI Symbol", size=11),
        logo=tkfont.Font(root, family="Segoe UI Symbol", size=15),
        mono=tkfont.Font(root, family="Consolas", size=9, weight="bold"),
    )


# ---------- çizim yardımcıları ----------

def _rr(draw, box, r, ss, **kw):
    x1, y1, x2, y2 = box
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    draw.rounded_rectangle([v * ss for v in box], radius=r * ss, **kw)


def _clip_fill(img, box, r, ss, x_from, x_to, color):
    """Yuvarlak kutunun yalnızca [x_from, x_to] aralığını boyar."""
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    _rr(md, box, r, ss, fill=255)
    md.rectangle([0, 0, x_from * ss, img.height], fill=0)
    md.rectangle([x_to * ss, 0, img.width, img.height], fill=0)
    img.paste(color, mask=mask)


def _finish(img, w, h):
    return ImageTk.PhotoImage(img.resize((w, h), Image.LANCZOS))


def _cached(key, make, cache=True):
    if not cache:
        return make()
    if key not in _cache:
        _cache[key] = make()
    return _cache[key]


def neo_box(w, h, fill, bg, r, border, shadow, off=0, cache=True, ss=3):
    """Gölgeli, kenarlıklı kutu. off: gövdenin gölgeye doğru kayması (basılma efekti)."""
    def make():
        img = Image.new("RGB", (w * ss, h * ss), bg)
        d = ImageDraw.Draw(img)
        bw, bh = w - shadow - 1, h - shadow - 1
        if shadow and off < shadow:
            _rr(d, (shadow, shadow, bw + shadow, bh + shadow), r, ss, fill=INK)
        _rr(d, (off, off, bw + off, bh + off), r, ss, fill=fill, outline=INK, width=border * ss)
        return _finish(img, w, h)
    return _cached(("box", w, h, fill, bg, r, border, shadow, off), make, cache)


def neo_segments(w, h, splits, active, fill, active_fill, bg, r, border, shadow, ss=3):
    def make():
        img = Image.new("RGB", (w * ss, h * ss), bg)
        d = ImageDraw.Draw(img)
        box = (0, 0, w - shadow - 1, h - shadow - 1)
        _rr(d, tuple(v + shadow for v in box), r, ss, fill=INK)
        _rr(d, box, r, ss, fill=fill)
        _clip_fill(img, box, r, ss, splits[active], splits[active + 1], active_fill)
        d = ImageDraw.Draw(img)
        for x in splits[1:-1]:
            d.line([(x * ss, 0), (x * ss, box[3] * ss)], fill=INK, width=border * ss)
        _rr(d, box, r, ss, outline=INK, width=border * ss)
        return _finish(img, w, h)
    return _cached(("seg", w, h, tuple(splits), active, fill, active_fill, bg), make)


def slider_geometry(w, h, shadow):
    """Kaydırıcının topuz çapı ve topuz merkezinin gidebileceği x aralığı."""
    kd = h - shadow - 1
    return kd, kd / 2, w - shadow - 1 - kd / 2


def neo_slider(w, h, frac, color, bg, border, shadow, pressed=False, ss=3):
    """İnce dolum çubuğu + üzerinde sürüklenebilen yuvarlak topuz."""
    def make():
        img = Image.new("RGB", (w * ss, h * ss), bg)
        d = ImageDraw.Draw(img)
        kd, x_min, x_max = slider_geometry(w, h, shadow)
        cy = kd / 2
        th = kd * 0.6
        box = (0, cy - th / 2, w - shadow - 1, cy + th / 2)
        r = th / 2
        _rr(d, (box[0] + shadow, box[1] + shadow, box[2] + shadow, box[3] + shadow), r, ss,
            fill=INK)
        _rr(d, box, r, ss, fill=WHITE)
        cx = x_min + frac * (x_max - x_min)
        _clip_fill(img, box, r, ss, 0, cx, color)
        d = ImageDraw.Draw(img)
        _rr(d, box, r, ss, outline=INK, width=border * ss)
        # topuz: basılıyken gölgesine doğru kayar
        off = shadow if pressed else 0
        if not pressed:
            d.ellipse([(cx - kd / 2 + shadow) * ss, shadow * ss, (cx + kd / 2 + shadow) * ss,
                       (kd + shadow) * ss], fill=INK)
        d.ellipse([(cx - kd / 2 + off) * ss, off * ss, (cx + kd / 2 + off) * ss,
                   (kd + off) * ss], fill=YELLOW if pressed else LIGHT, outline=INK,
                  width=border * ss)
        dot = kd * 0.16
        d.ellipse([(cx - dot + off) * ss, (cy - dot + off) * ss, (cx + dot + off) * ss,
                   (cy + dot + off) * ss], fill=INK)
        return _finish(img, w, h)
    return _cached(("slider", w, h, round(frac, 3), color, bg, pressed), make)


def neo_switch(w, h, on, bg, border, shadow, ss=3):
    def make():
        img = Image.new("RGB", (w * ss, h * ss), bg)
        d = ImageDraw.Draw(img)
        box = (0, 0, w - shadow - 1, h - shadow - 1)
        r = box[3] / 2
        _rr(d, tuple(v + shadow for v in box), r, ss, fill=INK)
        _rr(d, box, r, ss, fill=TEAL if on else WHITE, outline=INK, width=border * ss)
        m = border + 3
        k = box[3] - 2 * m
        kx = box[2] - m - k if on else m
        d.ellipse([kx * ss, m * ss, (kx + k) * ss, (m + k) * ss],
                  fill=LIGHT if on else PAPER, outline=INK, width=border * ss)
        return _finish(img, w, h)
    return _cached(("sw", w, h, on, bg), make)


def neo_dots(colors, size, gap, bg, border, ss=3):
    def make():
        w = len(colors) * size + (len(colors) - 1) * gap + 1
        img = Image.new("RGB", (w * ss, (size + 1) * ss), bg)
        d = ImageDraw.Draw(img)
        for i, c in enumerate(colors):
            x = i * (size + gap)
            d.ellipse([x * ss, 0, (x + size) * ss, size * ss], fill=c, outline=INK,
                      width=border * ss)
        return _finish(img, w, size + 1)
    return _cached(("dots", tuple(colors), size, gap, bg), make)


# ---------- bileşenler ----------

class _Canvas(tk.Canvas):
    def __init__(self, parent, bg, **kw):
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0, **kw)
        self.bg = bg


class Card(_Canvas):
    """İçine widget konabilen gölgeli kart. İçerik: card.inner"""

    def __init__(self, parent, fill=None, bg=None, radius=18, shadow=7, pad=16, **kw):
        fill, bg = fill or WHITE, bg or CREAM
        super().__init__(parent, bg, **kw)
        self.fill, self.radius = fill, px(radius)
        self.shadow, self.pad = px(shadow), px(pad)
        self.inner = tk.Frame(self, bg=fill)
        self._img = self.create_image(0, 0, anchor="nw")
        self._win = self.create_window(self.pad, self.pad, anchor="nw", window=self.inner)
        self.bind("<Configure>", self._redraw)

    def _redraw(self, e):
        if e.width < 40 or e.height < 40:
            return
        self._photo = neo_box(e.width, e.height, self.fill, self.bg, self.radius, px(2.5),
                              self.shadow, cache=False, ss=2)
        self.itemconfigure(self._img, image=self._photo)
        self.itemconfigure(self._win, width=e.width - self.shadow - 2 * self.pad,
                           height=e.height - self.shadow - 2 * self.pad)


class Button(_Canvas):
    """Basınca gölgesine doğru kayan buton. command=None ise rozet (badge) gibi davranır."""

    def __init__(self, parent, text="", command=None, color=None, bg=None, width=None,
                 height=40, icon=None, font=None, radius=10, shadow=4, text_color=None):
        color, bg = color or WHITE, bg or CREAM
        self.text, self.icon, self.color, self.command = text, icon, color, command
        self.font = font or FONTS["button"]
        self.icon_font = FONTS["logo"] if font is FONTS.get("logo") else FONTS["icon"]
        self.text_color = text_color
        self.r, self.shadow, self.h = px(radius), px(shadow), px(height)
        self.auto_width = width is None
        self.w = self._measure() if self.auto_width else px(width)
        super().__init__(parent, bg, width=self.w, height=self.h,
                         cursor="hand2" if command else "")
        self._hover = self._pressed = False
        if command:
            self.bind("<Enter>", lambda e: self._set(hover=True))
            self.bind("<Leave>", lambda e: self._set(hover=False, pressed=False))
            self.bind("<ButtonPress-1>", lambda e: self._set(pressed=True))
            self.bind("<ButtonRelease-1>", self._release)
        self.draw()

    def _measure(self):
        w = self.font.measure(self.text)
        if self.icon:
            w += FONTS["icon"].measure(self.icon) + (px(8) if self.text else 0)
        return w + px(36) + self.shadow

    def _set(self, hover=None, pressed=None):
        if hover is not None:
            self._hover = hover
        if pressed is not None:
            self._pressed = pressed
        self.draw()

    def _release(self, e):
        inside = 0 <= e.x < self.w and 0 <= e.y < self.h
        fire = self._pressed and inside
        self._set(pressed=False)
        if fire:
            self.command()

    def set(self, text=None, color=None):
        if text is not None:
            self.text = text
        if color is not None:
            self.color = color
        if self.auto_width:
            self.w = self._measure()
            self.configure(width=self.w)
        self.draw()

    def draw(self):
        self.delete("all")
        off = self.shadow if self._pressed else (px(1) if self._hover else 0)
        fg = self.text_color or (TEXT if self.color == WHITE else INK)
        self._photo = neo_box(self.w, self.h, self.color, self.bg, self.r, px(2), self.shadow, off)
        self.create_image(0, 0, anchor="nw", image=self._photo)
        cx = (self.w - self.shadow) / 2 + off
        cy = (self.h - self.shadow) / 2 + off
        if not self.icon:
            self.create_text(cx, cy, text=self.text, font=self.font, fill=fg)
            return
        iw = self.icon_font.measure(self.icon)
        gap = px(8) if self.text else 0
        x = cx - (iw + gap + self.font.measure(self.text)) / 2
        self.create_text(x, cy, text=self.icon, font=self.icon_font, fill=fg,
                         anchor="w")
        if self.text:
            self.create_text(x + iw + gap, cy, text=self.text, font=self.font,
                             fill=fg, anchor="w")


class ChipGroup(tk.Frame):
    """Hap şeklinde seçim çipleri (radio grubu). Seçili çip kendi rengine boyanır."""

    def __init__(self, parent, options, variable, bg, command=None, columns=2, width=140,
                 height=36):
        super().__init__(parent, bg=bg)
        self.variable, self.command, self.chips = variable, command, {}
        for i, (value, color) in enumerate(options):
            chip = Button(self, value, lambda v=value: self._pick(v), bg=bg, width=width,
                          height=height, radius=height // 2, shadow=3,
                          font=FONTS["small"])
            chip.grid(row=i // columns, column=i % columns, padx=(0, px(8)), pady=(0, px(8)),
                      sticky="w")
            self.chips[value] = (chip, color)
        _watch(self, variable, self._refresh)
        self._refresh()

    def _pick(self, value):
        self.variable.set(value)
        if self.command:
            self.command()

    def _refresh(self):
        for value, (chip, color) in self.chips.items():
            chip.set(color=color if value == self.variable.get() else WHITE)


class Segmented(_Canvas):
    """'Tab 1 | Tab 2' görünümlü radio grubu."""

    def __init__(self, parent, options, variable, bg, command=None, height=40,
                 active_fill=YELLOW):
        self.options, self.variable, self.command = options, variable, command
        self.active_fill, self.shadow, self.h = active_fill, px(4), px(height)
        font = FONTS["button"]
        self.splits = [0]
        for label, _ in options:
            self.splits.append(self.splits[-1] + font.measure(label) + px(36))
        self.w = self.splits[-1] + self.shadow + 1
        self.splits[-1] = self.w - self.shadow - 1
        super().__init__(parent, bg, width=self.w, height=self.h, cursor="hand2")
        self.bind("<Button-1>", self._click)
        _watch(self, variable, self.draw)
        self.draw()

    def _click(self, e):
        for i in range(len(self.options)):
            if self.splits[i] <= e.x < self.splits[i + 1]:
                self.variable.set(self.options[i][1])
                if self.command:
                    self.command()

    def draw(self):
        self.delete("all")
        values = [v for _, v in self.options]
        active = values.index(self.variable.get())
        self._photo = neo_segments(self.w, self.h, self.splits, active, WHITE,
                                   self.active_fill, self.bg, px(10), px(2), self.shadow)
        self.create_image(0, 0, anchor="nw", image=self._photo)
        cy = (self.h - self.shadow) / 2
        for i, (label, _) in enumerate(self.options):
            cx = (self.splits[i] + self.splits[i + 1]) / 2
            self.create_text(cx, cy, text=label, font=FONTS["button"],
                             fill=INK if i == active else TEXT)


class Switch(_Canvas):
    """Açık/kapalı anahtarı ve yanındaki etiket."""

    def __init__(self, parent, text, variable, bg, command=None):
        self.text, self.variable, self.command = text, variable, command
        self.sw, self.h, self.shadow = px(54), px(30), px(3)
        self.w = self.sw + px(12) + FONTS["small"].measure(text) + 2
        super().__init__(parent, bg, width=self.w, height=self.h, cursor="hand2")
        self.bind("<Button-1>", self._toggle)
        _watch(self, variable, self.draw)
        self.draw()

    def _toggle(self, _e):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()

    def draw(self):
        self.delete("all")
        self._photo = neo_switch(self.sw, self.h, bool(self.variable.get()), self.bg, px(2),
                                 self.shadow)
        self.create_image(0, 0, anchor="nw", image=self._photo)
        self.create_text(self.sw + px(12), (self.h - self.shadow) / 2, text=self.text,
                         font=FONTS["small"], fill=TEXT, anchor="w")


class Slider(_Canvas):
    """Yuvarlak topuzu tutup sürüklenen kaydırıcı. Çubuğa tıklamak da topuzu oraya taşır."""

    def __init__(self, parent, from_, to, variable, bg, command=None, width=200, height=34,
                 color=TEAL):
        self.from_, self.to, self.variable, self.command = from_, to, variable, command
        self.w, self.h, self.color, self.shadow = px(width), px(height), color, px(3)
        super().__init__(parent, bg, width=self.w, height=self.h, cursor="hand2")
        self._pressed = False
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)
        _watch(self, variable, self.draw)
        self.draw()

    def _press(self, e):
        self._pressed = True
        self.configure(cursor="sb_h_double_arrow")
        self._drag(e)
        self.draw()

    def _release(self, _e):
        self._pressed = False
        self.configure(cursor="hand2")
        self.draw()

    def _drag(self, e):
        _, x_min, x_max = slider_geometry(self.w, self.h, self.shadow)
        frac = min(1, max(0, (e.x - x_min) / (x_max - x_min)))
        value = round(self.from_ + frac * (self.to - self.from_))
        if value != self.variable.get():
            self.variable.set(value)
            if self.command:
                self.command()

    def draw(self):
        self.delete("all")
        frac = (self.variable.get() - self.from_) / (self.to - self.from_)
        self._photo = neo_slider(self.w, self.h, frac, self.color, self.bg, px(2), self.shadow,
                                 self._pressed)
        self.create_image(0, 0, anchor="nw", image=self._photo)


class Dots(_Canvas):
    def __init__(self, parent, colors, bg, size=22, gap=8):
        self._photo = neo_dots(colors, px(size), px(gap), bg, px(2))
        super().__init__(parent, bg, width=self._photo.width(), height=self._photo.height())
        self.create_image(0, 0, anchor="nw", image=self._photo)


class Preview(_Canvas):
    """Seçilen görselin önizleme kutusu."""

    def __init__(self, parent, bg, width=290, height=210):
        self.w, self.h, self.shadow = px(width), px(height), px(4)
        super().__init__(parent, bg, width=self.w, height=self.h)
        self._thumb = self._image = None
        self._drop_hover = False
        self.show(None)

    def set_drop_hover(self, on):
        """Dosya kutunun üzerine sürüklenirken vurgula."""
        if on != self._drop_hover:
            self._drop_hover = on
            self.show(self._image)

    def show(self, pil_image):
        self._image = pil_image
        self.delete("all")
        fill = YELLOW if self._drop_hover else PAPER
        self._photo = neo_box(self.w, self.h, fill, self.bg, px(14), px(2), self.shadow)
        self.create_image(0, 0, anchor="nw", image=self._photo)
        cx, cy = (self.w - self.shadow) / 2, (self.h - self.shadow) / 2
        if self._drop_hover:
            self.create_text(cx, cy - px(14), text="⭳", font=FONTS["logo"], fill=INK)
            self.create_text(cx, cy + px(18), text="Bırak, dönüştürelim!",
                             font=FONTS["button"], fill=INK)
            return
        if pil_image is None:
            self.create_text(cx, cy - px(16), text="⭳", font=FONTS["logo"], fill=MUTED)
            self.create_text(cx, cy + px(14), text="Görseli buraya sürükle",
                             font=FONTS["small"], fill=TEXT)
            self.create_text(cx, cy + px(34), text="ya da Görsel Seç'e tıkla",
                             font=FONTS["label"], fill=MUTED)
            return
        thumb = pil_image.convert("RGB")
        thumb.thumbnail((self.w - self.shadow - px(28), self.h - self.shadow - px(28)))
        self._thumb = ImageTk.PhotoImage(thumb)
        self.create_image(cx, cy, image=self._thumb)
        hw, hh = thumb.width / 2, thumb.height / 2
        self.create_rectangle(cx - hw - 1, cy - hh - 1, cx + hw, cy + hh, outline=INK,
                              width=px(2))
