import streamlit as st
import requests
import pandas as pd
import time
import itertools

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Consulta Masiva de DNIs", page_icon="🧾", layout="centered")

# === TOKENS Y LÍMITE POR TOKEN ===
TOKENS = [
    "2e2e37ebaa20a5dfb62c06b61ce7589341d87b259cad83ade5aca3a45253cc10",
    "2d258586a04f28c3409315a27ec64865d80ed2f0c643a3a8f8a76d0960fb9f05",
    "44a296c30f85be0407a00660a5fde4ac7e540a50a3925f17621dc3fefbf536eb",
    "833cd499bc5299a6d5c162576a9a8d10c4836831c6eef6dbaaf878b61b9a339e",
    # Puedes agregar más tokens aquí
]
LIMITE_POR_TOKEN = 100
token_ciclo = itertools.cycle(TOKENS)

# === ESTILO MEJORADO Y PROFESIONAL ===
st.markdown("""
    <style>
    /* Fondo con animación de gradiente */
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

# === TÍTULO Y DESCRIPCIÓN ===
st.title("🔍 Consulta Masiva de DNIs")
st.caption(f"API: apiperu.dev · {len(TOKENS)} token(s) registrados · Hasta {LIMITE_POR_TOKEN * len(TOKENS)} consultas")

# === INGRESO DE DATOS ===
st.markdown("### 📋 Pega tu lista de DNIs")
dni_text = st.text_area("🧾 Ingrese uno por línea o separados por comas:", height=250)

# === FUNCIÓN DE CONSULTA INDIVIDUAL ===
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

# === BOTÓN DE CONSULTA ===
if st.button("🚀 Consultar DNIs"):
    if not dni_text.strip():
        st.warning("⚠️ Por favor, ingresa al menos un DNI.")
    else:
        dni_list = [d.strip() for d in dni_text.replace(",", "\n").splitlines() if d.strip()]
        total_dnis = len(dni_list)
        max_dnis = LIMITE_POR_TOKEN * len(TOKENS)

        if total_dnis > max_dnis:
            st.warning(f"⚠️ Solo se procesarán los primeros {max_dnis} DNIs por límite de tokens.")
            dni_list = dni_list[:max_dnis]

        resultados = []
        progress = st.progress(0)
        total_tokens = len(TOKENS)
        consultas_realizadas = 0
        token_actual = next(token_ciclo)

        resultados = []
        progress = st.progress(0)
        total_tokens = len(TOKENS)
        consultas_realizadas = 0
        token_actual = next(token_ciclo)
        consultas_totales = len(dni_list)
        total_disponible = LIMITE_POR_TOKEN * len(TOKENS)

        status_placeholder = st.empty()  # ← Para mostrar contador dinámico

        with st.spinner("⌛ Realizando consultas..."):
            for i, dni in enumerate(dni_list, 1):
                if consultas_realizadas >= LIMITE_POR_TOKEN:
                    token_actual = next(token_ciclo)
                    consultas_realizadas = 0

                resultado = consultar_dni(dni, token_actual)
                resultados.append(resultado)

                consultas_realizadas += 1
                progress.progress(i / consultas_totales)

                restante = total_disponible - i
                status_placeholder.info(f"🧮 Consultas realizadas: {i} / {total_disponible} · Restantes: {restante}")

                time.sleep(1)


        df_resultado = pd.DataFrame(resultados)
        st.success(f"✅ Consulta completada ({len(df_resultado)} registros procesados)")
        st.dataframe(df_resultado, use_container_width=True)

        csv = df_resultado.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar resultados en CSV", csv, "resultados_dni.csv", "text/csv")
