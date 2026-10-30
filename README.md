<div align="center">

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Artist%20Palette.png" width="110" alt="Artist Palette">

# ASCII Art Studio

<img src="https://readme-typing-svg.demolab.com?font=Space+Grotesk&weight=700&size=22&duration=2600&pause=700&color=F25C54&center=true&vCenter=true&width=600&lines=Turn%20images%20into%20ASCII%20art;Numbers%20%26%20symbols%20%C2%B7%20colour%20or%20mono;Export%20to%20TXT%2C%20PNG%20or%20clipboard" alt="Turn images into ASCII art">

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/UI-Tkinter-1F1F1F?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Windows-.exe%20release-0078D6?style=for-the-badge&logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/style-Neo%20Brutalism-FFD966?style=for-the-badge" />
</p>

<a href="#-english"><b>🇬🇧 English</b></a> · <a href="#-türkçe"><b>🇹🇷 Türkçe</b></a>

</div>

<br>

<table align="center">
  <tr>
    <td align="center" width="25%"><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Framed%20Picture.png" width="40" alt="Framed Picture"><br><b>Drag & drop</b><br><sub>any image</sub></td>
    <td align="center" width="25%"><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Symbols/Input%20Numbers.png" width="40" alt="Input Numbers"><br><b>Character sets</b><br><sub>4 styles</sub></td>
    <td align="center" width="25%"><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Artist%20Palette.png" width="40" alt="Artist Palette"><br><b>Colour</b><br><sub>24-bit ANSI</sub></td>
    <td align="center" width="25%"><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Floppy%20Disk.png" width="40" alt="Floppy Disk"><br><b>Export</b><br><sub>TXT · PNG · copy</sub></td>
  </tr>
</table>

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Clapper%20Board.png" width="32" align="center"> Demo

<div align="center">
  <img src="docs/ekran-aydinlik.png" width="49%" alt="Light theme"> <img src="docs/ekran-karanlik.png" width="49%" alt="Dark theme, zoomed output"><br><sub>Light theme · dark theme with zoomed output</sub>
</div>

---

## 🇬🇧 English

A small Neo Brutalism-style desktop app that turns images into colour or monochrome ASCII art made of **numbers and symbols**. You can copy the result to the clipboard, or save it as a `.txt` file that shows in colour in the terminal, or as a `.png` image.

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Sparkles.png" width="26" align="center"> Features

| | |
| :--- | :--- |
| 🖱️ **Drag and drop** | Drop an image onto the window, or use the **Görsel Seç** (Choose Image) button |
| 🔄 **Rotate** | Turn the image 90° left or right with ↺ / ↻ |
| 📏 **Width** | Pick the output width (20–250 characters) with the knob slider |
| 🔤 **Character sets** | Mixed, Numbers, Symbols and Simple — characters are auto-sorted by how filled they look on screen |
| 🎨 **Colour / mono** | Colour or monochrome output |
| 🔍 **Zoom & pan** | −/+ buttons or Ctrl + wheel; drag to move around, ⤢ fits the view to the panel |
| 💾 **Export** | **Copy** plain text · **TXT** with 24-bit ANSI colours (open with `type` / `cat` to see it in colour) · **PNG** image |
| 🌙 **Dark theme** | Your choice is remembered next time |
| 💻 **Terminal mode** | Print the result straight to the terminal without opening a window |

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Rocket.png" width="26" align="center"> Installation

