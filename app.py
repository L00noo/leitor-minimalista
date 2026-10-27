import streamlit as st
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Leitor Minimalista", page_icon="📱", layout="centered")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    /* Esconde o menu superior e o rodapé do Streamlit para parecer um app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ajusta o espaçamento e a fonte para leitura confortável */
    .stTextArea textarea {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* Deixa o botão principal mais amigável */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #25D366; /* Verde estilo WhatsApp */
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1EBE5D;
        color: white;
    }
    
    /* Botão de limpar mais discreto */
    div[data-testid="stHorizontalBlock"] button {
        background-color: #f0f2f6 !important;
        color: #333 !important;
        border: 1px solid #ccc !important;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        background-color: #e0e0e0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO (Necessário para o botão Limpar) ---
if "texto_entrada" not in st.session_state:
    st.session_state.texto_entrada = ""
if "texto_saida" not in st.session_state:
    st.session_state.texto_saida = ""

# --- FUNÇÕES DE PROCESSAMENTO ---
def limpar_texto_bruto(texto):
    """Remove quebras de linha soltas e excesso de espaços."""
    texto_limpo = re.sub(r'\s+', ' ', texto)
    return texto_limpo.strip()

# LIMITE ALTERADO PARA 100 AQUI
def formatar_para_whatsapp(texto, limite_caracteres=100):
    """Quebra o texto em blocos de até X caracteres, respeitando o fim das palavras."""
    texto_limpo = limpar_texto_bruto(texto)
    
    if len(texto_limpo) <= limite_caracteres:
        return texto_limpo

    blocos = []
    palavras = texto_limpo.split(' ')
    bloco_atual = ""

    for palavra in palavras:
        if len(bloco_atual) + len(palavra) + 1 <= limite_caracteres:
            bloco_atual += palavra + " "
        else:
            blocos.append(bloco_atual.strip())
            bloco_atual = palavra + " "
    
    if bloco_atual:
        blocos.append(bloco_atual.strip())

    return "\n\n".join(blocos)

def limpar_campos():
    """Função chamada pelo botão de limpar"""
    st.session_state.texto_entrada = ""
    st.session_state.texto_saida = ""

# --- INTERFACE DO APP ---
st.title("⚡ Textos Minimalistas Para Quem Tem Pressa")
st.caption("Cole o texto bagunçado e receba parágrafos limpos, prontos para ler.")

# Campo de entrada de texto (vinculado ao session_state)
texto_bruto = st.text_area(
    "Cole o texto aqui (Ctrl+V / Cmd+V):", 
    height=250, 
    placeholder="Cole aqui o texto que você copiou da matéria...",
    key="texto_entrada"
)

# Botões lado a lado
col1, col2 = st.columns([3, 1])

with col1:
    botao_formatar = st.button("Reformatar Texto")

with col2:
    st.button("Limpar 🗑️", on_click=limpar_campos)

# Ação ao clicar em formatar
if botao_formatar:
    if texto_bruto.strip():
        # LIMITE ALTERADO PARA 100 AQUI TAMBÉM
        st.session_state.texto_saida = formatar_para_whatsapp(texto_bruto, limite_caracteres=100)
    else:
        st.warning("Por favor, cole algum texto antes de clicar no botão.")

# Exibe o resultado se houver algo na saída
if st.session_state.texto_saida:
    st.divider()
    st.subheader("Texto Pronto para Leitura:")
    
    st.text_area(
        "Copie o texto abaixo:", 
        value=st.session_state.texto_saida, 
        height=350
    )
