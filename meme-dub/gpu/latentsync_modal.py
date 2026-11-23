"""LatentSync lip sync on a Modal cloud GPU.

    modal run latentsync_modal.py --video face.mp4 --audio voice.wav --out out.mp4

First run builds the image and downloads the checkpoints into the
`latentsync-ckpt` volume; later runs reuse both.
"""
import pathlib
import time

import modal

VERSION = "1.6"  # 1.5 fits a 24 GB A10G; 1.6 (512px) needs ~18 GB
GPU = "L40S"
REPO = "/LatentSync"

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "libgl1", "libglib2.0-0", "build-essential")
    .run_commands(f"git clone https://github.com/bytedance/LatentSync {REPO}")
    .run_commands(f"pip install -r {REPO}/requirements.txt")
    .env({"HF_HOME": "/ckpt/hf", "TORCH_HOME": "/ckpt/torch"})
)
vol = modal.Volume.from_name("latentsync-ckpt", create_if_missing=True)
app = modal.App("latentsync", image=image)


@app.function(gpu=GPU, volumes={"/ckpt": vol}, timeout=3600)
def lipsync(video: bytes, audio: bytes, steps: int = 25, guidance: float = 1.5) -> bytes:
    import os
    import subprocess

    from huggingface_hub import hf_hub_download

    ck = f"/ckpt/latentsync-{VERSION}"
    for f in ("whisper/tiny.pt", "latentsync_unet.pt"):
        if not os.path.exists(f"{ck}/{f}"):
            hf_hub_download(f"ByteDance/LatentSync-{VERSION}", f, local_dir=ck)
    vol.commit()
    if not os.path.exists(f"{REPO}/checkpoints"):
        os.symlink(ck, f"{REPO}/checkpoints")

    pathlib.Path("/tmp/in.mp4").write_bytes(video)
    pathlib.Path("/tmp/in.wav").write_bytes(audio)
    unet = "stage2_512.yaml" if VERSION == "1.6" else "stage2.yaml"
    t = time.time()
    subprocess.run(
        ["python", "-m", "scripts.inference",
         "--unet_config_path", f"configs/unet/{unet}",
         "--inference_ckpt_path", "checkpoints/latentsync_unet.pt",
         "--inference_steps", str(steps), "--guidance_scale", str(guidance),
         "--enable_deepcache",
         "--video_path", "/tmp/in.mp4", "--audio_path", "/tmp/in.wav",
         "--video_out_path", "/tmp/out.mp4"],
        cwd=REPO, check=True,
    )
    vol.commit()  # keep HF/torch caches downloaded during inference
    print(f"inference took {time.time() - t:.0f} s on {GPU}")
    return pathlib.Path("/tmp/out.mp4").read_bytes()


@app.local_entrypoint()
def main(video: str, audio: str, out: str = "out.mp4", steps: int = 25, guidance: float = 1.5):
    t = time.time()
    data = lipsync.remote(pathlib.Path(video).read_bytes(), pathlib.Path(audio).read_bytes(),
                          steps, guidance)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_bytes(data)
    print(f"wrote {out} ({time.time() - t:.0f} s total)")
