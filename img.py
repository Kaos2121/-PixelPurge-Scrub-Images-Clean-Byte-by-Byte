from PIL import Image, PngImagePlugin, JpegImagePlugin
import os
import tempfile
import time
import uuid
import hashlib
import math
import piexif

def calculate_entropy(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    if not data:
        return 0
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    entropy = 0
    for count in freq:
        if count == 0:
            continue
        p = count / len(data)
        entropy -= p * math.log2(p)
    return entropy

def sha256_file(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def strip_exif_with_piexif(jpeg_path):
    try:
        piexif.remove(jpeg_path)
    except Exception as e:
        print(f"[!] EXIF strip error: {e}")

def remove_png_chunks(file_path):
    try:
        with Image.open(file_path) as im:
            data = list(im.getdata())
            mode = im.mode
            clean = Image.new(mode, im.size)
            clean.putdata(data)
            out = PngImagePlugin.PngInfo()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_file:
                clean.save(out_file.name, "PNG", pnginfo=out, optimize=True)
                return out_file.name
    except Exception as e:
        print(f"[!] PNG chunk strip error: {e}")
        return None

def fully_strip_image(input_path):
    if not os.path.exists(input_path):
        print(f"[-] File not found: {input_path}")
        return

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg"):
        print("[-] Unsupported file format. Only PNG and JPEG are supported.")
        return

    try:
        print(f"[~] Cleaning: {input_path}")
        start_time = time.time()

        original_entropy = calculate_entropy(input_path)
        original_hash = sha256_file(input_path)
        original_size = os.path.getsize(input_path)

        img = Image.open(input_path)
        original_mode = img.mode

        if ext == ".png":
            mode = "RGBA" if img.mode in ("RGBA", "LA") else "RGB"
        else:
            mode = "RGB"
        print(f"[~] Original color mode: {original_mode} -> Converted to: {mode}")
        img = img.convert(mode)

        pixels = list(img.getdata())
        clean_img = Image.new(mode, img.size)
        clean_img.putdata(pixels)

        format_out = "PNG" if ext == ".png" else "JPEG"

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            temp_name = tmp_file.name
            if format_out == "PNG":
                clean_info = PngImagePlugin.PngInfo()
                clean_img.save(temp_name, format="PNG", optimize=True, pnginfo=clean_info)
                chunk_clean = remove_png_chunks(temp_name)
                if chunk_clean:
                    os.replace(chunk_clean, temp_name)
            else:
                clean_img.save(temp_name, format="JPEG", optimize=True, quality=90, exif=b'')
                strip_exif_with_piexif(temp_name)

        rand_name = f"clean_{uuid.uuid4().hex[:10]}{ext}"
        final_path = os.path.join(os.path.dirname(input_path), rand_name)
        os.replace(temp_name, final_path)

        now = time.time()
        os.utime(final_path, (now, now))

        try:
            with Image.open(final_path) as test_img:
                test_img.verify()
        except Exception:
            print("[!] Warning: saved image may be corrupted.")
            os.remove(final_path)
            return

        final_hash = sha256_file(final_path)
        final_entropy = calculate_entropy(final_path)
        final_size = os.path.getsize(final_path)

        print(f"[✓] Final clean image saved to: {final_path}")
        print(f"[#] Original SHA256: {original_hash}")
        print(f"[#] Cleaned SHA256:  {final_hash}")
        print(f"[#] Original size:   {original_size} bytes")
        print(f"[#] Cleaned size:    {final_size} bytes")
        print(f"[#] Entropy:         {original_entropy:.2f} → {final_entropy:.2f}")

        if final_entropy > 7.5:
            print("[!] High entropy warning: file may still contain compressed or encrypted data.")
        if final_size > original_size * 1.5:
            print("[!] Warning: Output is much larger than input; check for residual embedded data.")
        if original_hash == final_hash:
            print("[!] Warning: File hash unchanged. Clean may have failed or image was already clean.")

        print(f"[~] Time taken:      {time.time() - start_time:.2f} seconds")

    except Exception as e:
        print(f"[!] Error during image scrubbing: {e}")

if __name__ == "__main__":
    input_file = "logo.jpg"  # CHANGE THIS TO YOUR FILE
    fully_strip_image(input_file)
