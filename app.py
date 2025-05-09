import streamlit as st
import requests
import pandas as pd
import time
import itertools
import json
import os

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Consulta Masiva de DNIs", page_icon="🧾", layout="centered")

# === TOKENS Y LÍMITE POR TOKEN ===
TOKENS = [
    "2e2e37ebaa20a5dfb62c06b61ce7589341d87b259cad83ade5aca3a45253cc10",
    "2d258586a04f28c3409315a27ec64865d80ed2f0c643a3a8f8a76d0960fb9f05",
    "44a296c30f85be0407a00660a5fde4ac7e540a50a3925f17621dc3fefbf536eb",
    "833cd499bc5299a6d5c162576a9a8d10c4836831c6eef6dbaaf878b61b9a339e",
]
LIMITE_POR_TOKEN = 100
TOTAL_DISPONIBLE = LIMITE_POR_TOKEN * len(TOKENS)
token_ciclo = itertools.cycle(TOKENS)

# === CONTADOR PERSISTENTE ===
CONTADOR_FILE = "contador_consultas.json"

def cargar_contador():
    if os.path.exists(CONTADOR_FILE):
        with open(CONTADOR_FILE, "r") as f:
            return json.load(f)
    else:
        return {"usadas": 0}

def guardar_contador(usadas):
    with open(CONTADOR_FILE, "w") as f:
        json.dump({"usadas": usadas}, f)

contador = cargar_contador()

# === ESTILO VISUAL ===
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #f1f5f9, #e0f2fe, #fef3c7, #f1f5f9);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
        font-family: 'Segoe UI', sans-serif;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .main .block-container {
        background-color: rgba(255,255,255,0.9);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    h1 {
        font-size: 2.2em;
        color: #1e293b;
        border-bottom: 2px solid #0ea5e9;
        padding-bottom: 0.3em;
        margin-bottom: 0.8em;
        text-align: center;
    }
    textarea {
        background-color: #ffffff !important;
        border: 2px solid #0ea5e9 !important;
        border-radius: 10px !important;
        font-size: 16px !important;
        color: #1e293b !important;
        padding: 10px !important;
        width: 100% !important;
    }
    .stButton button {
        background-color: #0ea5e9 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        width: 100%;
    }
    .stDownloadButton button {
        background-color: #334155 !important;
        color: white !important;
        border-radius: 10px;
        width: 100%;
    }
    @media only screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        textarea {
            font-size: 14px !important;
        }
        .stButton button, .stDownloadButton button {
            font-size: 14px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# === INTERFAZ ===
st.title("🔍 Consulta Masiva de DNIs")
st.caption(f"API: apiperu.dev · {len(TOKENS)} token(s) · Máximo {TOTAL_DISPONIBLE} consultas")
st.info(f"🧮 Consultas realizadas hasta ahora: {contador['usadas']} · Restantes: {TOTAL_DISPONIBLE - contador['usadas']}")

# === INGRESO DE DATOS ===
st.markdown("### 📋 Pega tu lista de DNIs")
dni_text = st.text_area("🧾 Uno por línea o separados por coma:", height=250)

# === FUNCIÓN PRINCIPAL ===
def consultar_dni(dni, token):
    url = "https://apiperu.dev/api/dni"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        r = requests.post(url, headers=headers, json={"dni": dni}, timeout=5)
        if r.status_code == 200 and r.json().get("success"):
            d = r.json()["data"]
            nombre_formateado = f"{d.get('nombres', '')} {d.get('apellido_paterno', '')} {d.get('apellido_materno', '')}".strip()
            return {"DNI": dni, "Nombre Completo": nombre_formateado}
        return {"DNI": dni, "Nombre Completo": "No encontrado"}
    except Exception as e:
        return {"DNI": dni, "Nombre Completo": str(e)}

# === BOTÓN ===
if st.button("🚀 Consultar DNIs"):
    if not dni_text.strip():
        st.warning("⚠️ Ingresa al menos un DNI.")
    else:
        dni_list = [d.strip() for d in dni_text.replace(",", "\n").splitlines() if d.strip()]
        total_disponibles = TOTAL_DISPONIBLE - contador["usadas"]

        if len(dni_list) > total_disponibles:
            st.warning(f"⚠️ Solo se procesarán los primeros {total_disponibles} DNIs disponibles.")
            dni_list = dni_list[:total_disponibles]

        resultados = []
        progress = st.progress(0)
        status_placeholder = st.empty()
        token_actual = next(token_ciclo)
        consultas_realizadas = 0

        with st.spinner("⌛ Consultando DNIs..."):
            for i, dni in enumerate(dni_list, 1):
                if consultas_realizadas >= LIMITE_POR_TOKEN:
                    token_actual = next(token_ciclo)
                    consultas_realizadas = 0

                resultado = consultar_dni(dni, token_actual)
                resultados.append(resultado)
                consultas_realizadas += 1
                progress.progress(i / len(dni_list))
                status_placeholder.info(f"🔁 Consultas realizadas: {contador['usadas'] + i} / {TOTAL_DISPONIBLE}")

                time.sleep(1)

        # Guardar contador actualizado
        contador["usadas"] += len(dni_list)
        guardar_contador(contador["usadas"])

        df_resultado = pd.DataFrame(resultados)
        st.success(f"✅ Consulta finalizada · Total consultados: {len(df_resultado)}")
        st.dataframe(df_resultado, use_container_width=True)

        csv = df_resultado.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, "resultados_dni.csv", "text/csv")
