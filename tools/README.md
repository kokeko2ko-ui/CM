# 素材ダウンロードツール

モーションデザインの素材（Instagram リールなど）をローカルに保存するためのツールです。

## なぜローカルで実行するのか

Claude Code のリモート実行環境は、通信ポリシーで `www.instagram.com` を
**403 で遮断**しています（意図的なネットワーク制限）。そのため、この環境からは
Instagram のリールを直接ダウンロードできません。お手元の PC / Mac で実行してください。

## セットアップ

```bash
pip install -U yt-dlp        # 必須
# 任意（フレーム抽出に使用）
#   macOS:  brew install ffmpeg
#   Ubuntu: sudo apt install ffmpeg
```

## 使い方

```bash
# リールをダウンロード（動画 + サムネイル）
./tools/download_reel.sh "https://www.instagram.com/reel/Dbra67Cy5Qv/"

# 保存先を指定
./tools/download_reel.sh "https://www.instagram.com/reel/Dbra67Cy5Qv/" ./assets

# 動画に加えて全フレームを PNG で抽出（素材候補の静止画が欲しい場合）
./tools/download_reel.sh "https://www.instagram.com/reel/Dbra67Cy5Qv/" ./assets --frames
```

非公開・年齢制限つきの投稿は、`download_reel.sh` 内のコメントに従って
`--cookies-from-browser chrome` などを追記してください。

## この後の流れ

保存した `mp4` / `jpg` / `png` を**チャットに直接アップロード**すれば、
モーションデザインスキルの素材として使えます。

---

# 動画書き出し（Vrew の MP3 + SRT）

```bash
python3 tools/render_video.py voice.mp3 subs.srt                 # 黒背景 1920x1080 → output.mp4
python3 tools/render_video.py voice.mp3 subs.srt --bg ./clips    # 画像/動画フォルダを均等配分で敷く
python3 tools/render_video.py voice.mp3 subs.srt --check         # 音声と字幕の尺だけ検証
```

MP3 が通らない問題への対策を組み込み済み:

- 日本語・空白を含むパスでも動くよう、ASCII 名の一時フォルダへコピーして処理
- MP3 は一度 44.1kHz ステレオ WAV に正規化（VBR・ID3・ヘッダ不良を吸収）
- 音声と SRT の尺が 5 秒以上ずれたら警告
- 日本語フォントを自動検出（Noto Sans CJK JP / ヒラギノ / 游ゴシック / メイリオ 等）

必要: `ffmpeg`（libass 付き。`brew install ffmpeg` / `sudo apt install ffmpeg`）
