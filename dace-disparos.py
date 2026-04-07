import streamlit as st
import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

st.set_page_config(page_title="Dace Disparos", page_icon="📱", layout="wide")

# Tema claro/escuro automático (Streamlit respeita o modo do navegador)
st.markdown("""
<style>
    .main { background-color: #f0f2f5; }
    .dark .main { background-color: #0f172a; }
    .stButton>button { background-color: #25D366; color: white; border-radius: 50px; height: 60px; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("📱 Dace Disparos")
st.markdown("**Disparador WhatsApp em Massa** • Use sua própria conta • Delay anti-ban")

with st.sidebar:
    st.header("⚙️ Configurações")
    delay_min = st.slider("Delay mínimo (segundos)", 12, 25, 15)
    delay_max = st.slider("Delay máximo (segundos)", 25, 40, 30)
    st.warning("Quanto maior o delay, menor o risco de banimento.")

uploaded_file = st.file_uploader("📎 Suba sua planilha (colunas: numero e mensagem)", type=["xlsx", "csv"])

mensagem_fixa = st.text_area("✍️ Mensagem (deixe em branco para usar a coluna 'mensagem' da planilha)", height=120)

if uploaded_file:
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    st.success(f"✅ {len(df)} contatos carregados!")
    st.dataframe(df.head(10), use_container_width=True)

    if st.button("🚀 INICIAR DISPAROS EM MASSA", use_container_width=True):
        with st.spinner("Abrindo WhatsApp Web..."):
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get("https://web.whatsapp.com")
            
            st.info("🔴 **ESCANEIE O QR CODE** que apareceu no navegador com o seu WhatsApp.")
            time.sleep(30)

            progress_bar = st.progress(0)
            status = st.empty()

            for i, row in df.iterrows():
                numero = str(row.get('numero', '')).strip()
                msg_planilha = str(row.get('mensagem', '')).strip()
                mensagem = mensagem_fixa.strip() if mensagem_fixa.strip() else msg_planilha
                
                if len(numero) < 10 or not mensagem:
                    continue

                try:
                    status.info(f"🔄 Enviando para {numero}... ({i+1}/{len(df)})")
                    link = f"https://web.whatsapp.com/send?phone={numero}&text={mensagem.replace(' ', '%20')}"
                    driver.get(link)
                    time.sleep(10)

                    message_box = WebDriverWait(driver, 20).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true" and @role="textbox"]')),
                            EC.presence_of_element_located((By.XPATH, '//div[@aria-placeholder="Digite uma mensagem"]'))
                        )
                    )
                    message_box.click()
                    message_box.send_keys(Keys.ENTER)

                    status.success(f"✅ Enviado para {numero}")
                except:
                    status.error(f"❌ Falha com {numero}")

                progress_bar.progress((i + 1) / len(df))
                time.sleep(random.uniform(delay_min, delay_max))

            driver.quit()
            st.balloons()
            st.success("🎉 Disparos finalizados com sucesso!")

st.caption("Dace Disparos © 2026 • Uso ético obrigatório • Risco de banimento existe")