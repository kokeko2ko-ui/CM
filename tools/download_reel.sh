#!/usr/bin/env bash
#
# download_reel.sh — Instagram リール / 投稿 / 動画・画像素材をダウンロードする
#
# 目的:
#   モーションデザインの素材（リールの動画、サムネイル画像、投稿画像）を
#   ローカルに保存し、そのままアップロードして使えるようにする。
#
# 前提:
#   - yt-dlp がインストールされていること
#       pip install -U yt-dlp   (または  brew install yt-dlp)
#   - Instagram にアクセスできるネットワーク環境で実行すること
#       ※ Claude Code のリモート実行環境では Instagram が
#         ネットワークポリシーで遮断されているため、ここでは動きません。
#         お手元のPC / Mac で実行してください。
#
# 使い方:
#   ./tools/download_reel.sh "https://www.instagram.com/reel/XXXXXXXXXXX/"
#   ./tools/download_reel.sh "<URL>" ./assets            # 保存先を指定
#   ./tools/download_reel.sh "<URL>" ./assets --frames   # 動画に加え全フレームをPNGで抽出
#
# 出力:
#   - 動画本体 (mp4)
#   - サムネイル画像 (jpg)
#   - --frames 指定時: frames/ に連番PNG（素材候補として使える静止画）
#
set -euo pipefail

URL="${1:-}"
OUTDIR="${2:-./assets}"
EXTRACT_FRAMES="false"
[[ "${3:-}" == "--frames" ]] && EXTRACT_FRAMES="true"

if [[ -z "$URL" ]]; then
  echo "使い方: $0 <Instagram/動画URL> [保存先ディレクトリ] [--frames]" >&2
  exit 1
fi

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "エラー: yt-dlp が見つかりません。先に  pip install -U yt-dlp  を実行してください。" >&2
  exit 1
fi

mkdir -p "$OUTDIR"

echo "▶ ダウンロード中: $URL"
# 非公開/年齢制限つきの場合はブラウザの Cookie を使う:
#   --cookies-from-browser chrome   などを下に追加してください。
yt-dlp \
  --no-playlist \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -o "$OUTDIR/%(uploader_id)s_%(id)s.%(ext)s" \
  "$URL"

echo "✅ 保存先: $OUTDIR"

if [[ "$EXTRACT_FRAMES" == "true" ]]; then
  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "注意: ffmpeg が無いためフレーム抽出はスキップしました（ brew install ffmpeg 等でインストール可）。" >&2
  else
    VIDEO="$(find "$OUTDIR" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.webm' -o -name '*.mkv' \) | head -1)"
    if [[ -n "$VIDEO" ]]; then
      mkdir -p "$OUTDIR/frames"
      echo "▶ フレーム抽出中: $VIDEO"
      # 1秒あたり2フレーム抽出（必要に応じて fps を変更）
      ffmpeg -y -loglevel error -i "$VIDEO" -vf "fps=2" "$OUTDIR/frames/frame_%03d.png"
      echo "✅ フレーム: $OUTDIR/frames/"
    fi
  fi
fi

echo ""
echo "次のステップ: 保存した mp4 / jpg / png をチャットにアップロードすれば素材として使えます。"
