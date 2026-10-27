import streamlit as st
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Leitor Minimalista", page_icon="📱", layout="centered")

# --- CSS PERSONALIZADO (Para deixar a interface mais limpa e agradável) ---
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
    
    /* Deixa o botão mais amigável */
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

# --- FUNÇÕES DE PROCESSAMENTO ---
def limpar_texto(texto):
    """Remove quebras de linha soltas e excesso de espaços."""
    # Substitui múltiplas quebras de linha ou espaços por um espaço simples
    texto_limpo = re.sub(r'\s+', ' ', texto)
    return texto_limpo.strip()

def formatar_para_whatsapp(texto, limite_caracteres=200):
    """Quebra o texto em blocos de até X caracteres, respeitando o fim das palavras."""
    texto_limpo = limpar_texto(texto)
    
    # Se o texto for menor que o limite, retorna ele mesmo
    if len(texto_limpo) <= limite_caracteres:
        return texto_limpo

    blocos = []
    palavras = texto_limpo.split(' ')
    bloco_atual = ""

    for palavra in palavras:
        # Se adicionar a próxima palavra não estourar o limite
        if len(bloco_atual) + len(palavra) + 1 <= limite_caracteres:
            bloco_atual += palavra + " "
        else:
            # Salva o bloco atual e começa um novo
            blocos.append(bloco_atual.strip())
            bloco_atual = palavra + " "
    
    # Adiciona o último bloco restante
    if bloco_atual:
        blocos.append(bloco_atual.strip())

    # Junta os blocos com quebra dupla de linha (estilo parágrafos de chat)
    return "\n\n".join(blocos)


# --- INTERFACE DO APP ---
st.title("📱 Leitor Minimalista")
st.caption("Cole o texto bagunçado e receba parágrafos limpos, prontos para ler.")

# Campo de entrada de texto
texto_bruto = st.text_area(
    "Cole o texto aqui (Ctrl+V / Cmd+V):", 
    height=250, 
    placeholder="Cole aqui o texto que você copiou da matéria..."
)

# Botão de ação
if st.button("Reformatar Texto"):
    if texto_bruto.strip():
        texto_formatado = formatar_para_whatsapp(texto_bruto, limite_caracteres=200)
        
        st.divider()
        st.subheader("Texto Pronto para Leitura:")
        
        # Caixa de saída (o usuário pode copiar daqui)
        st.text_area(
            "Copie o texto abaixo:", 
            value=texto_formatado, 
            height=350
        )
        
        # Dica de uso no celular
        st.info("💡 Dica: Toque dentro da caixa acima e selecione 'Copiar tudo' para enviar no WhatsApp ou salvar onde quiser.")
    else:
        st.warning("Por favor, cole algum texto antes de clicar no botão.")
