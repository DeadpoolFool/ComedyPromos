#!/usr/bin/env python3
"""Score how much a rendered meme looks like Artem: python likeness.py identity.npy out.mp4

Prints the mean and min ArcFace similarity of the face in every 6th frame to the kit identity.
The Bernie cut scored 0.73 with one photo and 0.82 with the 14-photo kit."""
import sys, cv2, numpy as np
from insightface.app import FaceAnalysis
fa=FaceAnalysis(name="buffalo_l",allowed_modules=["detection","recognition"],providers=["CPUExecutionProvider"]); fa.prepare(ctx_id=-1,det_size=(640,640))
m=np.load(sys.argv[1])
for p in sys.argv[2:]:
    cap=cv2.VideoCapture(p); sims=[]; i=0
    while True:
        ok,f=cap.read()
        if not ok: break
        if i%6==0:
            fs=fa.get(f)
            if fs: sims.append(float(max(fs,key=lambda x:x.bbox[2]-x.bbox[0]).normed_embedding@m))
        i+=1
    print(p.split("/")[-1], "mean", round(np.mean(sims),3), "min", round(np.min(sims),3), "n", len(sims))
