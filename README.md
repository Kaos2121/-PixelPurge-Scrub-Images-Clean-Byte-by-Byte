# 🧼 PixelPurge – Scrub Images Clean, Byte by Byte

**PixelPurge** is a high-precision image sanitizer that deep-cleans **PNG** and **JPEG** files by stripping metadata, killing EXIF/chunks, and recalculating entropy — all without touching the actual pixel data.  
Perfect for privacy, OSINT workflows, stego analysis, and clean archiving.

> File: `img.py`

---

## ⚙️ Features

- ✅ **EXIF remover** for JPEGs using `piexif`
- ✅ **Chunk cleaner** for PNGs via `PIL.Image` and `PngInfo`
- ✅ **Entropy analyzer** to detect compressed/encrypted residue
- ✅ **File hash comparison** (before & after scrub)
- ✅ **Auto-mode detection** and pixel preservation
- ✅ **Verifies output integrity**
- ✅ **Randomized output filename**

---

## 🖼️ How it works

PixelPurge reads the image, strips metadata, reconstructs it pixel-by-pixel, and rewrites it in a fresh container:

```bash
Original mode: RGBA → Re-encoded: RGB (or RGBA for PNG)
```

Then it:

- Calculates original entropy and SHA256
- Optimizes and scrubs metadata (EXIF / PNG chunks)
- Verifies image integrity
- Warns about high entropy or identical hashes (potential failures)
- Outputs a brand new file like `clean_d3f4e5c6b9.jpg`

---

## 🚀 Usage

Make sure to install the dependencies first:

```bash
pip install pillow piexif
```

Then run:

```bash
python img.py
```

Edit the file to point to your input image:

```python
input_file = "your_image.jpg"
```

---

## 🧠 Output Summary

Example output:

```
[~] Cleaning: logo.jpg
[~] Original color mode: RGB → Converted to: RGB
[✓] Final clean image saved to: clean_a1b2c3d4e5.jpg
[#] Original SHA256: 9f8d...
[#] Cleaned SHA256:  d5c3...
[#] Original size:   132KB
[#] Cleaned size:    115KB
[#] Entropy:         6.21 → 5.88
[~] Time taken:      0.97 seconds
```

---

## ⚠️ Warnings You Might See

- **High entropy after clean** → Image may still contain embedded/encrypted data
- **File hash unchanged** → File may have already been clean
- **Output larger than input** → Could be residual or recompression artifacts

---

## 🧪 Supported Formats

- ✅ `.png`
- ✅ `.jpg`, `.jpeg`

📁 Output files are saved in the same directory as the original with randomized filenames.

---

## 🧤 Perfect For:

- Privacy advocates
- Malware analysts
- Stego investigators
- OSINT toolkits
- Clean publishing pipelines

---

## 🔓 License

MIT – Free to use, modify, and share.
