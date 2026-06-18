import sys, time
from faster_whisper import WhisperModel

AUDIO = r"C:\Users\tbeng\Downloads\_aw_test_frames\audio16k.wav"
OUT_TXT = r"C:\Users\tbeng\Downloads\_aw_test_frames\transcript.txt"
OUT_SRT = r"C:\Users\tbeng\Downloads\_aw_test_frames\transcript.srt"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "small.en"

def ts(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

def srt_ts(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60); ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

print(f"Loading model '{MODEL}' (CPU int8)...", flush=True)
t0 = time.time()
model = WhisperModel(MODEL, device="cpu", compute_type="int8")
print(f"Model loaded in {time.time()-t0:.1f}s. Transcribing...", flush=True)

segments, info = model.transcribe(
    AUDIO, language="en", vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
    beam_size=5,
)
print(f"Detected language: {info.language} (p={info.language_probability:.2f}), "
      f"duration: {info.duration:.0f}s", flush=True)

with open(OUT_TXT, "w", encoding="utf-8") as ft, open(OUT_SRT, "w", encoding="utf-8") as fs:
    n = 0
    for seg in segments:
        n += 1
        line = f"[{ts(seg.start)} -> {ts(seg.end)}] {seg.text.strip()}"
        ft.write(line + "\n"); ft.flush()
        fs.write(f"{n}\n{srt_ts(seg.start)} --> {srt_ts(seg.end)}\n{seg.text.strip()}\n\n"); fs.flush()
        if n % 25 == 0:
            print(f"  ...{n} segments, t={seg.end:.0f}s", flush=True)
print(f"DONE: {n} segments in {time.time()-t0:.1f}s -> {OUT_TXT}", flush=True)
