import os
import uuid
import shlex
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, jsonify, abort

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUT_DIR = BASE_DIR / "processed"
for d in (UPLOAD_DIR, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {"mp4", "mov", "mkv", "avi", "webm"}

app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=2 * 1024 * 1024 * 1024)  # 2GB

def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXT

def _unique_name(suffix: str) -> str:
    import uuid
    return f"{uuid.uuid4().hex}{suffix}"

def _parse_time(t):
    """Accepts seconds (int/str) or HH:MM:SS, MM:SS, returns ffmpeg-compatible string."""
    if t is None:
        return None
    t = str(t).strip()
    if t == "":
        return None
    if t.isdigit():
        return str(int(t))
    # Accept MM:SS or HH:MM:SS
    parts = t.split(":")
    if len(parts) == 2:
        # MM:SS -> 00:MM:SS
        return f"00:{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    if len(parts) == 3:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)}"
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/upload")
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        abort(400, "no file")
    if not _allowed(file.filename):
        abort(400, "unsupported file type")
    ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    name = _unique_name(ext)
    save_path = UPLOAD_DIR / name
    file.save(save_path)
    return jsonify({"ok": True, "filename": name})

@app.post("/process")
def process():
    data = request.get_json(force=True)
    in_name = data.get("filename")
    task = data.get("task")  # 'vv', 'vgif', 'deid'
    reso = data.get("resolution")  # e.g., '1920x1080' or None
    fps = data.get("fps")
    mute = bool(data.get("mute"))
    deid_args = data.get("deid_args") or ""

    if not in_name:
        abort(400, "missing filename")

    in_path = UPLOAD_DIR / in_name
    if not in_path.exists():
        abort(404, "input not found")

    if task == "vgif":
        out_name = _unique_name(".gif")
    else:
        out_name = _unique_name(".mp4")
    out_path = OUT_DIR / out_name

    start_time = _parse_time(data.get("start_time"))  # Accepts seconds or HH:MM:SS
    duration   = _parse_time(data.get("duration"))    # Accepts seconds or HH:MM:SS

    if task == "vv":
        vf_parts = []
        if reso:
            if str(reso).isdigit():
                w = int(reso)
                vf_parts.append(f"scale={w}:-2:flags=bicubic")
        vf = ",".join(vf_parts) if vf_parts else None

        cmd = ["ffmpeg", "-y"]
        if start_time:
            cmd += ["-ss", str(start_time)]
        if duration:
            cmd += ["-t", str(duration)]
        cmd += ["-i", str(in_path)]
        if vf:
            cmd += ["-vf", vf]
        if fps:
            cmd += ["-r", str(int(fps))]
        if mute:
            cmd += ["-an"]
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(out_path)]

    elif task == "vgif":
        q = (data.get("gif_quality") or "custom").lower()
        presets = {
            "tiny":   {"w": 360, "fps": 8,  "dither": "bayer", "bayer_scale": 5},
            "small":  {"w": 480, "fps": 10, "dither": "bayer", "bayer_scale": 4},
            "medium": {"w": 640, "fps": 12, "dither": "bayer", "bayer_scale": 3},
            "high":   {"w": 720, "fps": 15, "dither": "bayer", "bayer_scale": 2},
        }
        sel_w = int(reso) if (reso and str(reso).isdigit()) else None
        sel_fps = int(fps) if fps else None
        if q in presets:
            p = presets[q]
            w = p["w"]
            eff_fps = p["fps"]
            dither = p["dither"]
            bayer_scale = p["bayer_scale"]
        else:
            w = sel_w or 640
            eff_fps = sel_fps or 12
            dither = "bayer"
            bayer_scale = 4
        bayer_scale = max(0, min(5, int(bayer_scale)))
        pal_fps = f"fps={eff_fps}"
        scale_clause = f",scale={w}:-2:flags=lanczos"
        vf = (
            pal_fps + scale_clause +
            ",split[s0][s1];[s0]palettegen=stats_mode=diff[p];"
            f"[s1][p]paletteuse=dither={dither}:bayer_scale={bayer_scale}"
        )
        cmd = ["ffmpeg", "-y"]
        if start_time:
            cmd += ["-ss", str(start_time)]
        if duration:
            cmd += ["-t", str(duration)]
        cmd += ["-i", str(in_path), "-vf", vf, str(out_path)]

    elif task == "deid":
        base_cmd = f"deface -i {shlex.quote(str(in_path))} -o {shlex.quote(str(out_path))} {deid_args}"
        cmd = ["bash", "-lc", base_cmd]
    else:
        abort(400, "unknown task")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return jsonify({
            "ok": True,
            "output": out_name,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
            "download_url": f"/download/{out_name}"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "ok": False,
            "error": "processing failed",
            "detail": e.stderr[-4000:] if e.stderr else str(e)
        }), 500

@app.get("/download/<path:fname>")
def download(fname):
    path = OUT_DIR / fname
    if not path.exists():
        abort(404)
    return send_from_directory(OUT_DIR, fname, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5252, debug=True)
