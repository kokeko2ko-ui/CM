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
