import os
from datetime import datetime
import dateparser
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Meus Post-its", page_icon="📌", layout="wide")

# Estilização CSS com suporte a cores por categoria
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
    /* Cores personalizadas por categoria */
    .postit-amarelo {
        background-color: #fefabc;
        border-left: 6px solid #f1c40f;
    }
    .postit-vermelho {
        background-color: #ffdde1;
        border-left: 6px solid #ee5253;
    }
    .postit-verde {
        background-color: #d4edda;
        border-left: 6px solid #28a745;
    }
    .postit-azul {
        background-color: #d0e8f2;
        border-left: 6px solid #3498db;
    }
    .postit-header {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    .postit-date {
        font-size: 0.85em;
        color: #555555;
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
        columns=["id", "texto", "categoria", "data_agendada", "criado_em", "concluido"]
    )

st.title("📌 Quadro de Lembretes estilo Post-it")

# Formulário para criar lembretes
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
        if st.button("📌 Criar Post-it", use_container_width=True):
            if novo_texto.strip():
                # Mapear categoria para classe CSS
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
                novo_id = int(df["id"].max() + 1) if not df.empty else 1

                nova_linha = pd.DataFrame([{
                    "id": novo_id,
                    "texto": novo_texto,
                    "categoria": estilo_cor,
                    "data_agendada": data_str,
                    "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "concluido": False,
                }])

                df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_csv(NOME_ARQUIVO, index=False)
                st.success("Post-it adicionado!")
                st.rerun()

st.divider()

# Exibição dos Post-its em grade
st.subheader("📋 Meus Lembretes Pendentes")

pendentes = df[df["concluido"] == False]

if pendentes.empty:
    st.info("Nenhum lembrete pendente no momento!")
else:
    cols = st.columns(3)
    for index, (idx, row) in enumerate(pendentes.iterrows()):
        col_idx = index % 3
        classe_css = row.get("categoria", "amarelo")
        
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
                df.loc[df["id"] == row["id"], "concluido"] = True
                df.to_csv(NOME_ARQUIVO, index=False)
                st.rerun()
