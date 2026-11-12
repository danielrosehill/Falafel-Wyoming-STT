"""Send a WAV file to a Wyoming ASR server and print the transcript and round-trip time.
Usage: uv run --with wyoming scripts/test_client.py HOST PORT file.wav
"""
import asyncio, sys, time, wave
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.client import AsyncTcpClient

async def main(host, port, path):
    with wave.open(path) as w:
        rate, width, ch, data = w.getframerate(), w.getsampwidth(), w.getnchannels(), w.readframes(w.getnframes())
    async with AsyncTcpClient(host, int(port)) as c:
        t0 = time.monotonic()
        await c.write_event(Transcribe().event())
        await c.write_event(AudioStart(rate=rate, width=width, channels=ch).event())
        step = rate * width * ch // 10
        for i in range(0, len(data), step):
            await c.write_event(AudioChunk(rate=rate, width=width, channels=ch, audio=data[i:i+step]).event())
        await c.write_event(AudioStop().event())
        while True:
            ev = await c.read_event()
            if ev and Transcript.is_type(ev.type):
                print(f"{time.monotonic()-t0:.2f}s  {Transcript.from_event(ev).text!r}")
                return

asyncio.run(main(*sys.argv[1:4]))
