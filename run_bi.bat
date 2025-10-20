@echo off
title 📊 Analista BI Local - 100% Offline

echo Iniciando Sistema de BI Local...
echo.

:: Mudar para o diretório onde estão os arquivos Python
cd /d "C:\BI LLM"

echo 🔹 Verificando arquivos Python...
if not exist "app.py" (
    echo ❌ Arquivo app.py não encontrado em:
    echo %CD%
    echo.
    echo 📁 Certifique-se de que estes arquivos estão na pasta:
    echo - app.py
    echo - agent_bi.py  
    echo - config.py
    pause
    exit
)

echo 🔹 Verificando Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama não encontrado. Execute install.bat primeiro.
    pause
    exit
)

echo 🔹 Verificando modelo Llama...
ollama list | findstr "llama3.1" >nul
if errorlevel 1 (
    echo ❌ Modelo llama3.1 não encontrado. Execute: ollama pull llama3.1:8b
    pause
    exit
)

echo 🔹 Ativando ambiente virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Ambiente virtual não encontrado!
    echo 📁 Verifique se a pasta venv ou .venv existe em: %CD%
    pause
    exit
)

echo 🔹 Iniciando Interface Web...
streamlit run app.py

echo.
echo ✅ Sistema finalizado.
pause