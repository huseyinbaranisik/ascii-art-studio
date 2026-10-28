"""Görseli sayı ve sembollerle ASCII art'a çeviren küçük masaüstü uygulaması.

GUI:      python ascii_art.py
Terminal: python ascii_art.py resim.jpg [--renkli] [--genislik 100] [--karakter Karışık]
"""

import argparse
import json
import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageFont
from tkinterdnd2 import DND_FILES, TkinterDnD

import neo_ui as ui

CHARSETS = {
    "Karışık": " .,:;-~+=*!?/\\|()[]{}<>0123456789#%&$@",
    "Sayılar": " 0123456789",
    "Semboller": " .,:;'`^\"-~_+=*!?/\\|()[]{}<>#%&$@",
    "Basit": " .:-=+*#%@",
}
CHAR_ASPECT = 0.5  # karakterler yaklaşık iki kat uzun olduğu için satır sayısını yarıya indir
FONT_FILES = ["consola.ttf", "cour.ttf", "DejaVuSansMono.ttf", "Menlo.ttc"]
BG = "#0c0c0c"
FG = "#cccccc"


def load_mono_font(size):
    for name in FONT_FILES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sort_by_density(chars):
    """Karakterleri mürekkep yoğunluğuna göre (boştan doluya) sıralar."""
    font = load_mono_font(24)

    def ink(ch):
        img = Image.new("L", (24, 32), 0)
        ImageDraw.Draw(img).text((0, 0), ch, font=font, fill=255)
        return sum(img.histogram()[i] * i for i in range(256))

    return "".join(sorted(dict.fromkeys(chars), key=ink))


_ramp_cache = {}


def get_ramp(name):
    if name not in _ramp_cache:
        _ramp_cache[name] = sort_by_density(CHARSETS[name])
    return _ramp_cache[name]


