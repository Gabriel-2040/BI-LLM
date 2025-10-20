# Configuração do seu PostgreSQL existente
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "bi_dw",  # Se não existir, crie: CREATE DATABASE bi_dw;
    "username": "postgres",  # Seu usuário PostgreSQL
    "password": ""  # SUA SENHA REAL DO POSTGRES
}

# ⭐⭐ NOVA CONFIGURAÇÃO DO MODELO OLLAMA ⭐⭐
OLLAMA_CONFIG = {
    "modelo_padrao": "llama3.2:3b",  # ⚡ ALTERE AQUI O MODELO!
    "modelo_rapido": "llama3.2:3b",
    "modelo_completo": "llama3.1:8b",
    "timeout": 120
}