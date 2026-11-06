import streamlit as st
import re
import requests
import base64
from readability import Document
from groq import Groq

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Leitor Minimalista IA", page_icon="⚡", layout="centered")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTextArea textarea {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #25D366;
        color: white;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stButton>button:hover {
        background-color: #1EBE5D;
        color: white;
    }
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

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "texto_entrada" not in st.session_state:
    st.session_state.texto_entrada = ""
if "texto_saida" not in st.session_state:
    st.session_state.texto_saida = ""

# --- FUNÇÕES DE PROCESSAMENTO ---

@st.cache_data(ttl=600)
def extrair_texto_do_link(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        doc = Document(response.text)
        texto_extraido = doc.summary()
        texto_limpo = re.sub(r'<[^>]+>', ' ', texto_extraido)
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
        return texto_limpo
    except Exception:
        return None

def limpar_com_ia(texto):
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            return None
        client = Groq(api_key=api_key)
        
        prompt = f"""
        Você é um assistente de limpeza de texto. Sua tarefa é remover qualquer introdução, rodapé, menu de navegação, anúncio, chamada para redes sociais ou informação irrelevante do texto abaixo. 
        Retorne APENAS o corpo do artigo/texto limpo, sem explicações, sem markdown, sem aspas.
        Se o texto já estiver limpo, retorne-o como está.
        
        Texto para limpar:
        {texto}
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.0,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception:
        return None

def transcrever_imagem(imagem_bytes):
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            return None
        client = Groq(api_key=api_key)
        
        base64_image = base64.b64encode(imagem_bytes).decode('utf-8')
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcreva fielmente todo o texto visível nesta imagem. Retorne apenas o texto, sem comentários ou formatação extra."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0.0,
            max_completion_tokens=1024,
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return None

def formatar_para_whatsapp(texto, limite_caracteres=100):
    if not texto: return ""
    texto_limpo = re.sub(r'\s+', ' ', texto).strip()
    
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
    st.session_state.texto_entrada = ""
    st.session_state.texto_saida = ""

# --- INTERFACE DO APP ---
st.title("⚡ Leitor para quem tem pressa")
st.caption("Cole um texto, link ou envie uma imagem. A IA limpa e formata para leitura rápida.")

# Campo de entrada de texto
texto_bruto = st.text_area(
    "Cole o texto ou link aqui:", 
    height=200, 
    placeholder="Cole aqui o texto ou o link da matéria...",
    key="texto_entrada"
)

# Botão de ação para Texto
col_texto, col_limpar = st.columns([3, 1])
with col_texto:
    botao_processar_texto = st.button("Limpar e Formatar Texto")
with col_limpar:
    st.button("Limpar 🗑️", on_click=limpar_campos)

st.divider()

# Campo de upload de imagem
imagem_upload = st.file_uploader("Ou envie uma captura de tela (print) para transcrever:", type=["png", "jpg", "jpeg"])

if imagem_upload is not None:
    st.image(imagem_upload, caption="Imagem carregada", use_container_width=True)
    botao_transcrever = st.button("Transcrever Imagem")

# --- LÓGICA DE AÇÃO ---

# Ação para Texto/Link
if botao_processar_texto:
    if texto_bruto.strip():
        with st.spinner("Processando texto... Isso pode levar alguns segundos."):
            texto_para_ia = texto_bruto
            
            if texto_bruto.strip().startswith("http"):
                st.info("Link detectado. Extraindo conteúdo...")
                texto_extraido = extrair_texto_do_link(texto_bruto.strip())
                if not texto_extraido:
                    st.error("Não foi possível extrair o texto deste link. Tente colar o texto manualmente.")
                    st.stop()
                texto_para_ia = texto_extraido

            st.info("Limpando com IA...")
            texto_limpo = limpar_com_ia(texto_para_ia)
            
            if texto_limpo:
                st.session_state.texto_saida = formatar_para_whatsapp(texto_limpo, limite_caracteres=100)
            else:
                st.session_state.texto_saida = formatar_para_whatsapp(texto_para_ia, limite_caracteres=100)
    else:
        st.warning("Por favor, cole algum texto ou link antes de clicar no botão.")

# Ação para Imagem
if imagem_upload is not None and 'botao_transcrever' in locals() and botao_transcrever:
    with st.spinner("Lendo a imagem..."):
        texto_transcrito = transcrever_imagem(imagem_upload.getvalue())
        if texto_transcrito:
            st.session_state.texto_saida = formatar_para_whatsapp(texto_transcrito, limite_caracteres=100)
        else:
            st.warning("Não foi possível transcrever a imagem. Verifique a qualidade ou tente novamente.")

# --- EXIBIÇÃO DO RESULTADO ---
if st.session_state.texto_saida:
    st.divider()
    st.subheader("Texto Pronto para Leitura:")
    st.text_area(
        "Copie o texto abaixo:", 
        value=st.session_state.texto_saida, 
        height=350
    )