def image_to_cells(img, width, ramp):
    """Görseli (karakter, (r, g, b)) hücrelerinden oluşan satırlara çevirir."""
    img = img.convert("RGB")
    w, h = img.size
    rows = max(1, round(h / w * width * CHAR_ASPECT))
    small = img.resize((width, rows), Image.LANCZOS)
    gray = small.convert("L")
    pixels, lum = small.load(), gray.load()
    last = len(ramp) - 1
    lines = []
    for y in range(rows):
        line = []
        for x in range(width):
            line.append((ramp[lum[x, y] * last // 255], pixels[x, y]))
        lines.append(line)
    return lines


def cells_to_plain(lines):
    return "\n".join("".join(ch for ch, _ in line).rstrip() for line in lines)


def cells_to_ansi(lines):
    """24-bit renk kodlarıyla terminalde renkli görünen metin üretir."""
    out = []
    for line in lines:
        parts, prev = [], None
        for ch, rgb in line:
            if rgb != prev and ch != " ":
                parts.append("\x1b[38;2;%d;%d;%dm" % rgb)
                prev = rgb
            parts.append(ch)
        out.append("".join(parts).rstrip() + "\x1b[0m")
    return "\n".join(out)


def cells_to_png(lines, colored, font_size=14):
    font = load_mono_font(font_size)
    left, top, right, bottom = font.getbbox("@")
    cw = max(1, round(font.getlength("@")))
    ch_h = max(1, bottom + top)
    cols = max((len(line) for line in lines), default=1)
    img = Image.new("RGB", (cols * cw + 20, len(lines) * ch_h + 20), BG)
    draw = ImageDraw.Draw(img)
    for y, line in enumerate(lines):
        py = 10 + y * ch_h
        if colored:
            for x, (ch, rgb) in enumerate(line):
                if ch != " ":
                    draw.text((10 + x * cw, py), ch, font=font, fill=rgb)
        else:
            draw.text((10, py), "".join(c for c, _ in line), font=font, fill=FG)
    return img


def quantize(rgb, step=16):
    return tuple(min(255, (c // step) * step + step // 2) for c in rgb)


SETTINGS_PATH = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                             "ASCII Art Studio", "settings.json")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff")
MIN_FONT_PX, MAX_FONT_PX = 3, 72  # çıktı yazı boyutu sınırları (yakınlaştırma için)


def resource_path(name):
    # exe içinde dosyalar geçici bir klasöre (sys._MEIPASS) açılır
    return os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), name)


def load_settings():
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(data):
    try:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        pass


class App(tk.Tk):
    def __init__(self):
        if os.name == "nt":
            try:  # yüksek DPI ekranlarda bulanık görünmesin
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        super().__init__()
        try:
            TkinterDnD.require(self)
            self._dnd = True
        except Exception:  # tkdnd yüklenemezse sürükle-bırak olmadan devam et
            self._dnd = False
        ui.setup(self)
        self.settings = load_settings()
        self.dark_var = tk.BooleanVar(value=self.settings.get("theme") == "dark")
        ui.set_theme("dark" if self.dark_var.get() else "light")

        self.title("ASCII Art Studio")
        # ekrana sığacak şekilde boyutlandır ve ortala
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(ui.px(900), sw - 40), min(ui.px(580), sh - ui.px(90))
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 2 - ui.px(24))}")
        self.minsize(min(ui.px(760), w), min(ui.px(510), h))
        self._set_icon()

        self.image = None
        self.image_path = None
        self.lines = []
        self._render_job = None
        self._leave_job = None
        self._needs_convert = False
        self._color_tags = set()
        self._frame = None
        self.zoom_px = None  # None: çıktıyı panele sığdır
        self.fit_px = 8

        self.color_mode = tk.StringVar(value="renkli")
        self.width_var = tk.IntVar(value=100)
        self.charset_var = tk.StringVar(value="Karışık")
        self.status_var = tk.StringVar(
            value="Görsel seçin ya da pencereye sürükleyip bırakın" if self._dnd
            else "Başlamak için bir görsel seçin")
        self.status_var.trace_add("write",
                                  lambda *_: self.status_badge.set(self.status_var.get()))

        self._build_ui()

    def _set_icon(self):
        path = resource_path("icon.ico")
        if not os.path.exists(path):
            return
        self.iconbitmap(default=path)
        if os.name != "nt":
            return
        # Tk görev çubuğuna küçük bir ikon verip büyütüyor (bulanık). Windows'un istediği
        # boyutları .ico'dan doğrudan yükleyip pencereye ve pencere sınıfına ata.
        try:
            import ctypes
            u32 = ctypes.windll.user32
            u32.LoadImageW.restype = ctypes.c_void_p
            u32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p,
                                         ctypes.c_void_p]
            u32.SetClassLongPtrW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
            self.update_idletasks()
            hwnd = u32.GetParent(self.winfo_id())
            for which, metric, cls_index in ((1, 11, -14), (0, 49, -34)):  # büyük, küçük
                size = u32.GetSystemMetrics(metric)
                hicon = u32.LoadImageW(None, path, 1, size, size, 0x10)  # IMAGE_ICON, FROMFILE
                if hicon:
                    u32.SendMessageW(hwnd, 0x80, which, hicon)  # WM_SETICON
                    u32.SetClassLongPtrW(hwnd, cls_index, hicon)
        except Exception:
            pass

    def _style_titlebar(self):
        """Windows başlık çubuğunu temaya uydurur (karanlık/aydınlık)."""
        if os.name != "nt":
            return
        try:
            import ctypes
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            value = ctypes.c_int(1 if self.dark_var.get() else 0)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), 4)
            self.wm_attributes("-alpha", 0.99)  # başlık çubuğunu yeniden çizdir
            self.wm_attributes("-alpha", 1.0)
        except Exception:
            pass

    # ---------- arayüz ----------
    def _build_ui(self):
        px, F = ui.px, ui.FONTS
        self.configure(bg=ui.CREAM)
        style = ttk.Style(self)
        style.theme_use("clam")
        for orient in ("Vertical", "Horizontal"):
            style.configure(f"Neo.{orient}.TScrollbar", troughcolor=ui.TERMINAL,
                            background=ui.YELLOW, bordercolor=ui.INK, lightcolor=ui.YELLOW,
                            darkcolor=ui.YELLOW, arrowcolor=ui.INK, gripcount=0,
                            arrowsize=px(12))
            style.map(f"Neo.{orient}.TScrollbar", background=[("active", ui.ORANGE)])

        root = self._frame = tk.Frame(self, bg=ui.CREAM, padx=px(16), pady=px(12))
        root.pack(fill="both", expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        # başlık
        header = tk.Frame(root, bg=ui.CREAM)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, px(12)))
        ui.Button(header, icon="✦", color=ui.RED, width=42, height=42, radius=11,
                  font=F["logo"]).pack(side="left")
        titles = tk.Frame(header, bg=ui.CREAM)
        titles.pack(side="left", padx=px(12))
        tk.Label(titles, text="ASCII Art Studio", font=F["title"], bg=ui.CREAM,
                 fg=ui.TEXT).pack(anchor="w")
        tk.Label(titles, text="Görselleri sayı ve sembollerle terminal sanatına dönüştür",
                 font=F["sub"], bg=ui.CREAM, fg=ui.MUTED).pack(anchor="w")
        ui.Switch(header, "Karanlık", self.dark_var, bg=ui.CREAM,
                  command=self.toggle_theme).pack(side="right")
        ui.Dots(header, [ui.RED, ui.PURPLE, ui.TEAL, ui.YELLOW, ui.ORANGE], bg=ui.CREAM,
                size=14, gap=6).pack(side="right", padx=(0, px(18)))

        # sol kart: görsel + ayarlar (iç genişlik W)
        W = 236
        left = ui.Card(root, width=px(W + 30), height=px(390), radius=14, shadow=6, pad=12)
        left.grid(row=1, column=0, sticky="ns", padx=(0, px(16)))
        body = left.inner

        self.preview = ui.Preview(body, bg=ui.WHITE, width=W, height=138)
        self.preview.pack(anchor="w")
        row = tk.Frame(body, bg=ui.WHITE)
        row.pack(anchor="w", fill="x", pady=(px(10), 0))
        ui.Button(row, "Görsel Seç", self.choose_image, icon="＋", color=ui.RED, bg=ui.WHITE,
                  width=W - 2 * 44, height=38).pack(side="left")
        ui.Button(row, icon="↻", command=lambda: self.rotate(+1), color=ui.YELLOW,
                  bg=ui.WHITE, width=38, height=38, font=F["logo"]).pack(side="right")
        ui.Button(row, icon="↺", command=lambda: self.rotate(-1), color=ui.YELLOW,
                  bg=ui.WHITE, width=38, height=38, font=F["logo"]).pack(side="right", padx=(0, px(6)))

        self._section(body, "GENİŞLİK")
        row = tk.Frame(body, bg=ui.WHITE)
        row.pack(anchor="w", fill="x")
        ui.Slider(row, 20, 250, self.width_var, bg=ui.WHITE, command=self._on_width,
                  width=W - 58, height=30).pack(side="left")
        self.width_badge = ui.Button(row, str(self.width_var.get()), color=ui.YELLOW,
                                     bg=ui.WHITE, width=50, height=28, radius=8, shadow=3,
                                     font=F["small"])
        self.width_badge.pack(side="right")

        self._section(body, "KARAKTERLER")
        ui.ChipGroup(body, [("Karışık", ui.RED), ("Sayılar", ui.PURPLE),
                            ("Semboller", ui.TEAL), ("Basit", ui.YELLOW)],
                     self.charset_var, bg=ui.WHITE, command=self.schedule_render,
                     width=(W - 16) // 2, height=32).pack(anchor="w")

        # sağ taraf: araç çubuğu + terminal çıktısı
        right = tk.Frame(root, bg=ui.CREAM)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        bar = tk.Frame(right, bg=ui.CREAM)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, px(10)))
        ui.Button(bar, "Kopyala", self.copy_text, icon="⧉", color=ui.PURPLE,
                  height=34).pack(side="left")
        ui.Button(bar, "TXT", self.save_txt, icon="⭳", color=ui.TEAL, height=34).pack(
            side="left", padx=px(8))
        ui.Button(bar, "PNG", self.save_png, icon="⭳", color=ui.ORANGE, height=34).pack(
            side="left")
        ui.Segmented(bar, [("Renkli", "renkli"), ("Renksiz", "renksiz")], self.color_mode,
                     bg=ui.CREAM, command=self.show_output, height=34).pack(side="right")

        card = ui.Card(right, width=px(440), height=px(340), radius=14, shadow=6, pad=10)
        card.grid(row=1, column=0, sticky="nsew")
        inner = card.inner
        inner.columnconfigure(0, weight=1)
        inner.rowconfigure(1, weight=1)

        head = tk.Frame(inner, bg=ui.WHITE)
        head.grid(row=0, column=0, sticky="ew", pady=(0, px(8)))
        ui.Dots(head, [ui.RED, ui.YELLOW, ui.TEAL], bg=ui.WHITE, size=11, gap=5).pack(
            side="left")
        tk.Label(head, text="terminal", font=F["mono"], bg=ui.WHITE, fg=ui.TEXT).pack(
            side="left", padx=px(8))
        self.info_badge = ui.Button(head, "—", color=ui.PINK, bg=ui.WHITE, height=24,
                                    radius=12, shadow=3, font=F["label"])
        self.info_badge.pack(side="right")
        # yakınlaştırma: −  %100  +  ⤢(sığdır)
        zoom = dict(bg=ui.WHITE, width=28, height=26, radius=7, shadow=3, font=F["button"])
        ui.Button(head, icon="⤢", command=self.zoom_fit, color=ui.TEAL, **zoom).pack(
            side="right", padx=(0, px(12)))
        ui.Button(head, "+", lambda: self.zoom(+1), color=ui.YELLOW, **zoom).pack(
            side="right", padx=(0, px(6)))
        self.zoom_badge = ui.Button(head, "Sığdır", bg=ui.WHITE, height=24, radius=7,
                                    shadow=3, font=F["label"])
        self.zoom_badge.pack(side="right", padx=(0, px(6)))
        ui.Button(head, "−", lambda: self.zoom(-1), color=ui.YELLOW, **zoom).pack(
            side="right", padx=(0, px(6)))

        term = tk.Frame(inner, bg=ui.INK, padx=px(2), pady=px(2))
        term.grid(row=1, column=0, sticky="nsew")
        term.rowconfigure(0, weight=1)
        term.columnconfigure(0, weight=1)
        self.out_font = tkfont.Font(family="Consolas", size=7)
        self.text = tk.Text(term, bg=ui.TERMINAL, fg=FG, font=self.out_font, wrap="none",
                            relief="flat", borderwidth=px(6), insertbackground=FG,
                            selectbackground=ui.PURPLE, width=1, height=1)
        self.text.grid(row=0, column=0, sticky="nsew")
        ys = ttk.Scrollbar(term, orient="vertical", command=self.text.yview,
                           style="Neo.Vertical.TScrollbar")
        xs = ttk.Scrollbar(term, orient="horizontal", command=self.text.xview,
                           style="Neo.Horizontal.TScrollbar")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        self.text.configure(yscrollcommand=ys.set, xscrollcommand=xs.set, state="disabled")
        self.text.bind("<Configure>", lambda e: self.schedule_render(fit_only=True))
        # Ctrl+tekerlek yakınlaştırır, sol tuşla tutup sürüklemek görüntüyü kaydırır
        self.text.bind("<Control-MouseWheel>", lambda e: (self.zoom(1 if e.delta > 0 else -1),
                                                          "break")[1])
        self.text.bind("<Shift-MouseWheel>", lambda e: (
            self.text.xview_scroll(-1 if e.delta > 0 else 1, "units"), "break")[1])
        self.text.bind("<ButtonPress-1>", lambda e: (self.text.scan_mark(e.x, e.y), "break")[1])
        self.text.bind("<B1-Motion>", lambda e: (self.text.scan_dragto(e.x, e.y, gain=1),
                                                 "break")[1])
        self.text.configure(cursor="fleur")
        self._color_tags.clear()

        # durum rozeti
        self.status_badge = ui.Button(root, self.status_var.get(), color=ui.YELLOW,
                                      height=26, radius=13, shadow=3, font=F["label"])
        self.status_badge.grid(row=2, column=0, columnspan=2, sticky="w", pady=(px(10), 0))

        if self._dnd:
            self._register_drop(root)
        self._style_titlebar()
        if self.image is not None:
            self.preview.show(self.image)

    def _section(self, parent, text):
        tk.Label(parent, text=text, font=ui.FONTS["label"], bg=ui.WHITE, fg=ui.MUTED).pack(
            anchor="w", pady=(ui.px(12), ui.px(5)))

    def toggle_theme(self):
        dark = self.dark_var.get()
        ui.set_theme("dark" if dark else "light")
        self.settings["theme"] = "dark" if dark else "light"
        save_settings(self.settings)
        self._frame.destroy()
        self._build_ui()

    # ---------- sürükle-bırak ----------
    def _register_drop(self, widget):
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<DropEnter>>", self._drop_enter)
        widget.dnd_bind("<<DropLeave>>", self._drop_leave)
        widget.dnd_bind("<<Drop>>", self._drop)
        for child in widget.winfo_children():
            self._register_drop(child)

    def _drop_enter(self, e):
        # alt widget'lar arasında gezerken leave/enter art arda gelir; titremesin
        if self._leave_job:
            self.after_cancel(self._leave_job)
            self._leave_job = None
        self.preview.set_drop_hover(True)
        return e.action

    def _drop_leave(self, e):
        self._leave_job = self.after(80, lambda: self.preview.set_drop_hover(False))
        return e.action

    def _drop(self, e):
        self._drop_leave(e)
        paths = self.tk.splitlist(e.data)
        path = next((p for p in paths if p.lower().endswith(IMAGE_EXTS)),
                    paths[0] if paths else None)
        if path:
            self.load_image(path)
        return e.action

    # ---------- olaylar ----------
    def _on_width(self):
        self.width_badge.set(str(self.width_var.get()))
        self.schedule_render()

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Görsel seç",
            filetypes=[("Görseller", " ".join("*" + e for e in IMAGE_EXTS)),
                       ("Tüm dosyalar", "*.*")])
        if path:
            self.load_image(path)

    def load_image(self, path):
        try:
            img = Image.open(path)
            img.load()
        except Exception as exc:
            messagebox.showerror("Hata", f"Görsel açılamadı:\n{exc}")
            return
        self.image, self.image_path = img, path
        self.zoom_px = None  # yeni görsel sığdırılarak açılır
        self.preview.show(img)
        self.schedule_render()

    def rotate(self, direction):
        """direction: -1 sola (saat yönünün tersi), +1 sağa 90° döndürür."""
        if self.image is None:
            self.status_var.set("Döndürmek için önce bir görsel seçin")
            return
        t = Image.Transpose.ROTATE_90 if direction < 0 else Image.Transpose.ROTATE_270
        self.image = self.image.transpose(t)
        self.preview.show(self.image)
        self.schedule_render()

    def schedule_render(self, fit_only=False):
        if self._render_job:
            self.after_cancel(self._render_job)
        # bekleyen tam dönüşüm, sadece yeniden boyutlandırma yüzünden iptal olmasın
        self._needs_convert = self._needs_convert or not fit_only
        action = self.render if self._needs_convert else self.show_output
        self._render_job = self.after(120, action)

    def render(self):
        self._render_job = None
        self._needs_convert = False
        if self.image is None:
            return
        self.lines = image_to_cells(self.image, self.width_var.get(),
                                    get_ramp(self.charset_var.get()))
        self.show_output()

    def _fit_font(self, cols, rows):
        """Çıktının tamamı panele sığacak en büyük yazı boyutunu (piksel) bulur ve uygular;
        yakınlaştırma açıksa onun boyutunu kullanır."""
        pad = 2 * int(self.text.cget("borderwidth")) + 4
        avail_w = self.text.winfo_width() - pad
        avail_h = self.text.winfo_height() - pad
        fit = MIN_FONT_PX
        for s in range(MIN_FONT_PX, MAX_FONT_PX + 1):
            self.out_font.configure(size=-s)  # negatif boyut = piksel
            if (self.out_font.measure("@") * cols <= avail_w
                    and self.out_font.metrics("linespace") * rows <= avail_h):
                fit = s
            else:
                break
        self.fit_px = fit
        self.out_font.configure(size=-(self.zoom_px or fit))
        self._update_zoom_badge()

    def _update_zoom_badge(self):
        if self.zoom_px is None:
            self.zoom_badge.set("Sığdır")
        else:
            self.zoom_badge.set(f"%{round(self.zoom_px / self.fit_px * 100)}")

    def zoom(self, direction):
        """direction: +1 yakınlaştır, -1 uzaklaştır. Görünümün ortası yerinde kalır."""
        if not self.lines:
            return
        cur = self.zoom_px or self.fit_px
        if direction > 0:
            new = max(cur + 1, round(cur * 1.2))
        else:
            new = min(cur - 1, round(cur / 1.2))
        new = max(MIN_FONT_PX, min(MAX_FONT_PX, new))
        if new == cur:
            return
        t = self.text
        cx, cy = sum(t.xview()) / 2, sum(t.yview()) / 2
        self.zoom_px = new
        self.out_font.configure(size=-new)
        self._update_zoom_badge()
        t.update_idletasks()
        x0, x1 = t.xview()
        y0, y1 = t.yview()
        t.xview_moveto(cx - (x1 - x0) / 2)
        t.yview_moveto(cy - (y1 - y0) / 2)

    def zoom_fit(self):
        self.zoom_px = None
        self.out_font.configure(size=-self.fit_px)
        self._update_zoom_badge()
        self.text.xview_moveto(0)
        self.text.yview_moveto(0)

    def show_output(self):
        self._render_job = None
        if not self.lines:
            return
        cols = len(self.lines[0])
        self._fit_font(cols, len(self.lines))
        colored = self.color_mode.get() == "renkli"

        t = self.text
        t.configure(state="normal")
        t.delete("1.0", "end")
        if colored:
            args = []
            for line in self.lines:
                run, run_tag = [], None
                for ch, rgb in line:
                    tag = "c%02x%02x%02x" % quantize(rgb)
                    if tag != run_tag and run:
                        args += ["".join(run), run_tag]
                        run = []
                    run_tag = tag
                    run.append(ch)
                    if tag not in self._color_tags:
                        t.tag_configure(tag, foreground="#" + tag[1:])
                        self._color_tags.add(tag)
                if run:
                    args += ["".join(run), run_tag]
                args += ["\n", ()]
            t.insert("end", *args)
        else:
            t.insert("end", cells_to_plain(self.lines))
        t.configure(state="disabled")

        self.info_badge.set(f"{cols} × {len(self.lines)}")
        self.status_var.set(f"✓  {os.path.basename(self.image_path)} dönüştürüldü · "
                            f"{'renkli' if colored else 'renksiz'}")

    # ---------- dışa aktarma ----------
    def _need_output(self):
        if not self.lines:
            messagebox.showinfo("Bilgi", "Önce bir görsel seçin.")
            return False
        return True

    def _default_name(self, ext):
        base = os.path.splitext(os.path.basename(self.image_path))[0]
        return f"{base}_ascii{ext}"

    def copy_text(self):
        if not self._need_output():
            return
        self.clipboard_clear()
        self.clipboard_append(cells_to_plain(self.lines))
        self.status_var.set("✓  Metin panoya kopyalandı")

    def save_txt(self):
        if not self._need_output():
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            initialfile=self._default_name(".txt"),
                                            filetypes=[("Metin dosyası", "*.txt")])
        if not path:
            return
        colored = self.color_mode.get() == "renkli"
        content = cells_to_ansi(self.lines) if colored else cells_to_plain(self.lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        hint = "  ·  renkli görmek için terminalde: type / cat" if colored else ""
        self.status_var.set(f"✓  Kaydedildi: {os.path.basename(path)}{hint}")

    def save_png(self):
        if not self._need_output():
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            initialfile=self._default_name(".png"),
                                            filetypes=[("PNG görseli", "*.png")])
        if not path:
            return
        cells_to_png(self.lines, self.color_mode.get() == "renkli").save(path)
        self.status_var.set(f"✓  Kaydedildi: {os.path.basename(path)}")


def main():
    parser = argparse.ArgumentParser(description="Görseli ASCII art'a çevirir.")
    parser.add_argument("gorsel", nargs="?", help="verilirse sonuç terminale yazdırılır")
    parser.add_argument("--renkli", action="store_true", help="24-bit renkli çıktı")
    parser.add_argument("--genislik", type=int, default=100)
    parser.add_argument("--karakter", choices=list(CHARSETS), default="Karışık")
    args = parser.parse_args()

    if args.gorsel is None or sys.stdout is None:  # konsolsuz exe'de terminal modu yok
        App().mainloop()
        return

    if os.name == "nt":
        os.system("")  # Windows konsolunda ANSI renk kodlarını etkinleştirir
    sys.stdout.reconfigure(encoding="utf-8")
    lines = image_to_cells(Image.open(args.gorsel), args.genislik,
                           get_ramp(args.karakter))
    print(cells_to_ansi(lines) if args.renkli else cells_to_plain(lines))


if __name__ == "__main__":
    main()
