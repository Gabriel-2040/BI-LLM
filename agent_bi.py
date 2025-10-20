import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, inspect
import matplotlib.pyplot as plt
import streamlit as st
import tempfile
import os
import ollama
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# --- Configuração ---
from config import DB_CONFIG, OLLAMA_CONFIG

# ⭐⭐ VERIFICAÇÃO DOS MODELOS ⭐⭐
MODELO_ATUAL = OLLAMA_CONFIG["modelo_padrao"]
MODELO_RAPIDO = OLLAMA_CONFIG["modelo_rapido"]
MODELO_COMPLETO = OLLAMA_CONFIG["modelo_completo"]

# Debug: mostra qual modelo está sendo usado
print(f"🎯 MODELO CONFIGURADO: {MODELO_ATUAL}")

# --- Conexão com Banco ---
def get_engine():
    """Cria conexão com PostgreSQL local"""
    if DB_CONFIG["password"]:
        connection_string = f"postgresql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    else:
        connection_string = f"postgresql://{DB_CONFIG['username']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_string)

# --- Função Principal de Consulta ---
def consultar_ollama_local(prompt: str, contexto: Dict = None, modelo_especifico: str = None) -> str:
    """Consulta o modelo Ollama configurado - VERSÃO CORRIGIDA"""
    
    # ⭐⭐ SEMPRE usa o modelo especificado ou o padrão do config.py ⭐⭐
    modelo_usar = modelo_especifico if modelo_especifico else MODELO_ATUAL
    
    # Força phi3:mini se ainda estiver usando outro
    if modelo_usar != "phi3:mini":
        modelo_usar = "phi3:mini"
    
    try:
        # Prompt otimizado
        if contexto:
            prompt_completo = f"""
            CONTEXTO DOS DADOS:
            {json.dumps(contexto, indent=2, ensure_ascii=False)}
            
            TAREFA:
            {prompt}
            
            RESPOSTA: Seja conciso e direto ao ponto.
            """
        else:
            prompt_completo = prompt
            
        st.info(f"🤖 Consultando {modelo_usar}...")
        
        resposta = ollama.chat(
            model=modelo_usar,  # ⬅️ AGORA usa phi3:mini
            messages=[{"role": "user", "content": prompt_completo}],
            options={'num_predict': 500, 'temperature': 0.1}
        )
        return resposta["message"]["content"]
    except Exception as e:
        return f"❌ Erro ao consultar {modelo_usar}: {str(e)}"

# ============================================================================
# 1. 🎯 ORQUESTRADOR PRINCIPAL
# ============================================================================

def orquestrar_acao(pergunta_usuario: str, caminhos_csv: List[str]) -> str:
    """Orquestra a ação baseada na pergunta do usuário"""
    
    pergunta = pergunta_usuario.lower()
    contexto_csv = obter_contexto_csv(caminhos_csv)
    
    # Análise da intenção usando LLM
    intencao = analisar_intencao(pergunta_usuario, contexto_csv)
    
    st.info(f"🎯 Ação detectada: {intencao['acao_principal']}")
    
    # Executa a ação correspondente
    if intencao['acao_principal'] == 'analise_exploratoria':
        return executar_analise_exploratoria(caminhos_csv, pergunta_usuario)
    
    elif intencao['acao_principal'] == 'criar_dw':
        return executar_criacao_dw(caminhos_csv, pergunta_usuario)
    
    elif intencao['acao_principal'] == 'consultas_sql':
        return executar_consultas_sql(caminhos_csv, pergunta_usuario)
    
    elif intencao['acao_principal'] == 'ddl_operations':
        return executar_operacoes_ddl(pergunta_usuario)
    
    elif intencao['acao_principal'] == 'dml_operations':
        return executar_operacoes_dml(caminhos_csv, pergunta_usuario)
    
    elif intencao['acao_principal'] == 'visualizacao':
        return executar_visualizacao(caminhos_csv, pergunta_usuario)
    
    elif intencao['acao_principal'] == 'relatorios':
        return executar_relatorios(caminhos_csv, pergunta_usuario)
    
    else:
        return processo_padrao_bi(caminhos_csv, pergunta_usuario)

