import streamlit as st
import pandas as pd
import time
import random
import asyncio
from playwright.async_api import async_playwright

st.set_page_config(page_title="Dace Disparos", page_icon="📱", layout="wide")

st.title("📱 Dace Disparos")
st.subheader("Disparador WhatsApp em Massa - Versão Cloud")

with st.sidebar:
    st.header("⚙️ Configurações")
    delay = st.slider("Delay entre mensagens (segundos)", 15, 45, 22)
    st.warning("⚠️ Use apenas com permissão. Risco de banimento existe.")

uploaded_file = st.file_uploader("📎 Suba sua planilha (colunas: numero e mensagem)", type=["xlsx", "csv"])

mensagem_fixa = st.text_area("✍️ Mensagem para enviar", height=120)

if uploaded_file:
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.success(f"✅ {len(df)} contatos carregados")
    st.dataframe(df.head(10), use_container_width=True)

    if st.button("🚀 INICIAR DISPAROS", type="primary", use_container_width=True):
        with st.spinner("Iniciando Playwright..."):
            async def run_disparos():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    context = await browser.new_context()
                    page = await context.new_page()

                    await page.goto("https://web.whatsapp.com")
                    st.info("🔴 **ESCANEIE O QR CODE** na janela que abriu.")
                    await asyncio.sleep(30)

                    progress_bar = st.progress(0)
                    status = st.empty()

                    total = len(df)
                    for i, row in df.iterrows():
                        numero = str(row.get('numero', '')).strip()
                        msg = mensagem_fixa.strip() if mensagem_fixa.strip() else str(row.get('mensagem', '')).strip()

                        if len(numero) < 10 or not msg:
                            continue

                        try:
                            status.info(f"🔄 Enviando para {numero}... ({i+1}/{total})")
                            await page.goto(f"https://web.whatsapp.com/send?phone={numero}&text={msg.replace(' ', '%20')}")
                            await asyncio.sleep(8)

                            # Clica no campo e envia
                            await page.keyboard.press("Enter")
                            status.success(f"✅ Enviado para {numero}")
                        except:
                            status.error(f"❌ Erro com {numero}")

                        progress_bar.progress((i + 1) / total)
                        await asyncio.sleep(delay)

                    await browser.close()
                    st.balloons()
                    st.success("🎉 Disparos finalizados!")

            asyncio.run(run_disparos())
st.caption("Dace Disparos © 2026 • Uso ético obrigatório • Risco de banimento existe")
