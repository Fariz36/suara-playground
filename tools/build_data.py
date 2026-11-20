"""Build demo/data.js from the team's comparison.csv (+ tools/extra_clips.csv) and the WAVs in demo/audio.
Precomputes waveform peaks so the page needs no backend.
Usage: python -I tools/build_data.py <dir with comparison.csv> data.js"""
import csv, json, sys, wave
from pathlib import Path
import numpy as np

SRC = Path(sys.argv[1]); OUT = Path(sys.argv[2]); DEMO = OUT.resolve().parent
rows = list(csv.DictReader((DEMO / "tools/extra_clips.csv").open(encoding="utf-8")))
rows += list(csv.DictReader((SRC / "comparison.csv").open(encoding="utf-8-sig")))
clips = []
for r in rows:
    wav = DEMO / "audio" / Path(r["audio"]).name
    with wave.open(str(wav)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; sr = w.getframerate()
    pk = np.array([s.max() if len(s) else 0 for s in np.array_split(np.abs(x), 96)])
    clips.append(dict(id=r["clip"], audio="audio/" + wav.name, expected=r["expected"],
        baseline=r["whisper_baseline"], suara=r["suara_lora"],
        baseline_ok=r["baseline_exact"] == "1", suara_ok=r["suara_exact"] == "1",
        seconds=round(len(x) / sr, 2), peaks=(pk / (pk.max() or 1)).round(3).tolist()))
OUT.write_text("window.SUARA_CLIPS = " + json.dumps(clips, ensure_ascii=False) + ";\n")
print(len(clips), "clips", OUT.stat().st_size // 1024, "KB")