def analisar_intencao(pergunta: str, contexto_csv: Dict) -> Dict:
    """Usa LLM para analisar a intenção do usuário"""
    
    prompt_intencao = f"""
    Analise a pergunta do usuário e classifique a intenção principal.

    PERGUNTA: "{pergunta}"
    
    CONTEXTO DOS DADOS: {json.dumps(contexto_csv, indent=2)}
    
    CLASSIFIQUE em uma destas categorias:
    
    1. analise_exploratoria - Para explorar dados: ver colunas, amostras, estatísticas básicas
    2. criar_dw - Para criar data warehouse: modelagem, tabelas, ETL
    3. consultas_sql - Para executar queries SELECT, filtros, agregações
    4. ddl_operations - Para operações DDL: CREATE, ALTER, DROP tabelas
    5. dml_operations - Para operações DML: INSERT, UPDATE, DELETE dados
    6. visualizacao - Para criar gráficos, dashboards, visualizações
    7. relatorios - Para gerar relatórios estruturados, análises complexas
    
    Responda APENAS com JSON, nada mais:
    {{
        "acao_principal": "nome_da_categoria",
        "confianca": 0.9,
        "detalhes": "explicacao"
    }}
    """
    
    try:
        # ✅ FORÇA usar phi3:mini
        resposta = consultar_ollama_local(prompt_intencao, contexto_csv, "phi3:mini")
        return json.loads(resposta)
    except:
        return analisar_intencao_fallback(pergunta)

def analisar_intencao_fallback(pergunta: str) -> Dict:
    """Fallback para análise de intenção baseada em palavras-chave"""
    pergunta = pergunta.lower()
    
    if any(palavra in pergunta for palavra in ['coluna', 'estrutura', 'amostra', 'analise', 'exploratória']):
        return {"acao_principal": "analise_exploratoria", "confianca": 0.8, "detalhes": "Análise exploratória detectada"}
    
    elif any(palavra in pergunta for palavra in ['dw', 'data warehouse', 'modelo', 'etl', 'carregar']):
        return {"acao_principal": "criar_dw", "confianca": 0.9, "detalhes": "Criação de DW detectada"}
    
    elif any(palavra in pergunta for palavra in ['select', 'query', 'consultar', 'filtrar', 'agrupar']):
        return {"acao_principal": "consultas_sql", "confianca": 0.85, "detalhes": "Consulta SQL detectada"}
    
    elif any(palavra in pergunta for palavra in ['create', 'alter', 'drop', 'tabela', 'índice']):
        return {"acao_principal": "ddl_operations", "confianca": 0.9, "detalhes": "Operação DDL detectada"}
    
    elif any(palavra in pergunta for palavra in ['insert', 'update', 'delete', 'atualizar', 'incluir']):
        return {"acao_principal": "dml_operations", "confianca": 0.9, "detalhes": "Operação DML detectada"}
    
    elif any(palavra in pergunta for palavra in ['gráfico', 'grafico', 'visualizar', 'dashboard', 'chart']):
        return {"acao_principal": "visualizacao", "confianca": 0.8, "detalhes": "Visualização detectada"}
    
    elif any(palavra in pergunta for palavra in ['relatório', 'relatorio', 'report', 'análise', 'analise']):
        return {"acao_principal": "relatorios", "confianca": 0.8, "detalhes": "Relatório detectado"}
    
    else:
        return {"acao_principal": "processo_padrao", "confianca": 0.6, "detalhes": "Intenção não clara, usando processo padrão"}

# ============================================================================
# 2. 📊 ANÁLISE EXPLORATÓRIA
# ============================================================================

def executar_analise_exploratoria(caminhos_csv: List[str], pergunta: str) -> str:
    """Executa análise exploratória completa dos dados"""
    
    resultados = []
    for caminho in caminhos_csv:
        try:
            df = pd.read_csv(caminho)
            nome_arquivo = os.path.basename(caminho)
            
            analise = {
                "arquivo": nome_arquivo,
                "colunas": list(df.columns),
                "tipos_dados": df.dtypes.astype(str).to_dict(),
                "total_linhas": len(df),
                "total_colunas": len(df.columns),
                "valores_nulos": df.isnull().sum().to_dict(),
                "amostra_dados": df.head(3).to_dict('records')
            }
            resultados.append(analise)
            
        except Exception as e:
            resultados.append({"arquivo": os.path.basename(caminho), "erro": str(e)})
    
    return gerar_relatorio_analise_exploratoria(resultados, pergunta)

