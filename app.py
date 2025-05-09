import streamlit as st
import pandas as pd
import requests

TOKEN = "1f17cd95fae8ef4c9f8752c26753e4f51393f27d8f3f0875aee5580d5abb5f7b"

# Consulta individual usando ApiPeruDev
def consultar_dni(dni):
    url = "https://apiperu.dev/api/dni"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    body = {"dni": dni}
    try:
        response = requests.post(url, headers=headers, json=body, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["data"].get("nombre_completo", "No encontrado")
            else:
                return "No encontrado"
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return str(e)

# Interfaz Streamlit
st.title("🧾 Consulta masiva de DNIs (ApiPeruDev)")

st.write("Pega una lista de DNIs (uno por línea o separados por coma):")

dni_text = st.text_area("Lista de DNIs", height=200)

if st.button("Consultar"):
    if dni_text.strip() == "":
        st.warning("⚠️ Ingresa al menos un DNI.")
    else:
        if "," in dni_text:
            dni_list = [d.strip() for d in dni_text.split(",") if d.strip()]
        else:
            dni_list = [d.strip() for d in dni_text.splitlines() if d.strip()]

        resultados = []
        with st.spinner("Consultando, por favor espera..."):
            for dni in dni_list:
                nombre = consultar_dni(dni)
                resultados.append({"DNI": dni, "Nombre Completo": nombre})

        df = pd.DataFrame(resultados)
        st.success("✅ Consulta completada")
        st.dataframe(df)

        # Descarga
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, "resultados_dni.csv", "text/csv")



# python -m streamlit run app.py