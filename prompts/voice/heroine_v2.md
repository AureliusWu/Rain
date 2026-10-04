# heroine_voice_v2 — v0.6 key dialogue

Preserve the existing adult heroine voice: Kokoro-82M v1.1-zh ONNX int8,
kokoro-onnx 0.6.1, misaki 0.9.4 ZHG2P(version="1.1"), zf_001, speed 0.95.
Use the exact Chinese text bound to each line_id in voice_manifest.json.
No real-person voice cloning, additional words or reading of identifiers.

Cover the letter response, both trust branches, a restrained emotional response,
the heroine's boundaries, the repaired relationship and both endings. These are
selected key lines, not a full-voice edition. Preserve all six v0.2 recordings.

Direction: clear, calm adult female delivery. Emotion labels describe scene
direction only; this model receives no emotion-conditioning input. Fixed voice
and speed keep consistency across scenes. Final sound choice awaits user review.

Save PCM_16 24kHz mono WAV and encode Vorbis OGG. Apply only short edge fades
and a peak ceiling when needed; measure decoded signal levels and text binding.
Keep inference dependencies and pinned models outside the player package.