def gerar_relatorio_analise_exploratoria(resultados: List[Dict], pergunta: str) -> str:
    """Gera relatório completo da análise exploratória"""
    
    relatorio = f"## 📊 RELATÓRIO DE ANÁLISE EXPLORATÓRIA\n\n"
    relatorio += f"**Pergunta:** {pergunta}\n\n"
    
    for analise in resultados:
        if "erro" in analise:
            relatorio += f"### ❌ {analise['arquivo']}\n"
            relatorio += f"**Erro:** {analise['erro']}\n\n"
            continue
            
        relatorio += f"### 📁 {analise['arquivo']}\n"
        relatorio += f"**📈 Dimensões:** {analise['total_linhas']} linhas × {analise['total_colunas']} colunas\n\n"
        
        # Colunas e tipos
        relatorio += "**📋 Estrutura das Colunas:**\n"
        for coluna, tipo in analise['tipos_dados'].items():
            nulos = analise['valores_nulos'][coluna]
            relatorio += f"- `{coluna}`: {tipo} | Nulos: {nulos}\n"
        
        # Amostra de dados
        relatorio += f"\n**👀 Amostra de Dados (3 primeiras linhas):**\n"
        relatorio += "```\n"
        df_amostra = pd.DataFrame(analise['amostra_dados'])
        relatorio += df_amostra.to_string(index=False) + "\n"
        relatorio += "```\n\n"
    
    return relatorio

# ============================================================================
# 3. 🗄️ DATA WAREHOUSE
# ============================================================================

def executar_criacao_dw(caminhos_csv: List[str], pergunta: str) -> str:
    """Executa criação de Data Warehouse"""
    
    contexto_csv = obter_contexto_csv(caminhos_csv)
    
    # Carrega dados para staging
    tabelas_carregadas = []
    for i, caminho in enumerate(caminhos_csv):
        df = pd.read_csv(caminho)
        nome_tabela = f"stg_{os.path.basename(caminho).replace('.csv', '').lower()}"
        df.to_sql(nome_tabela, get_engine(), if_exists='replace', index=False)
        tabelas_carregadas.append(nome_tabela)
    
    # Gera modelo DW com LLM
    prompt_dw = f"""
    CONTEXTO DOS DADOS:
    {json.dumps(contexto_csv, indent=2)}
    
    PERGUNTA: {pergunta}
    
    Crie um modelo de Data Warehouse estrela com:
    1. Tabelas de fato e dimensões
    2. Chaves primárias e estrangeiras
    3. Scripts SQL completos
    
    TABELAS CARREGADAS: {tabelas_carregadas}
    """
    
    resposta_llm = consultar_ollama_local(prompt_dw, {})
    
    # Extrai e executa SQL
    scripts_sql = extrair_scripts_sql(resposta_llm)
    resultados_execucao = executar_scripts_sql(scripts_sql)
    
    relatorio = f"## 🗄️ DATA WAREHOUSE CRIADO\n\n"
    relatorio += f"**Pergunta:** {pergunta}\n\n"
    relatorio += f"**Tabelas Carregadas:** {', '.join(tabelas_carregadas)}\n\n"
    relatorio += f"**Modelo Proposto:**\n{resposta_llm}\n\n"
    relatorio += f"**Resultados da Execução:**\n{resultados_execucao}\n"
    
    return relatorio

# ============================================================================
# 4. 🔍 CONSULTAS SQL
# ============================================================================

def executar_consultas_sql(caminhos_csv: List[str], pergunta: str) -> str:
    """Executa consultas SQL baseadas na pergunta"""
    
    # Primeiro carrega os CSVs se necessário
    if caminhos_csv:
        for caminho in caminhos_csv:
            df = pd.read_csv(caminho)
            nome_tabela = f"consulta_{os.path.basename(caminho).replace('.csv', '').lower()}"
            df.to_sql(nome_tabela, get_engine(), if_exists='replace', index=False)
    
    # Gera consulta SQL com LLM
    prompt_consulta = f"""
    Baseado na pergunta: "{pergunta}"
    
    Gere uma consulta SQL otimizada para PostgreSQL.
    Inclua comentários explicativos.
    
    TABELAS DISPONÍVEIS: {obter_tabelas_banco()}
    """
    
    resposta_llm = consultar_ollama_local(prompt_consulta, {})
    consulta_sql = extrair_script_sql_unico(resposta_llm)
    
    if consulta_sql:
        resultado = executar_sql(consulta_sql)
        
        relatorio = f"## 🔍 CONSULTA SQL EXECUTADA\n\n"
        relatorio += f"**Pergunta:** {pergunta}\n\n"
        relatorio += f"**Consulta SQL:**\n```sql\n{consulta_sql}\n```\n\n"
        relatorio += f"**Resultado:**\n```\n{resultado}\n```\n\n"
        relatorio += f"**Explicação do LLM:**\n{resposta_llm}\n"
        
        return relatorio
    else:
        return f"❌ Não foi possível gerar consulta SQL para: {pergunta}"

