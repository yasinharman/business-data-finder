import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

st.set_page_config(
    page_title="İşletme Verisi Bulma Aracı",
    page_icon="🔎",
    layout="centered",
)

st.markdown(
    """
    <style>
    #MainMenu, footer, header {visibility: hidden;}

    html, body, .stApp {
        background: #0e1117;
    }

    div[data-testid="stAppViewContainer"] > section.main,
    div[data-testid="stAppViewContainer"] > div[data-testid="stMain"],
    section[data-testid="stMain"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
    }

    div[data-testid="stMainBlockContainer"],
    .block-container {
        max-width: 720px !important;
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.chat-card-marker) {
        background: #1b1f27;
        border: 1px solid #2a2f3a;
        border-radius: 18px;
        padding: 2rem 1.75rem 1.25rem 1.75rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.35);
        width: 100%;
    }

    .chat-card-title {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 1.25rem;
        color: #f3f4f6;
    }

    div[data-testid="stChatInput"] {
        background: transparent !important;
        position: relative !important;
        bottom: auto !important;
    }

    div[data-testid="stBottomBlockContainer"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.container(border=True):
    st.markdown('<div class="chat-card-marker"></div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-card-title">İşletme Verisi Bulma Aracı</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Mesajınızı yazın...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    if not N8N_WEBHOOK_URL:
        reply = "⚠️ N8N_WEBHOOK_URL tanımlı değil. Lütfen .env dosyasına webhook adresini ekleyin."
    else:
        try:
            response = requests.post(
                N8N_WEBHOOK_URL,
                json={"message": prompt, "history": st.session_state.messages},
                timeout=120,
            )
            response.raise_for_status()
            try:
                data = response.json()
                if isinstance(data, dict):
                    reply = data.get("reply") or data.get("output") or data.get("message") or str(data)
                elif isinstance(data, list) and data:
                    first = data[0]
                    if isinstance(first, dict):
                        reply = first.get("reply") or first.get("output") or first.get("message") or str(first)
                    else:
                        reply = str(first)
                else:
                    reply = str(data)
            except ValueError:
                reply = response.text or "✅ İstek gönderildi."
        except requests.RequestException as exc:
            reply = f"❌ Webhook'a ulaşılamadı: {exc}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
