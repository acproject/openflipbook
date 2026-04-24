@echo off
echo ========================================
echo Starting llama.cpp server
echo ========================================
echo.
echo Please make sure you have:
echo 1. Downloaded llama.cpp from https://github.com/ggerganov/llama.cpp
echo 2. Downloaded a model (e.g., qwen2.5-7b-instruct-q4_k_m.gguf)
echo.
echo Example command:
echo server.exe -m models\qwen2.5-7b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8080 -c 4096
echo.
echo For vision model (Qwen2.5-VL):
echo server.exe -m models\qwen2.5-vl-7b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8081 -c 4096 --mmproj models\qwen2.5-vl-7b-mmproj.gguf
echo.
pause
