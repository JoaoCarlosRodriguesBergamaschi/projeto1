import streamlit as st
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    page_title="Calendário de Anotações",
    layout="wide"
)

st.title("📅 Calendário de Anotações")

# =========================
# BANCO DE DADOS
# =========================

conn = sqlite3.connect("agenda.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS anotacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    titulo TEXT,
    descricao TEXT,
    categoria TEXT
)
""")

conn.commit()

# =========================
# CORES DAS CATEGORIAS
# =========================

cores_categoria = {
    "Estudos": "🔵",
    "Trabalho": "🟢",
    "Pessoal": "🟡",
    "Importante": "🔴"
}

# =========================
# FORMULÁRIO
# =========================

col1, col2 = st.columns([1, 2])

with col1:

    data = st.date_input("Selecione a Data")

    categoria = st.selectbox(
        "Categoria",
        [
            "Estudos",
            "Trabalho",
            "Pessoal",
            "Importante"
        ]
    )

with col2:

    titulo = st.text_input("Título")

    descricao = st.text_area("Descrição")

# =========================
# SALVAR ANOTAÇÃO
# =========================

if st.button("Salvar Anotação"):

    if titulo == "" or descricao == "":
        st.warning("Preencha todos os campos")

    else:

        data_formatada = data.strftime("%d/%m/%Y")

        cursor.execute(
            """
            INSERT INTO anotacoes
            (data, titulo, descricao, categoria)
            VALUES (?, ?, ?, ?)
            """,
            (
                data_formatada,
                titulo,
                descricao,
                categoria
            )
        )

        conn.commit()

        st.success("Anotação salva com sucesso!")

# =========================
# MOSTRAR ANOTAÇÕES
# =========================

st.divider()

st.subheader("📌 Anotações do Dia")

data_busca = data.strftime("%d/%m/%Y")

cursor.execute(
    """
    SELECT titulo, descricao, categoria
    FROM anotacoes
    WHERE data=?
    """,
    (data_busca,)
)

anotacoes = cursor.fetchall()

if len(anotacoes) == 0:

    st.info("Nenhuma anotação encontrada")

else:

    for titulo, descricao, categoria in anotacoes:

        emoji = cores_categoria[categoria]

        st.markdown(f"""
### {emoji} {titulo}

**Categoria:** {categoria}

**Descrição:**  
{descricao}
""")

        st.divider()

# =========================
# EXPORTAR PDF
# =========================

if st.button("Exportar PDF"):

    if len(anotacoes) == 0:

        st.warning("Não há anotações para exportar")

    else:

        nome_arquivo = f"anotacoes_{data_busca.replace('/', '-')}.pdf"

        pdf = canvas.Canvas(
            nome_arquivo,
            pagesize=letter
        )

        largura, altura = letter

        y = altura - 50

        pdf.setFont("Helvetica-Bold", 18)

        pdf.drawString(
            50,
            y,
            f"Anotações do Dia {data_busca}"
        )

        y -= 40

        for titulo, descricao, categoria in anotacoes:

            pdf.setFont("Helvetica-Bold", 12)

            pdf.drawString(
                50,
                y,
                f"Categoria: {categoria}"
            )

            y -= 20

            pdf.drawString(
                50,
                y,
                f"Título: {titulo}"
            )

            y -= 20

            pdf.setFont("Helvetica", 11)

            pdf.drawString(
                50,
                y,
                f"Descrição: {descricao}"
            )

            y -= 40

            if y < 100:

                pdf.showPage()

                y = altura - 50

        pdf.save()

        with open(nome_arquivo, "rb") as file:

            st.download_button(
                label="⬇️ Baixar PDF",
                data=file,
                file_name=nome_arquivo,
                mime="application/pdf"
            )