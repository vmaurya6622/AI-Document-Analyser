@echo off
echo Starting LLaMA 3 model with Ollama...
start "" /B cmd /C "ollama run llama3"

timeout /t 5 >nul

echo Starting local Python server on port 5500...
start "" /B cmd /C "python app.py"

timeout /t 2 >nul

echo Opening browser at http://localhost:5500...
start http://127.0.0.1:5000/

exit
