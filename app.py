import streamlit as st # type: ignore
import pandas as pd # type: ignore
import unicodedata

st.set_page_config(page_title="Conversor de Exames", layout="wide")

# =========================
# ESTADO
# =========================
if "depara" not in st.session_state:
    st.session_state.depara = {
        "glucosa": "1001",
        "urea": "1002",
        "urea post": "1004",
        "creatinina": "1006",
        "creatinina post": "1007",
        "colesterol total": "1008",
        "trigliceridos": "1009",
        "albumina": "1010",
        "calcio": "1011",
        "fosforo": "1012",
        "sodio": "1013",
        "sodio post": "1014",
        "potasio": "1015",
        "potasio post": "1016",
        "recuento globulos rojos": "1018",
        "neutrofilos": "1019",
        "linfocitos": "1020",
        "monocitos": "1021",
        "eosinofilos": "1022",
        "basofilos": "1023"
    }

if "nao_mapeados" not in st.session_state:
    st.session_state.nao_mapeados = []

# =========================
# FUNÇÕES
# =========================
def normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto

def ajustar(texto, tamanho):
    return str(texto)[:tamanho].ljust(tamanho)

def formatar_data(data):
    try:
        return pd.to_datetime(data).strftime("%d/%m/%Y")
    except:
        return "01/01/0001"

# =========================
# UI
# =========================
st.title("🔬 Conversor de Exames")

arquivo = st.file_uploader("📂 Upload do Excel", type=["xlsx", "xls"])

if arquivo:
    df = pd.read_excel(arquivo, header=None)

    st.success("Arquivo carregado!")

    # =========================
    # PREVIEW
    # =========================
    st.subheader("📊 Preview do Excel")

    col1, col2 = st.columns(2)

    with col1:
        st.write("🔢 Dimensão:")
        st.write(f"{df.shape[0]} linhas x {df.shape[1]} colunas")

    with col2:
        st.write("📌 Primeiras linhas:")

    st.dataframe(df.head(10), use_container_width=True)

    # =========================
    # EXAMES DETECTADOS
    # =========================
    st.subheader("🧪 Exames detectados")

    try:
        exames = df.iloc[1, 4:].dropna().tolist()
        st.write(exames)
    except:
        st.warning("Não foi possível identificar os exames")

    # =========================
    # BOTÃO CONVERTER
    # =========================
    if st.button("⚙️ Converter"):

        linhas = []
        nao_mapeados = set()
        ignorar = [
            "neutrofilos %",
            "granulocitos inmaduros %",
            "linfocitos %",
            "monocitos %",
            "eosinofilos %",
            "basofilos %"
        ]

        for i in range(2, len(df)):
            nome = ajustar(df.iloc[i, 1], 49)
            data = ajustar(formatar_data(df.iloc[i, 3]), 10)

            for col in range(4, df.shape[1]):

                exame_original = df.iloc[1, col]
                exame = normalizar(exame_original)
                resultado = df.iloc[i, col]

                if exame in ignorar:
                    continue

                if pd.notna(resultado):

                    if exame in st.session_state.depara:

                        codigo = ajustar(st.session_state.depara[exame], 20)
                        resultado_fmt = ajustar(resultado, 10)
                        descricao = ajustar(exame_original, 15)

                        linha = nome + data + codigo + resultado_fmt + (" " * 10) + descricao
                        linhas.append(linha)

                    else:
                        nao_mapeados.add(exame_original)

        st.session_state.nao_mapeados = list(nao_mapeados)

        txt = "\n".join(linhas)

        st.success("TXT gerado com sucesso!")

        st.download_button("📥 Baixar TXT", txt, file_name="saida.txt")

# =========================
# DEPARA
# =========================
st.subheader("📊 DE PARA")
st.dataframe(pd.DataFrame(st.session_state.depara.items(), columns=["Exame", "Código"]))

# =========================
# MAPEAR EXAMES
# =========================
st.subheader("🧠 Mapear Exames")

if st.session_state.nao_mapeados:

    exame_sel = st.selectbox("Exame não mapeado", st.session_state.nao_mapeados)
    codigo = st.text_input("Código")

    if st.button("➕ Adicionar ao DE/PARA"):
        st.session_state.depara[normalizar(exame_sel)] = codigo
        st.success(f"{exame_sel} adicionado!")

else:
    st.info("Nenhum exame pendente")
