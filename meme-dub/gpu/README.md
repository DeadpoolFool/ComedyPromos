# LatentSync on Modal (cloud GPU)

Lip-syncs a face video to a voice track with ByteDance LatentSync 1.6 on a Modal L40S.

## One-time setup (Windows, PowerShell)

```
cd "C:\Standup Studio\latentsync-cloud"
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install modal imageio-ffmpeg
.\.venv\Scripts\python -m modal setup     # browser login
```

## Run

```
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python -m modal run latentsync_modal.py `
  --video meme-dub\gpu\bernie_swaponly.mp4 `
  --audio meme-dub\gpu\voice_trimmed.wav `
  --out out\bernie_latentsync.mp4
```

Options: `--steps 25` (20-30), `--guidance 1.5`. The first run builds the image and
caches checkpoints in the `latentsync-ckpt` volume.

## Caption overlay

```
$ff = .\.venv\Scripts\python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"
& $ff -i out\bernie_latentsync.mp4 -i meme-dub\gpu\caption.png `
  -filter_complex "[1:v][0:v]scale2ref[c][v];[v][c]overlay=0:0" `
  -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy meme-dub\out\bernie-once-again-latentsync.mp4
```
