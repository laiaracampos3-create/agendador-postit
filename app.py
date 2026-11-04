from datetime import datetime
import sqlite3
import dateparser
import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Agenda & Post-its", page_icon="📅", layout="wide"
)

# --- BANCO DE DADOS SQLITE (Garante que nada apague) ---
CONN = sqlite3.connect("agenda_postits.db", check_same_thread=False)
CURSOR = CONN.cursor()

CURSOR.execute("""
    CREATE TABLE IF NOT EXISTS lembretes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        texto TEXT NOT NULL,
        categoria TEXT NOT NULL,
        data_agendada TEXT,
        criado_em TEXT,
        concluido INTEGER DEFAULT 0
    )
""")
CONN.commit()

# --- ESTILIZAÇÃO VISUAL ---
st.markdown(
    """
    <style>
    .postit {
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.12);
        margin-bottom: 15px;
        color: #2c3e50;
    }
    .postit-amarelo { background-color: #fefabc; border-left: 6px solid #f1c40f; }
    .postit-vermelho { background-color: #ffdde1; border-left: 6px solid #ee5253; }
    .postit-azul { background-color: #d0e8f2; border-left: 6px solid #3498db; }
    .postit-header { font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }
    .postit-date { font-size: 0.85em; color: #555555; }
    </style>
""",
    unsafe_allow_html=True,
)


def carregar_dados():
  return pd.read_sql_query("SELECT * FROM lembretes", CONN)


st.title("📅 Agenda de Compromissos & Post-its")

# --- FORMULÁRIO DE NOVO LEMBRETE ---
with st.container():
  col1, col2, col3 = st.columns([3, 1.5, 1])
  with col1:
    novo_texto = st.text_input(
        "Novo Lembrete:", placeholder="ex: 25/11 demissão lucas ás 14:00"
    )
  with col2:
    categoria = st.selectbox(
        "Prioridade / Cor:",
        options=["Normal 🟡", "Urgente 🔴", "Rotina/DP 🔵"],
    )
  with col3:
    st.write("##")
    if st.button("📌 Salvar Lembrete", use_container_width=True):
      if novo_texto.strip():
        cor_mapa = {
            "Normal 🟡": "amarelo",
            "Urgente 🔴": "vermelho",
            "Rotina/DP 🔵": "azul",
        }
        estilo_cor = cor_mapa.get(categoria, "amarelo")

        data_parsed = dateparser.parse(
            novo_texto,
            languages=["pt"],
            settings={"PREFER_DATES_FROM": "future", "DATE_ORDER": "DMY"},
        )

        data_str = (
            data_parsed.strftime("%d/%m/%Y %H:%M")
            if data_parsed
            else "Sem data definida"
        )
        criado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

        CURSOR.execute(
            """
            INSERT INTO lembretes (texto, categoria, data_agendada, criado_em, concluido)
            VALUES (?, ?, ?, ?, 0)
        """,
            (novo_texto, estilo_cor, data_str, criado_em),
        )
        CONN.commit()
        st.success("Lembrete salvo com sucesso!")
        st.rerun()

st.divider()

# --- CARREGAR DADOS ---
df = carregar_dados()

# --- PAINEL DE EXPORTAÇÃO PARA EXCEL ---
col_titulo, col_excel = st.columns([3, 1])

with col_titulo:
  st.subheader("📋 Meus Lembretes Pendentes")

with col_excel:
  if not df.empty:
    # Gerar arquivo Excel em memória para download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
      df_export = df.copy()
      df_export["concluido"] = df_export["concluido"].map(
          {0: "Pendente", 1: "Concluído"}
      )
      df_export.columns = [
          "ID",
          "Compromisso",
          "Categoria/Cor",
          "Data Agendada",
          "Criado Em",
          "Status",
      ]
      df_export.to_excel(writer, index=False, sheet_name="Agenda_Lembretes")

    st.download_button(
        label="📥 Exportar para Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"agenda_lembretes_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

# --- EXIBIÇÃO EM CARD / POST-IT ---
pendentes = df[df["concluido"] == 0]

if pendentes.empty:
  st.info("Nenhum compromisso pendente no momento!")
else:
  cols = st.columns(3)
  for index, row in pendentes.reset_index(drop=True).iterrows():
    col_idx = index % 3
    classe_css = row["categoria"]

    with cols[col_idx]:
      st.markdown(
          f"""
                <div class="postit postit-{classe_css}">
                    <div class="postit-header">📌 {row['texto']}</div>
                    <div class="postit-date">⏰ Agendado para: <b>{row['data_agendada']}</b></div>
                    <div class="postit-date">📅 Criado em: {row['criado_em']}</div>
                </div>
            """,
          unsafe_allow_html=True,
      )

      if st.button(f"✅ Concluir #{row['id']}", key=f"btn_{row['id']}"):
        CURSOR.execute(
            "UPDATE lembretes SET concluido = 1 WHERE id = ?", (row["id"],)
        )
        CONN.commit()
        st.rerun()

# --- HISTÓRICO / TABELA DE CONCLUÍDOS ---
with st.expander("📁 Ver compromissos já concluídos"):
  concluidos = df[df["concluido"] == 1]
  if concluidos.empty:
    st.write("Nenhum compromisso concluído ainda.")
  else:
    st.dataframe(
        concluidos[
            ["id", "texto", "categoria", "data_agendada", "criado_em"]
        ].rename(
            columns={
                "id": "ID",
                "texto": "Compromisso",
                "categoria": "Cor",
                "data_agendada": "Data Agendada",
                "criado_em": "Criado Em",
            }
        ),
        use_container_width=True,
    )
