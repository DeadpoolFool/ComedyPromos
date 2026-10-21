# meme-dub

Takes a meme clip and a voice note from Artem, and gives back the meme with his face on the subject, his voice, lips synced to it, and his line as the burned-in caption. The caption is the hook, so it's whatever he says.

First one: Bernie's "I am once again asking..." → "I am once again asking you to support my stand-up career." (`out/bernie-once-again.mp4`).

## Making one

1. Get the meme clip (mp4/mov, one clear face, ideally front-on and under ~10s).
2. Artem records the line as a voice note. Dead air at the start and end is trimmed, so no need to be precise.
3. Run:

```bash
python meme_dub.py --clip bernie.mov --voice take1.m4a --face face.jpg \
    --erase-box 100,565,520,110 --out out/bernie-once-again.mp4
```

| Flag | What it does |
|---|---|
| `--face` | Photos of Artem, or a folder of them. Use the face kit: `--face /mnt/project-files/photos/face-kit`. Every photo in it gets blended into one identity, which looks more like him than any single shot. |
| `--erase-box x,y,w,h` | Box around the clip's old caption, in pixels. White text inside it is painted out. Leave it off when the clip has no caption. |
| `--caption "..."` | Use this text instead of the transcript (to fix a word or punch up the wording). |
| `--caption-y 0.86` | Caption center as a fraction of the height. 0.86 sits where most meme captions are. |
| `--no-caption` | Skip the caption. |
| `--lip-model` | `edtalk_256` (default, sharper mouth) or `wav2lip_gan_96` (the older 96px model). |
| `--lip-weight` | Mouth movement strength, 0 to 1. Default 1.0; FaceFusion's own default of 0.5 looked mumbled. |
| `--lip-lead-ms` | Timing correction for the lip-sync model. Default 133 (4 frames at 30 fps). |
| `--keep` | Keep the work folder (trimmed voice, fitted clip, cleaned clip) for debugging. |

If the voice runs longer than the clip, the clip plays forward then backward until it's long enough. If it's shorter, the clip is cut to the voice.

Finding the erase box: grab a frame with `ffmpeg -ss 1 -i clip.mov -frames:v 1 frame.png`, look at where the caption sits, and pad it by ~10px.

## What it does

1. Trims leading and trailing silence off the voice note (ffmpeg `silencedetect`).
2. Fits the clip to the voice length.
3. Inpaints the old caption out (OpenCV).
4. Swaps Artem's face in (inswapper_128), lip-syncs to the voice (EDTalk 256 at full strength) and cleans up the face (GFPGAN 1.4), all via [FaceFusion](https://github.com/facefusion/facefusion). The lip-sync models open the mouth about 4 frames before the sound, so the script feeds them the voice delayed by 133 ms and muxes the undelayed voice back in.
5. Transcribes the voice note first thing (Whisper small.en via sherpa-onnx) and prints it as `caption: ...`. Whisper sometimes mishears a word ("stand of career"), so check that line and rerun with `--caption` if needed.
6. Burns the caption in white Inter Bold with a soft shadow, two balanced lines, and muxes the audio.

## Setup

```bash
git clone --depth 1 https://github.com/facefusion/facefusion.git meme-dub/facefusion
pip install -r meme-dub/facefusion/requirements.txt -r meme-dub/requirements.txt
```

FaceFusion downloads its models from GitHub on the first run. The Whisper model (~600 MB) downloads into `meme-dub/.models/` on the first transcription. Both folders are gitignored.

On CPU a 5-second 720×720 clip takes about 12 minutes, mostly the face enhancer. A GPU cuts that to under a minute.

## Notes

- The swap keeps the meme subject's hair and glasses and takes Artem's face and beard. On Bernie that's the joke. On a subject with a very different head shape it can look off, so check a frame before posting.
- Wav2lip only redraws the mouth at 96px and looked blurry under Artem's beard; EDTalk works at 256px.
- To check sync without eyeballing it: track the inner-lip gap per frame (insightface 68-point landmarks, points 62 and 66) and correlate it with the audio loudness per frame. The peak should sit at lag 0. The first Bernie cut peaked at -4 frames, which is why it looked off.
- Posting: these are reels. Post the clip as-is (square is fine) and put the hook in the first line of the IG caption too.

## Face kit

`/mnt/project-files/photos/face-kit/` holds the 14 photos that make up Artem's face for every meme: 8 front-on selfies (eyes level, mouth closed, 300-450px faces) and 6 LBC stage shots turned less than 20 degrees from camera (stage light, mid-talk). `identity.npy` is their averaged ArcFace embedding, and `kit.json` lists each photo's similarity to it, all between 0.83 and 0.91.

To add a photo, it should be front-on (under ~20 degrees of turn), sharp, with only his face in frame and a face at least ~150px wide. Drop it in the folder. The script picks up the whole folder. Leave out sunglasses, heavy shadow and shirtless shots. LBC shots 103 and 104 caught another comic, so they're excluded.