# ============================================================================
# 5. ⚙️ OPERAÇÕES DDL
# ============================================================================

def executar_operacoes_ddl(pergunta: str) -> str:
    """Executa operações DDL (CREATE, ALTER, DROP)"""
    
    prompt_ddl = f"""
    PERGUNTA: "{pergunta}"
    
    TABELAS EXISTENTES: {obter_tabelas_banco()}
    
    Gere comandos DDL (CREATE, ALTER, DROP) para PostgreSQL.
    Inclua apenas os comandos SQL necessários.
    """
    
    resposta_llm = consultar_ollama_local(prompt_ddl, {})
    scripts_sql = extrair_scripts_sql(resposta_llm)
    resultados_execucao = executar_scripts_sql(scripts_sql)
    
    relatorio = f"## ⚙️ OPERAÇÕES DDL EXECUTADAS\n\n"
    relatorio += f"**Pergunta:** {pergunta}\n\n"
    relatorio += f"**Comandos Gerados:**\n```sql\n{resposta_llm}\n```\n\n"
    relatorio += f"**Resultados:**\n{resultados_execucao}\n"
    
    return relatorio

# ============================================================================
# 6. 🔄 OPERAÇÕES DML
# ============================================================================

def executar_operacoes_dml(caminhos_csv: List[str], pergunta: str) -> str:
    """Executa operações DML (INSERT, UPDATE, DELETE)"""
    
    contexto_csv = obter_contexto_csv(caminhos_csv) if caminhos_csv else {}
    
    prompt_dml = f"""
    PERGUNTA: "{pergunta}"
    
    CONTEXTO: {json.dumps(contexto_csv, indent=2)}
    TABELAS EXISTENTES: {obter_tabelas_banco()}
    
    Gere comandos DML (INSERT, UPDATE, DELETE) para PostgreSQL.
    Inclua apenas os comandos SQL necessários.
    """
    
    resposta_llm = consultar_ollama_local(prompt_dml, {})
    scripts_sql = extrair_scripts_sql(resposta_llm)
    resultados_execucao = executar_scripts_sql(scripts_sql)
    
    relatorio = f"## 🔄 OPERAÇÕES DML EXECUTADAS\n\n"
    relatorio += f"**Pergunta:** {pergunta}\n\n"
    relatorio += f"**Comandos Gerados:**\n```sql\n{resposta_llm}\n```\n\n"
    relatorio += f"**Resultados:**\n{resultados_execucao}\n"
    
    return relatorio

# ============================================================================
# 7. 📈 VISUALIZAÇÃO
# ============================================================================

def executar_visualizacao(caminhos_csv: List[str], pergunta: str) -> str:
    """Executa criação de visualizações e gráficos"""
    
    if not caminhos_csv:
        return "❌ É necessário fazer upload de CSV para visualizações"
    
    df = pd.read_csv(caminhos_csv[0])
    nome_arquivo = os.path.basename(caminhos_csv[0])
    
    # Tenta gerar gráfico básico
    try:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        if len(df.select_dtypes(include=[np.number]).columns) >= 2:
            # Gráfico de dispersão se tiver colunas numéricas
            x_col = df.select_dtypes(include=[np.number]).columns[0]
            y_col = df.select_dtypes(include=[np.number]).columns[1]
            ax.scatter(df[x_col], df[y_col])
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'{x_col} vs {y_col}')
        
        elif len(df.select_dtypes(include=[np.number]).columns) == 1:
            # Histograma se tiver uma coluna numérica
            col_num = df.select_dtypes(include=[np.number]).columns[0]
            ax.hist(df[col_num].dropna(), bins=10)
            ax.set_xlabel(col_num)
            ax.set_ylabel('Frequência')
            ax.set_title(f'Distribuição de {col_num}')
        
        else:
            # Gráfico de barras para categóricas
            col_cat = df.columns[0]
            contagem = df[col_cat].value_counts().head(8)
            ax.bar(contagem.index, contagem.values)
            ax.set_xlabel(col_cat)
            ax.set_ylabel('Contagem')
            ax.set_title(f'Top - {col_cat}')
            plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()
        
        relatorio = f"## 📈 VISUALIZAÇÃO GERADA\n\n"
        relatorio += f"**Arquivo:** {nome_arquivo}\n\n"
        relatorio += f"**Pergunta:** {pergunta}\n\n"
        relatorio += "✅ Gráfico exibido acima"
        
    except Exception as e:
        relatorio = f"❌ Erro ao gerar visualização: {str(e)}"
    
    return relatorio

