#!/usr/bin/env bash
# Download the Falafel sherpa-onnx int8 builds into ./models. Gated (auto-approve) on Hugging Face: needs HF_TOKEN.
# Usage: with-secrets scripts/fetch-models.sh
set -euo pipefail
cd "$(dirname "$0")/.."
get() { # repo dest
  mkdir -p "models/$2"
  for f in encoder.int8.onnx decoder.int8.onnx joiner.int8.onnx tokens.txt version.json; do
    curl -fsSL -H "Authorization: Bearer ${HF_TOKEN}" -o "models/$2/$f" "https://huggingface.co/$1/resolve/main/$f"
  done
}
get Hebrish/Falafel-sherpa-onnx-int8 falafel
get Hebrish/Falafel-Parakeet-110M-sherpa-onnx-int8 falafel-110m
ls -la models/*
