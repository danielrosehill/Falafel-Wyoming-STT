# Falafel-Wyoming-STT

A Wyoming speech-to-text server for [Falafel](https://huggingface.co/Hebrish/Falafel), the Hebrish voice-command
ASR model (Parakeet TDT, sherpa-onnx int8). It lets Home Assistant Assist, or any Wyoming client, use Falafel as its
speech-to-text engine. Created 2026-11-12.

Audio in, text out. Deciding what to do with the text is the job of the agent behind it, not this server.

## Run

```bash
with-secrets scripts/fetch-models.sh   # needs HF_TOKEN; the models are gated with automatic approval
docker compose up -d --build
```

- Port `10300`, bound in `docker-compose.yml` (edit the host IP for your machine).
- Default model: Falafel 0.6B int8 (`models/falafel`). For the 110M build, pass `--model-dir /models/falafel-110m`.
- Home Assistant: Settings > Devices & services > Add integration > Wyoming Protocol, host and port of this server.
  Then pick it as the speech-to-text engine in a voice assistant pipeline.

## Test

```bash
uv run --with wyoming scripts/test_client.py HOST 10300 sample.wav
```