# ============================================================================
# 8. 📋 RELATÓRIOS
# ============================================================================

def executar_relatorios(caminhos_csv: List[str], pergunta: str) -> str:
    """Executa geração de relatórios complexos"""
    
    contexto_csv = obter_contexto_csv(caminhos_csv)
    
    prompt_relatorio = f"""
    PERGUNTA: "{pergunta}"
    
    CONTEXTO: {json.dumps(contexto_csv, indent=2)}
    
    Gere um relatório analítico completo incluindo:
    1. Análise descritiva
    2. Insights principais
    3. Recomendações
    """
    
    resposta_llm = consultar_ollama_local(prompt_relatorio, {})
    
    relatorio = f"## 📋 RELATÓRIO ANALÍTICO\n\n"
    relatorio += f"**Pergunta:** {pergunta}\n\n"
    relatorio += f"**Arquivos Analisados:** {', '.join([os.path.basename(c) for c in caminhos_csv])}\n\n"
    relatorio += f"**Análise:**\n{resposta_llm}\n"
    
    return relatorio

# ============================================================================
# 9. 🛠️ FUNÇÕES AUXILIARES
# ============================================================================

def obter_contexto_csv(caminhos_csv: List[str]) -> Dict:
    """Obtém contexto básico dos CSVs"""
    contexto = {}
    for caminho in caminhos_csv:
        try:
            df = pd.read_csv(caminho, nrows=3)
            contexto[os.path.basename(caminho)] = {
                "colunas": list(df.columns),
                "tipos": df.dtypes.astype(str).to_dict(),
                "amostra": df.head(2).to_dict('records')
            }
        except Exception as e:
            contexto[os.path.basename(caminho)] = {"erro": str(e)}
    return contexto

def executar_sql(sql: str):
    """Executa SQL no PostgreSQL"""
    try:
        with get_engine().connect() as conn:
            if sql.strip().lower().startswith('select'):
                result = conn.execute(text(sql))
                return result.fetchall()
            else:
                conn.execute(text(sql))
                conn.commit()
                return "Comando executado com sucesso"
    except Exception as e:
        return f"Erro SQL: {str(e)}"

def executar_scripts_sql(scripts: List[str]) -> str:
    """Executa múltiplos scripts SQL"""
    resultados = []
    for script in scripts:
        resultados.append(f"---\n{script}\nResultado: {executar_sql(script)}")
    return "\n".join(resultados)

def extrair_scripts_sql(texto: str) -> List[str]:
    """Extrai scripts SQL do texto do LLM"""
    scripts = []
    if "```sql" in texto:
        partes = texto.split("```sql")[1:]
        for parte in partes:
            script = parte.split("```")[0].strip()
            if script:
                scripts.append(script)
    return scripts

def extrair_script_sql_unico(texto: str) -> Optional[str]:
    """Extrai um único script SQL"""
    scripts = extrair_scripts_sql(texto)
    return scripts[0] if scripts else None

def obter_tabelas_banco() -> List[str]:
    """Obtém lista de tabelas do banco"""
    try:
        inspector = inspect(get_engine())
        return inspector.get_table_names()
    except:
        return []

def processo_padrao_bi(caminhos_csv: List[str], pergunta: str) -> str:
    """Processo padrão para perguntas não classificadas"""
    contexto_csv = obter_contexto_csv(caminhos_csv)
    
    prompt_padrao = f"""
    PERGUNTA: "{pergunta}"
    
    CONTEXTO: {json.dumps(contexto_csv, indent=2)}
    TABELAS EXISTENTES: {obter_tabelas_banco()}
    
    Forneça uma resposta útil e sugira próximos passos.
    """
    
    return consultar_ollama_local(prompt_padrao, contexto_csv)

# ============================================================================
# 🎯 FUNÇÃO PRINCIPAL (MANTIDA PARA COMPATIBILIDADE)
# ============================================================================

def agente_bi_local(caminhos_csv, pergunta_usuario):
    """Função principal mantida para compatibilidade com app.py"""
    return orquestrar_acao(pergunta_usuario, caminhos_csv)