#!/bin/bash

MODEL_DIR="model"
MODEL_FILE="$MODEL_DIR/qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

# Create model directory if not exists
mkdir -p "$MODEL_DIR"

# Skip download if file already exists
if [ -f "$MODEL_FILE" ]; then
    echo "Model already exists at $MODEL_FILE — skipping download."
    exit 0
fi

echo "Downloading model..."
curl -L "$MODEL_URL" -o "$MODEL_FILE"

echo "Done. Model saved to $MODEL_FILE"