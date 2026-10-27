import streamlit as st
import re

st.set_page_config(page_title="Leitor Minimalista", page_icon="📱", layout="centered")

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
        background-color: #25D366; /* Verde estilo WhatsApp */
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1EBE5D;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

def limpar_texto(texto):
    """Remove quebras de linha soltas e excesso de espaços."""
    texto_limpo = re.sub(r'\s+', ' ', texto)
    return texto_limpo.strip()

def formatar_para_whatsapp(texto, limite_caracteres=200):
    """Quebra o texto em blocos de até X caracteres, respeitando o fim das palavras."""
    texto_limpo = limpar_texto(texto)
    
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


st.title("📱 Leitor Minimalista")
st.caption("Cole o texto bagunçado e receba parágrafos limpos, prontos para ler.")

texto_bruto = st.text_area(
    "Cole o texto aqui (Ctrl+V / Cmd+V):", 
    height=250, 
    placeholder="Cole aqui o texto que você copiou da matéria..."
)

if st.button("Reformatar Texto"):
    if texto_bruto.strip():
        texto_formatado = formatar_para_whatsapp(texto_bruto, limite_caracteres=200)
        
        st.divider()
        st.subheader("Texto Pronto para Leitura:")
        
        st.text_area(
            "Copie o texto abaixo:", 
            value=texto_formatado, 
            height=350
        )
        
        st.info("💡 Dica: Toque dentro da caixa acima e selecione 'Copiar tudo' para enviar no WhatsApp ou salvar onde quiser.")
    else:
        st.warning("Por favor, cole algum texto antes de clicar no botão.")