**Ready-made exe (Windows):** download `ASCII.Art.Studio.exe` from the [Releases](https://github.com/huseyinbaranisik/ascii-art-studio/releases/latest) page and double-click it — no Python needed.

> Windows SmartScreen may warn about unsigned apps. If so, click **More info → Run anyway**.

**From source** (Python 3.10+):

```bash
pip install -r requirements.txt
python ascii_art.py
```

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Laptop.png" width="26" align="center"> Terminal mode

```bash
python ascii_art.py resim.jpg --renkli --genislik 100 --karakter Sayılar
```

| Option | Description |
| --- | --- |
| `--renkli` | 24-bit colour (ANSI) output |
| `--genislik N` | Width in characters (default 100) |
| `--karakter` | `Karışık` (mixed), `Sayılar` (numbers), `Semboller` (symbols) or `Basit` (simple) |

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" width="26" align="center"> Building the exe

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "ASCII Art Studio" --icon icon.ico --add-data "icon.ico;." ascii_art.py
```

To change the app icon, edit and run `make_icon.py`; it redraws `icon.ico` separately at every size.

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/File%20Folder.png" width="26" align="center"> Project structure

| File | Role |
| --- | --- |
| `ascii_art.py` | Image → ASCII conversion, export, app window and terminal mode |
| `neo_ui.py` | Neo Brutalism widgets for Tkinter: thick-bordered buttons with hard shadows, cards, slider, switch and theme colours |
| `make_icon.py` | `icon.ico` generator |

Tkinter cannot draw hard shadows or smooth rounded corners on its own, so the widgets are drawn large with Pillow, scaled down and shown as images; that keeps the edges smooth.

---

## 🇹🇷 Türkçe

Görselleri **sayı ve sembollerle** renkli ya da renksiz ASCII art'a dönüştüren, Neo Brutalism tasarımlı küçük bir masaüstü uygulaması. Çıktıyı panoya kopyalayabilir, terminalde renkli görünen bir `.txt` dosyası ya da `.png` resmi olarak kaydedebilirsin.

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Sparkles.png" width="26" align="center"> Özellikler

| | |
| :--- | :--- |
| 🖱️ **Sürükle-bırak** | Görseli pencereye bırakman yeterli; istersen **Görsel Seç** butonunu da kullanabilirsin |
| 🔄 **Döndürme** | Görseli ↺ / ↻ butonlarıyla 90° sola ya da sağa çevirebilirsin |
| 📏 **Genişlik ayarı** | Çıktının kaç karakter genişliğinde olacağını (20–250) topuzlu kaydırıcıyla seçersin |
| 🔤 **Karakter setleri** | Karışık, Sayılar, Semboller ve Basit — karakterler ekranda ne kadar dolu göründüklerine göre otomatik sıralanır |
| 🎨 **Renkli / Renksiz** | İki çıktı modu |
| 🔍 **Yakınlaştırma** | −/+ butonları ya da Ctrl + tekerlek; fareyle sürükleyerek gezinirsin, ⤢ görüntüyü panele sığdırır |
| 💾 **Dışa aktarma** | **Kopyala** düz metin · **TXT** 24-bit ANSI renk kodlarıyla (`type` / `cat` ile açınca terminalde renkli) · **PNG** resim |
| 🌙 **Karanlık tema** | Seçimin bir sonraki açılışta hatırlanır |
| 💻 **Terminal modu** | Pencere açmadan sonucu doğrudan terminale yazdırır |

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Rocket.png" width="26" align="center"> Kurulum

**Hazır exe (Windows):** [Releases](https://github.com/huseyinbaranisik/ascii-art-studio/releases/latest) sayfasından `ASCII.Art.Studio.exe` dosyasını indirip çift tıklaman yeterli; Python kurulu olmasına gerek yok.

> Windows SmartScreen imzasız uygulamalar için uyarı gösterebilir. Bu durumda **Ek bilgi → Yine de çalıştır** seçeneğine tıkla.

**Kaynaktan çalıştırma** (Python 3.10+):

```bash
pip install -r requirements.txt
python ascii_art.py
```

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Laptop.png" width="26" align="center"> Terminal modu

```bash
python ascii_art.py resim.jpg --renkli --genislik 100 --karakter Sayılar
```

| Seçenek | Açıklama |
| --- | --- |
| `--renkli` | 24-bit renkli (ANSI) çıktı |
| `--genislik N` | Karakter cinsinden genişlik (varsayılan 100) |
| `--karakter` | `Karışık`, `Sayılar`, `Semboller` veya `Basit` |

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" width="26" align="center"> Exe oluşturma

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "ASCII Art Studio" --icon icon.ico --add-data "icon.ico;." ascii_art.py
```

Uygulama ikonunu değiştirmek istersen `make_icon.py` dosyasını düzenleyip çalıştırman yeterli. Bu betik `icon.ico` dosyasını her boyutu ayrı çizerek yeniden üretir.

### <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/File%20Folder.png" width="26" align="center"> Proje yapısı

| Dosya | Görevi |
| --- | --- |
| `ascii_art.py` | Görseli ASCII'ye çevirme, dışa aktarma, uygulama penceresi ve terminal modu |
| `neo_ui.py` | Tkinter için Neo Brutalism bileşenleri: kalın kenarlı, keskin gölgeli butonlar, kartlar, kaydırıcı, anahtar ve tema renkleri |
| `make_icon.py` | `icon.ico` üretici |

Tkinter kendi başına keskin gölge ve pürüzsüz yuvarlak köşe çizemiyor. Bu yüzden bileşenler Pillow ile büyük boyutta çizilip küçültülüyor ve resim olarak gösteriliyor; böylece kenarlar yumuşak kalıyor.


<br>

<div align="center">
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Red%20Heart.png" width="22" align="center" alt="Red Heart">
  <sub>Made by <a href="https://github.com/huseyinbaranisik">Hüseyin Baran Işık</a> · Animated emojis: <a href="https://github.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis">Animated Fluent Emojis</a></sub>
</div>
