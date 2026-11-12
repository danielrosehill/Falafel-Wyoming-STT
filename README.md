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

## Measured (residencehome, 16-core CPU, no GPU, 2026-11-12)

Falafel 0.6B int8, 8 threads. Input was Kokoro-generated speech, so this checks plumbing and speed, not accuracy on a
real voice in a room.

| Audio | Decode | Transcript |
|---|---|---|
| 3.01 s | 0.12 s | Turn the living room AC up to 24 degrees. |
| 2.71 s | 0.15 s | Send an email to Hannah saying I will be home late. |
| 3.20 s | 0.14 s | Create a new private repo called Voice Agent Tests. |
| 1.73 s | 0.17 s | What's on my calendar tomorrow. |

## Deployment (Daniel's)

- residencehome stack `falafel-wyoming` in `~/deployments` (submodule of Residencehome-Deployments), `10.0.0.2:10300`,
  LAN only, no auth. Models fetched on the host with `with-secrets scripts/fetch-models.sh` (HF_TOKEN from Infisical).
- Home Assistant 10.0.0.3: Wyoming entry `falafel` (entity `stt.falafel`), added 2026-11-12. Used by the pipeline
  "Hey Yossi" (id `01m789tt8jbtvqv9y23bq8e217`): stt.falafel → conversation → tts.kokoro.
- Part of the voice pipeline in [Hey-Yossi-Voice-Satellite](https://github.com/danielrosehill/Hey-Yossi-Voice-Satellite)
  (private).
