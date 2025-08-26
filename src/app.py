import streamlit as st
from typing import List, Dict

from src.rules_loader import load_rules_from_url
from src.llm_client import LLMClient


st.set_page_config(page_title="Kural Tabanlı Asistan", page_icon="🧭", layout="wide")

if "messages" not in st.session_state:
    st.session_state["messages"] = []  # List[Dict[str, str]]
if "system_rules" not in st.session_state:
    st.session_state["system_rules"] = ""


def build_system_prompt(rules_text: str) -> str:
    base = (
        "Sen; verilen kurallar, politika ve metinleri kesin referans alan bir asistansın. "
        "Cevaplarında her zaman kurallara uy. Uymayan isteklerde kibarca reddet veya yönlendir.\n\n"
        "Kurallar (kısa özet + tam metin):\n"
    )
    if not rules_text.strip():
        return base + "(Kurallar yüklenmedi. Kullanıcıdan kuralları talep et ve ilerleme.)"

    guidance = (
        "\n\nCevaplama Kuralları:\n"
        "- Yalnızca yukarıdaki kurallara dayan.\n"
        "- Emin olmadığın noktada netleştirici soru sor.\n"
        "- Gerekirse ilgili kural/madde numarasına atıf yap.\n"
        "- Kısa, kesin ve uygulanabilir cevaplar ver.\n"
    )
    return base + rules_text.strip() + guidance


with st.sidebar:
    st.header("Kaynak Kurallar")
    url = st.text_input("ChatGPT Paylaşım Bağlantısı", placeholder="https://chatgpt.com/share/...")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Kuralları Yükle", use_container_width=True, type="primary"):
            if not url.strip():
                st.error("Lütfen geçerli bir bağlantı girin.")
            else:
                with st.spinner("Bağlantıdan içerik çekiliyor..."):
                    try:
                        rules = load_rules_from_url(url.strip())
                        st.session_state["system_rules"] = rules
                        st.success("Kurallar başarıyla yüklendi.")
                    except Exception as exc:  # noqa: BLE001
                        st.error(str(exc))
    with col2:
        if st.button("Kuralları Temizle", use_container_width=True):
            st.session_state["system_rules"] = ""

    st.divider()
    pasted = st.text_area("Kuralları Yapıştır (Alternatif)", height=180, placeholder="Kuralları buraya yapıştırın...")
    if st.button("Kuralları Kaydet", use_container_width=True):
        if pasted.strip():
            st.session_state["system_rules"] = pasted.strip()
            st.success("Kurallar kaydedildi.")
        else:
            st.warning("Boş metin kaydedilemez.")

    if st.session_state["system_rules"]:
        with st.expander("Kurallar Önizleme", expanded=False):
            st.write(st.session_state["system_rules"][:4000] + ("..." if len(st.session_state["system_rules"]) > 4000 else ""))

st.title("🧭 Kural Tabanlı Sohbet Asistanı")

if not st.session_state["system_rules"]:
    st.info("Sohbete başlamadan önce kuralları bir bağlantıdan yükleyin veya yapıştırın.")

# Render chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])  # content may include markdown

user_input = st.chat_input("Mesajınızı yazın...")

if user_input is not None and user_input.strip():
    if not st.session_state["system_rules"]:
        st.warning("Önce kuralları yükleyin veya yapıştırın.")
    else:
        st.session_state["messages"].append({"role": "user", "content": user_input.strip()})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Yanıt hazırlanıyor..."):
                try:
                    client = LLMClient()
                    messages: List[Dict[str, str]] = [{
                        "role": "system",
                        "content": build_system_prompt(st.session_state["system_rules"]),
                    }]
                    messages.extend(st.session_state["messages"])  # include prior turns

                    response_text = client.chat(messages)
                    st.markdown(response_text)
                    st.session_state["messages"].append({"role": "assistant", "content": response_text})
                except Exception as exc:  # noqa: BLE001
                    st.error(str(exc))

col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("Sohbeti Sıfırla", use_container_width=True):
        st.session_state["messages"] = []
with col_b:
    st.caption("OpenAI ile çalışır. `.env` içinde `OPENAI_API_KEY` gereklidir.")