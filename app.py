## 🌐 **3. INTERFACE STREAMLIT**
### 📄 **app.py**
import streamlit as st
import tempfile
import os
from agent_bi import agente_bi_local

# Configuração da página
st.set_page_config(
    page_title="Analista BI Local 100% Offline",
    page_icon="📊",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .offline-badge {
        background-color: #28a745;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Analista de BI Local 100% Offline</h1>', unsafe_allow_html=True)
st.markdown('<p class="offline-badge">✅ Totalmente Local - Sem Dependências Externas</p>', unsafe_allow_html=True)

st.write("""
**Carregue seus CSVs e faça análises complexas usando IA local (Llama 3.1) + PostgreSQL local.**
Tudo roda na sua máquina - nenhum dado sai para a internet!
""")

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Configuração")
    st.success("**Status do Sistema:**")
    st.write("• 🤖 Llama 3.1 Local: ✅")
    st.write("• 🗄️ PostgreSQL Local: ✅") 
    st.write("• 📊 Streamlit: ✅")
    
    st.info("**Como usar:**")
    st.write("1. 📁 Faça upload dos CSVs")
    st.write("2. 💬 Descreva sua análise")
    st.write("3. ⚡ Execute e veja resultados")
    modelo_selecionado = st.sidebar.selectbox(
    "🤖 Escolha o Modelo:",
    ["llama3.2:3b", "phi3:mini", "llama3.1:8b"],
    index=0
)

# Área principal
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📁 Upload de Dados")
    arquivos = st.file_uploader(
        "Selecione arquivos CSV", 
        type="csv", 
        accept_multiple_files=True,
        help="Podem ser vários arquivos para relacionar"
    )

with col2:
    st.subheader("💬 Análise Desejada")
    pergunta = st.text_area(
        "Descreva o que você quer analisar:",
        placeholder="Ex: Crie um data warehouse com essas tabelas e mostre o faturamento mensal por produto...",
        height=100
    )

    if st.button("🚀 Executar Análise", type="primary", use_container_width=True):
        if arquivos and pergunta:
            with st.spinner("Processando localmente (pode levar alguns segundos)..."):
                # Salvar arquivos temporariamente
                caminhos_temp = []
                for arquivo in arquivos:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                        tmp.write(arquivo.getvalue())
                        caminhos_temp.append(tmp.name)
                
                # Executar agente BI
                resultado = agente_bi_local(caminhos_temp, pergunta)
                
                # Limpar arquivos temporários
                for caminho in caminhos_temp:
                    try:
                        os.unlink(caminho)
                    except:
                        pass
                
                # Mostrar resultados
                st.subheader("📋 Resultado da Análise")
                st.markdown(resultado)
        else:
            st.warning("⚠️ Por favor, faça upload de pelo menos 1 CSV e escreva uma pergunta.")

# Rodapé
st.markdown("---")
st.caption("Sistema 100% Local - Desenvolvido para BI Offline | Llama 3.1 + PostgreSQL + Streamlit")