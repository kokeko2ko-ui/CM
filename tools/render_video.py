#!/usr/bin/env python3
"""render_video.py — Vrew の MP3 + SRT から字幕つき動画(mp4)を書き出す。

MP3 が読めない／尺がずれる原因(日本語パス、VBR、ID3、壊れたヘッダ等)を避けるため、
入力は ASCII 名の一時フォルダへコピーし、音声は一度 44.1kHz ステレオ WAV に正規化してから使う。

使い方:
  python3 tools/render_video.py voice.mp3 subs.srt                  # 黒背景 1920x1080
  python3 tools/render_video.py voice.mp3 subs.srt -o out.mp4 --bg bg.jpg
  python3 tools/render_video.py voice.mp3 subs.srt --bg ./clips     # 画像/動画フォルダを順に敷く
  python3 tools/render_video.py voice.mp3 subs.srt --check          # 検証だけ(書き出さない)

必要: ffmpeg / ffprobe (libass 付き)
"""
import argparse, re, shutil, subprocess, sys, tempfile
from pathlib import Path

IMG = {".jpg", ".jpeg", ".png", ".webp"}
VID = {".mp4", ".mov", ".mkv", ".webm"}
FONTS = ["Noto Sans CJK JP", "Noto Sans JP", "Hiragino Sans", "Hiragino Kaku Gothic ProN",
         "Yu Gothic", "Meiryo", "IPAGothic", "TakaoGothic", "WenQuanYi Zen Hei"]


def die(msg):
    sys.exit(f"エラー: {msg}")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        die(f"{cmd[0]} が失敗しました\n{r.stderr[-1500:]}")
    return r.stdout


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)]).strip()
    return float(out)


def srt_end(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    ts = re.findall(r"-->\s*(\d+):(\d+):(\d+)[,.](\d+)", text)
    if not ts:
        die("SRT に時刻行が見つかりません(UTF-8 の SRT か確認)")
    h, m, s, ms = map(int, ts[-1])
    return h * 3600 + m * 60 + s + ms / 1000, len(ts)


def pick_font():
    try:
        have = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    except FileNotFoundError:
        return "Yu Gothic" if sys.platform == "win32" else "Noto Sans CJK JP"
    for f in FONTS:
        if f.lower() in have.lower():
            return f
    print("警告: 日本語フォントが見つかりません。文字化け(□)する場合は Noto Sans CJK JP を入れてください。")
    return "sans-serif"


def build_bg(bg, total, size, work):
    """背景を total 秒ぶんの 1 本の mp4 にする。"""
    w, h = size.split("x")
    scale = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30,format=yuv420p"
    out = work / "bg.mp4"
    if bg is None:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={size}:r=30",
             "-t", f"{total:.3f}", "-pix_fmt", "yuv420p", str(out)])
        return out
    bg = Path(bg)
    files = sorted(p for p in bg.iterdir() if p.suffix.lower() in IMG | VID) if bg.is_dir() else [bg]
    if not files:
        die(f"背景フォルダに画像/動画がありません: {bg}")
    per = total / len(files)
    parts = []
    for i, f in enumerate(files):
        seg = work / f"seg{i:03d}.mp4"
        pre = ["-loop", "1"] if f.suffix.lower() in IMG else ["-stream_loop", "-1"]
        run(["ffmpeg", "-y", *pre, "-i", str(f), "-t", f"{per:.3f}", "-an", "-vf", scale,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(seg)])
        parts.append(seg)
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio"), ap.add_argument("srt")
    ap.add_argument("-o", "--out", default="output.mp4")
    ap.add_argument("--bg", help="背景の画像/動画 または そのフォルダ(省略=黒)")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--font-size", type=int, default=20)
    ap.add_argument("--check", action="store_true", help="検証のみ")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(f"{tool} が見つかりません(macOS: brew install ffmpeg / Ubuntu: sudo apt install ffmpeg)")
    audio, srt = Path(a.audio), Path(a.srt)
    for p in (audio, srt):
        if not p.is_file():
            die(f"ファイルがありません: {p}")

    with tempfile.TemporaryDirectory(prefix="rv_") as t:
        work = Path(t)
        # ASCII 名にコピー(日本語・空白パス対策)し、音声は WAV に正規化
        shutil.copy(srt, work / "subs.srt")
        run(["ffmpeg", "-y", "-i", str(audio), "-vn", "-ac", "2", "-ar", "44100",
             "-c:a", "pcm_s16le", str(work / "voice.wav")])
        a_len = duration(work / "voice.wav")
        s_len, n = srt_end(work / "subs.srt")
        diff = a_len - s_len
        print(f"音声 {a_len:.2f}s / 字幕 {s_len:.2f}s ({n}行) / 差 {diff:+.2f}s")
        if abs(diff) > 5:
            print("警告: 音声と字幕の尺が 5 秒以上ずれています。Vrew で書き出した同じ版か確認してください。")
        if a.check:
            return
        bg = build_bg(a.bg, a_len, a.size, work)
        style = (f"FontName={pick_font()},FontSize={a.font_size},PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H00000000,BorderStyle=1,Outline=1.2,Shadow=0,Alignment=2,MarginV=18")
        out = Path(a.out).resolve()
        # subtitles フィルタは相対パス解決が必要なので work を cwd にして実行
        r = subprocess.run(["ffmpeg", "-y", "-i", str(bg), "-i", "voice.wav",
                            "-vf", f"subtitles=subs.srt:force_style='{style}'",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)],
                           cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            die("書き出しに失敗しました\n" + r.stderr[-1500:])
        print(f"完了: {out} ({duration(out):.2f}s)")


if __name__ == "__main__":
    main()
