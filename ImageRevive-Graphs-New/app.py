from io import BytesIO
import base64, time
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat, UnidentifiedImageError

app = Flask(__name__, static_folder="public", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
ALLOWED = {"png", "jpg", "jpeg", "webp"}

@app.get("/")
def home():
    return send_from_directory("public", "index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "ImageRevive API"})

@app.post("/api/process")
def process():
    start = time.perf_counter()
    if "image" not in request.files:
        return jsonify(error="Choose an image to upload."), 400
    upload = request.files["image"]
    ext = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
    if ext not in ALLOWED:
        return jsonify(error="Use a PNG, JPG, JPEG, or WEBP image."), 400
    operation = request.form.get("operation", "auto_enhance")
    try:
        strength = max(1, min(9, int(request.form.get("strength", "5"))))
    except ValueError:
        strength = 5
    try:
        image = ImageOps.exif_transpose(Image.open(upload.stream)).convert("RGB")
        image.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
    except (UnidentifiedImageError, OSError):
        return jsonify(error="This file could not be read as an image."), 400
    try:
        result = transform(image, operation, strength)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    buf = BytesIO()
    result.save(buf, format="PNG", optimize=True)
    original_gray = image.convert("L")
    result_gray = result.convert("L")
    original_stat = ImageStat.Stat(original_gray)
    result_stat = ImageStat.Stat(result_gray)
    original_hist = original_gray.histogram()
    result_hist = result_gray.histogram()
    return jsonify(
        image="data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii"),
        operation=operation, width=result.width, height=result.height,
        processing_ms=round((time.perf_counter()-start)*1000, 1),
        output_bytes=len(buf.getvalue()), brightness=round(result_stat.mean[0], 1),
        contrast=round(result_stat.stddev[0], 1),
        original_brightness=round(original_stat.mean[0], 1),
        original_contrast=round(original_stat.stddev[0], 1),
        original_histogram=original_hist,
        result_histogram=result_hist
    )

def transform(image, operation, strength):
    if operation == "grayscale":
        return ImageOps.grayscale(image).convert("RGB")
    if operation == "auto_enhance":
        return ImageOps.autocontrast(image, cutoff=1)
    if operation == "contrast":
        return ImageEnhance.Contrast(image).enhance(0.6 + strength * 0.25)
    if operation == "brightness":
        return ImageEnhance.Brightness(image).enhance(0.5 + strength * 0.15)
    if operation == "median":
        size = 3 if strength <= 3 else 5 if strength <= 6 else 7
        return image.filter(ImageFilter.MedianFilter(size=size))
    if operation == "sharpen":
        return image.filter(ImageFilter.UnsharpMask(radius=1+strength/4, percent=80+strength*20, threshold=3))
    if operation == "edges":
        return ImageOps.grayscale(image).filter(ImageFilter.FIND_EDGES).convert("RGB")
    if operation == "threshold":
        gray = ImageOps.grayscale(image)
        threshold = otsu(gray)
        return gray.point(lambda p: 255 if p >= threshold else 0).convert("RGB")
    raise ValueError("Unknown processing method.")

def otsu(gray):
    hist = gray.histogram()
    total = sum(hist)
    weighted = sum(i*n for i, n in enumerate(hist))
    bg_weight = bg_sum = 0
    best_var, best_t = -1, 127
    for t, count in enumerate(hist):
        bg_weight += count
        if bg_weight == 0:
            continue
        fg_weight = total - bg_weight
        if fg_weight == 0:
            break
        bg_sum += t * count
        mb = bg_sum / bg_weight
        mf = (weighted - bg_sum) / fg_weight
        var = bg_weight * fg_weight * (mb - mf) ** 2
        if var > best_var:
            best_var, best_t = var, t
    return best_t

@app.errorhandler(413)
def too_large(_):
    return jsonify(error="Image exceeds the 8 MB upload limit."), 413

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
