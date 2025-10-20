@echo off
echo 📊 Instalando Analista de BI Local 100% Offline...
echo.

echo 🔹 Etapa 1/5: Baixando Ollama...
powershell -Command "Invoke-WebRequest -Uri https://ollama.com/download/OllamaSetup.exe -OutFile OllamaSetup.exe"
echo Aguarde a instalacao do Ollama...
start /wait OllamaSetup.exe
timeout /t 10

echo 🔹 Etapa 2/5: Baixando modelo Llama 3.1 8B...
ollama pull llama3.1:8b

@REM echo 🔹 Etapa 3/5: Instalando PostgreSQL...
@REM powershell -Command "Invoke-WebRequest -Uri https://get.enterprisedb.com/postgresql/postgresql-16.2-1-windows-x64-binaries.zip -OutFile postgres.zip"
@REM mkdir postgres
@REM tar -xf postgres.zip -C postgres --strip-components=1

@REM echo 🔹 Etapa 4/5: Configurando PostgreSQL...
@REM cd postgres
@REM bin\initdb.exe -D data -U postgres -W postgres123
@REM bin\pg_ctl.exe -D data start
@REM timeout /t 5
@REM bin\createdb.exe -U postgres bi_dw
@REM cd ..

echo 🔹 Etapa 5/5: Instalando dependencias Python...
pip install pandas sqlalchemy psycopg2-binary matplotlib streamlit ollama

echo.
echo ✅ Instalacao concluida! 
echo 🚀 Execute 'run_bi.bat' para iniciar o sistema.
pause