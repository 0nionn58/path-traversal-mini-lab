from flask import Flask, request, render_template, redirect, url_for, send_file, abort
from pathlib import Path
import mimetypes

app = Flask(__name__)

PROJECT_ROOT = Path(".").resolve()
BASE_DIR     = PROJECT_ROOT / "app" / "files"

IMAGE_EXTS   = {".png", ".jpg", ".jpeg", ".gif"}

def resolve_user_path(user_input: str) -> Path:
    candidate = (BASE_DIR / user_input).resolve()

    if candidate.exists():
        return candidate

    alt = (PROJECT_ROOT / user_input.lstrip("/")).resolve()
    if alt.exists():
        return alt

    return candidate


def build_tree(root: Path, highlight: str) -> str:
    lines = ["/"]

    def walk(dir_path: Path, prefix: str = ""):
        entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        for idx, entry in enumerate(entries):
            connector = "└── " if idx == len(entries) - 1 else "├── "
            line_prefix = prefix + connector
            rel = entry.relative_to(root).as_posix()

            text = entry.name
            if rel == highlight:
                cls = "selected danger" if text == "flag.txt" else "selected"
                text = f'<span class="{cls}">{text}</span>'
            elif entry.name == "flag.txt":
                text = f'<span class="danger">{text}</span>'

            lines.append(f"{line_prefix}{text}")

            if entry.is_dir():
                next_prefix = prefix + ("    " if idx == len(entries) - 1 else "│   ")
                walk(entry, next_prefix)

    walk(root)
    return "\n".join(lines)

@app.route("/")
def home():
    return redirect(url_for("index", file="report.txt"))

@app.route("/index")
def index():
    raw_input = request.args.get("file", "")
    resolved  = resolve_user_path(raw_input)

    try:
        rel_path = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        rel_path = resolved.as_posix().lstrip("/")

    tree_html = build_tree(PROJECT_ROOT, rel_path)
    is_image, content, error = False, "", ""
    if raw_input:
        try:
            if resolved.suffix.lower() in IMAGE_EXTS:
                is_image = True
            else:
                data = resolved.read_bytes()
                content = data.decode("utf-8", errors="replace")
        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        tree=tree_html,
        raw=raw_input,
        is_image=is_image,
        content=content,
        error=error,
    )


@app.route("/raw")
def raw():
    raw_input = request.args.get("file", "")
    resolved  = resolve_user_path(raw_input)
    try:
        mime = mimetypes.guess_type(resolved)[0] or "application/octet-stream"
        return send_file(resolved, mime)
    except FileNotFoundError:
        abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
