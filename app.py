import os
from datetime import datetime
import dateparser
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Meus Post-its", page_icon="📌", layout="wide")

# Estilização CSS para o visual de Post-it
st.markdown(
    """
    <style>
    .postit {
        background-color: #fefabc;
        border-left: 6px solid #f1c40f;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        color: #333333;
    }
    .postit-header {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    .postit-date {
        font-size: 0.85em;
        color: #7f8c8d;
    }
    </style>
""",
    unsafe_allow_html=True,
)

NOME_ARQUIVO = "lembretes.csv"

# Carregar dados existentes
if os.path.exists(NOME_ARQUIVO):
  df = pd.read_csv(NOME_ARQUIVO)
else:
  df = pd.DataFrame(
      columns=["id", "texto", "data_agendada", "criado_em", "concluido"]
  )

st.title("📌 Quadro de Lembretes estilo Post-it")

# Campo para introduzir a tarefa
with st.container():
  col1, col2 = st.columns([3, 1])
  with col1:
    novo_texto = st.text_input(
        "Novo Lembrete:", placeholder="ex: 25/11 demissão lucas ás 14:00"
    )
  with col2:
    st.write("##")
    if st.button("📌 Criar Post-it", use_container_width=True):
      if novo_texto.strip():
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
        novo_id = int(df["id"].max() + 1) if not df.empty else 1

        nova_linha = pd.DataFrame([{
            "id": novo_id,
            "texto": novo_texto,
            "data_agendada": data_str,
            "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "concluido": False,
        }])

        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(NOME_ARQUIVO, index=False)
        st.success("Post-it adicionado!")
        st.rerun()

st.divider()

# Exibição dos Post-its em grelha
st.subheader("📋 Meus Lembretes Pendentes")

pendentes = df[df["concluido"] == False]

if pendentes.empty:
  st.info("Nenhum lembrete pendente no momento!")
else:
  cols = st.columns(3)
  for index, row in pendentes.iterrows():
    col_idx = index % 3
    with cols[col_idx]:
      st.markdown(
          f"""
                <div class="postit">
                    <div class="postit-header">📌 {row['texto']}</div>
                    <div class="postit-date">⏰ Agendado para: <b>{row['data_agendada']}</b></div>
                    <div class="postit-date">📅 Criado em: {row['criado_em']}</div>
                </div>
            """,
          unsafe_allow_html=True,
      )

      if st.button(f"✅ Concluir #{row['id']}", key=f"btn_{row['id']}"):
        df.loc[df["id"] == row["id"], "concluido"] = True
        df.to_csv(NOME_ARQUIVO, index=False)
        st.rerun()
