"""Wyoming speech-to-text server for Falafel (Parakeet TDT, sherpa-onnx int8 transducer).

Audio in, text out. Home Assistant (or any Wyoming client) sends AudioStart/AudioChunk/AudioStop,
gets back one Transcript.
"""

import argparse
import asyncio
import logging
import time
from functools import partial
from pathlib import Path

import numpy as np
import sherpa_onnx
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioChunkConverter, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import AsrModel, AsrProgram, Attribution, Describe, Info
from wyoming.server import AsyncEventHandler, AsyncServer

_LOGGER = logging.getLogger("falafel_wyoming")
RATE = 16000


def load_recognizer(model_dir: Path, threads: int) -> sherpa_onnx.OfflineRecognizer:
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(model_dir / "encoder.int8.onnx"),
        decoder=str(model_dir / "decoder.int8.onnx"),
        joiner=str(model_dir / "joiner.int8.onnx"),
        tokens=str(model_dir / "tokens.txt"),
        model_type="nemo_transducer",
        num_threads=threads,
        sample_rate=RATE,
        feature_dim=80,
        decoding_method="greedy_search",
    )


class FalafelHandler(AsyncEventHandler):
    def __init__(self, info: Info, recognizer, lock: asyncio.Lock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = info
        self.recognizer = recognizer
        self.lock = lock
        self.converter = AudioChunkConverter(rate=RATE, width=2, channels=1)
        self.audio = bytearray()

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.info.event())
            return True
        if Transcribe.is_type(event.type) or AudioStart.is_type(event.type):
            if AudioStart.is_type(event.type):
                self.audio = bytearray()
            return True
        if AudioChunk.is_type(event.type):
            chunk = self.converter.convert(AudioChunk.from_event(event))
            self.audio.extend(chunk.audio)
            return True
        if AudioStop.is_type(event.type):
            samples = np.frombuffer(bytes(self.audio), dtype=np.int16).astype(np.float32) / 32768.0
            self.audio = bytearray()
            t0 = time.monotonic()
            async with self.lock:
                text = await asyncio.get_running_loop().run_in_executor(None, self._decode, samples)
            _LOGGER.info("%.2fs audio -> %.2fs decode: %r", len(samples) / RATE, time.monotonic() - t0, text)
            await self.write_event(Transcript(text=text).event())
            return False
        return True

    def _decode(self, samples: np.ndarray) -> str:
        stream = self.recognizer.create_stream()
        stream.accept_waveform(RATE, samples)
        self.recognizer.decode_stream(stream)
        return stream.result.text.strip()


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--uri", default="tcp://0.0.0.0:10300")
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--model-name", default="falafel")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--debug", action="store_true")
    a = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if a.debug else logging.INFO)

    recognizer = load_recognizer(a.model_dir, a.threads)
    info = Info(
        asr=[
            AsrProgram(
                name="falafel",
                description="Falafel voice-command ASR (Parakeet TDT, sherpa-onnx)",
                attribution=Attribution(name="Hebrish", url="https://huggingface.co/Hebrish"),
                installed=True,
                version="1.0",
                models=[
                    AsrModel(
                        name=a.model_name,
                        description=a.model_name,
                        attribution=Attribution(name="Hebrish", url="https://huggingface.co/Hebrish"),
                        installed=True,
                        languages=["en"],
                        version="1.0",
                    )
                ],
            )
        ]
    )
    _LOGGER.info("Loaded %s, listening on %s", a.model_dir, a.uri)
    server = AsyncServer.from_uri(a.uri)
    await server.run(partial(FalafelHandler, info, recognizer, asyncio.Lock()))


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
