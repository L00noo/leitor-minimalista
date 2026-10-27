import streamlit as st
import re
import requests
from readability import Document
from groq import Groq

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Leitor Minimalista IA", page_icon="⚡", layout="centered")

# --- CSS PERSONALIZADO (mantido) ---
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

@st.cache_data(ttl=600) # Cache para evitar chamadas repetidas ao mesmo link
def extrair_texto_do_link(url):
    """Extrai o texto principal de uma página web comum."""
    try:
        # User-Agent para evitar bloqueios simples
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Usa readability para extrair o conteúdo do artigo
        doc = Document(response.text)
        texto_extraido = doc.summary()
        
        # Remove tags HTML que possam ter sobrado
        texto_limpo = re.sub(r'<[^>]+>', ' ', texto_extraido)
        # Normaliza espaços
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
        
        return texto_limpo
    except Exception as e:
        st.error(f"Erro ao extrair do link: {e}")
        return None

def limpar_com_ia(texto):
    """Usa o Groq para limpar o texto."""
    try:
        # A chave deve estar nos Secrets do Streamlit
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            st.error("Chave da API do Groq não configurada nos Secrets.")
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
            model="llama-3.3-70b-versatile", # Modelo rápido e gratuito
            temperature=0.0, # Para ser o mais determinístico possível
        )
        
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Erro na limpeza com IA: {e}")
        return None

def formatar_para_whatsapp(texto, limite_caracteres=100):
    """Quebra o texto em blocos respeitando o fim das palavras."""
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
st.caption("Cole um texto ou link. A IA limpa a sujeira e formata para leitura rápida.")

texto_bruto = st.text_area(
    "Cole o texto ou link aqui:", 
    height=250, 
    placeholder="Cole aqui o texto ou o link da matéria (ex: https://exemplo.com/noticia)...",
    key="texto_entrada"
)

col1, col2 = st.columns([3, 1])
with col1:
    botao_processar = st.button("Limpar e Formatar")
with col2:
    st.button("Limpar 🗑️", on_click=limpar_campos)

if botao_processar:
    if texto_bruto.strip():
        with st.spinner("Processando... Isso pode levar alguns segundos."):
            texto_para_ia = texto_bruto
            
            # 1. Se for um link, tenta extrair o texto primeiro
            if texto_bruto.strip().startswith("http"):
                st.info("Link detectado. Extraindo conteúdo...")
                texto_extraido = extrair_texto_do_link(texto_bruto.strip())
                if not texto_extraido:
                    st.error("Não foi possível extrair o texto deste link. Tente colar o texto manualmente.")
                    st.stop()
                texto_para_ia = texto_extraido

            # 2. Limpa com a IA
            st.info("Limpando com IA...")
            texto_limpo = limpar_com_ia(texto_para_ia)
            
            if texto_limpo:
                # 3. Formata
                st.session_state.texto_saida = formatar_para_whatsapp(texto_limpo, limite_caracteres=100)
            else:
                st.warning("A limpeza com IA falhou. O texto original será usado.")
                st.session_state.texto_saida = formatar_para_whatsapp(texto_para_ia, limite_caracteres=100)
    else:
        st.warning("Por favor, cole algum texto ou link antes de clicar no botão.")

if st.session_state.texto_saida:
    st.divider()
    st.subheader("Texto Pronto para Leitura:")
    st.text_area(
        "Copie o texto abaixo:", 
        value=st.session_state.texto_saida, 
        height=350
    )
