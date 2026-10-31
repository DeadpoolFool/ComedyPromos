"""Fix color from his skin: find the face, set channel gains so the cheeks hit a neutral skin ratio,
apply at `k` strength, then tame saturation. Usage: skingrade.py in out [k] [sat]"""
import sys, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions
from PIL import Image, ImageEnhance
src, dst = sys.argv[1:3]; k = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8; sat = float(sys.argv[4]) if len(sys.argv) > 4 else 0.9
TARGET = np.array([1.0, 0.80, 0.68])  # R:G:B of neutral light skin
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="/tmp/claude-0/mp/face_landmarker.task"), num_faces=1, min_face_detection_confidence=0.3))
im = Image.open(src).convert("RGB"); a = np.asarray(im).astype(np.float32); H, W = a.shape[:2]
best = None
for S in (W // 3, W // 5):
    for x0 in range(0, W - S + 1, S // 2):
        for y0 in range(0, H - S + 1, S // 2):
            crop = np.ascontiguousarray(a[y0:y0+S, x0:x0+S].astype(np.uint8))
            r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=crop))
            if r.face_landmarks:
                p = r.face_landmarks[0]; best = [(x0 + q.x * S, y0 + q.y * S) for q in p]; break
        if best: break
    if best: break
if not best: sys.exit(f"no face in {src}")
# cheeks + forehead landmarks
idx = [50, 280, 101, 330, 10, 151, 108, 337]
px = np.array([a[int(best[i][1]), int(best[i][0])] for i in idx]); r = 6
px = np.array([a[int(best[i][1])-r:int(best[i][1])+r, int(best[i][0])-r:int(best[i][0])+r].reshape(-1, 3).mean(0) for i in idx])
skin = np.median(px, axis=0); ratio = skin / skin[0]
gain = TARGET / ratio; gain = gain / gain.mean() * (skin.mean() / (skin * gain / gain.mean()).mean())
gain = 1 + k * (gain - 1)
out = np.clip(a * gain, 0, 255).astype(np.uint8)
ImageEnhance.Color(Image.fromarray(out)).enhance(sat).save(dst, quality=94)
print(dst, "skin", np.round(skin), "gain", np.round(gain, 3))
