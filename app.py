import io
import os
from datetime import datetime, time
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Agenda & Planejador Pessoal",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Profissional e Feminina
st.markdown(
    """
    <style>
    /* Estilo Global e Fundo */
    .stApp {
        background-color: #FAF6F0;
    }
    
    /* Fontes e Títulos */
    h1, h2, h3 {
        color: #4A3E3D !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Cards Estilo Agenda / Post-it */
    .card-compromisso {
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 18px;
        background-color: #FFFFFF;
        transition: transform 0.2s ease;
    }
    .card-rosa { border-left: 6px solid #E8A0BF; background-color: #FFF5F8; }
    .card-vinho { border-left: 6px solid #C05C7E; background-color: #FDF0F3; }
    .card-dourado { border-left: 6px solid #D4A373; background-color: #FEFAE0; }
    .card-lilás { border-left: 6px solid #B39DDB; background-color: #F3E5F5; }

    .card-header {
        font-weight: 600;
        font-size: 1.15em;
        color: #2D2424;
        margin-bottom: 6px;
    }
    .card-detalhe {
        font-size: 0.9em;
        color: #6D5D5D;
        margin-bottom: 3px;
    }
    .badge-categoria {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: bold;
        color: #FFF;
        margin-top: 5px;
    }
    .bg-rosa { background-color: #E8A0BF; }
    .bg-vinho { background-color: #C05C7E; }
    .bg-dourado { background-color: #D4A373; }
    .bg-lilas { background-color: #B39DDB; }

    /* Botões */
    .stButton>button {
        border-radius: 8px;
        border: none;
        background-color: #C05C7E;
        color: white;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #A34866;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

NOME_ARQUIVO = "lembretes.csv"

# Carregar Dados
if os.path.exists(NOME_ARQUIVO):
  df = pd.read_csv(NOME_ARQUIVO)
else:
  df = pd.DataFrame(
      columns=[
          "id",
          "titulo",
          "categoria",
          "data_evento",
          "hora_evento",
          "detalhes",
          "criado_em",
          "concluido",
      ]
  )

st.title("🌸 Agenda & Planejador de Atividades")
st.caption("Organize seus compromissos e rotinas com praticidade e estilo.")

# Sidebar - Novo Compromisso
with st.sidebar:
  st.header("✨ Novo Compromisso")

  with st.form("form_compromisso", clear_on_submit=True):
    titulo = st.text_input(
        "Título do Compromisso / Tarefa:",
        placeholder="ex: Demissão Lucas",
    )

    col_d, col_h = st.columns(2)
    with col_d:
      data_sel = st.date_input("Data:", value=datetime.now())
    with col_h:
      hora_sel = st.time_input("Horário:", value=time(14, 0))

    categoria = st.selectbox(
        "Categoria / Prioridade:",
        options=[
            "DP & RH 💼",
            "Urgente 🚨",
            "Reunião 🤝",
            "Pessoal / Outros 🎀",
        ],
    )

    detalhes = st.text_area(
        "Observações / Detalhes (opcional):",
        placeholder="Adicione informações importantes aqui...",
        height=70,
    )

    submetido = st.form_submit_button(
        "📌 Agendar Compromisso", use_container_width=True
    )

    if submetido:
      if titulo.strip():
        mapa_estilos = {
            "DP & RH 💼": ("rosa", "bg-rosa"),
            "Urgente 🚨": ("vinho", "bg-vinho"),
            "Reunião 🤝": ("dourado", "bg-dourado"),
            "Pessoal / Outros 🎀": ("lilás", "bg-lilas"),
        }
        estilo, bg_badge = mapa_estilos.get(categoria, ("rosa", "bg-rosa"))

        novo_id = int(df["id"].max() + 1) if not df.empty else 1
        nova_linha = pd.DataFrame([{
            "id": novo_id,
            "titulo": titulo,
            "categoria": categoria,
            "data_evento": data_sel.strftime("%d/%m/%Y"),
            "hora_evento": hora_sel.strftime("%H:%M"),
            "detalhes": detalhes,
            "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "concluido": False,
        }])

        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(NOME_ARQUIVO, index=False)
        st.success("Compromisso agendado com sucesso!")
        st.rerun()

# Conteúdo Principal - Abas
aba1, aba2 = st.tabs(["📋 Minha Agenda", "📊 Histórico & Exportação Excel"])

with aba1:
  pendentes = df[df["concluido"] == False]

  if pendentes.empty:
    st.info("Nenhum compromisso pendente. Sua agenda está em dia! ✨")
  else:
    # Ordenar por data
    cols = st.columns(3)
    for index, (idx, row) in enumerate(pendentes.iterrows()):
      col_idx = index % 3

      cat = row.get("categoria", "DP & RH 💼")
      estilo_map = {
          "DP & RH 💼": "card-rosa",
          "Urgente 🚨": "card-vinho",
          "Reunião 🤝": "card-dourado",
          "Pessoal / Outros 🎀": "card-lilás",
      }
      classe_card = estilo_map.get(cat, "card-rosa")

      with cols[col_idx]:
        obs_html = (
            f"<div class='card-detalhe'>📝 {row['detalhes']}</div>"
            if pd.notna(row["detalhes"]) and str(row["detalhes"]).strip()
            else ""
        )

        st.markdown(
            f"""
                <div class="card-compromisso {classe_card}">
                    <div class="card-header">📌 {row['titulo']}</div>
                    <div class="card-detalhe">📅 <b>Data:</b> {row['data_evento']}</div>
                    <div class="card-detalhe">⏰ <b>Hora:</b> {row['hora_evento']} h</div>
                    {obs_html}
                    <div class="card-detalhe" style="margin-top: 8px;">🏷️ {row['categoria']}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(f"✅ Concluir #{row['id']}", key=f"btn_{row['id']}"):
          df.loc[df["id"] == row["id"], "concluido"] = True
          df.to_csv(NOME_ARQUIVO, index=False)
          st.rerun()

with aba2:
  col_t, col_btn = st.columns([3, 1])

  with col_t:
    st.subheader("📊 Relatório de Compromissos")

  with col_btn:
    if not df.empty:
      buffer = io.BytesIO()
      with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_export = df.copy()
        df_export["concluido"] = df_export["concluido"].map(
            {False: "Pendente", True: "Concluído"}
        )
        df_export.columns = [
            "ID",
            "Compromisso",
            "Categoria",
            "Data",
            "Hora",
            "Detalhes",
            "Criado Em",
            "Status",
        ]
        df_export.to_excel(writer, index=False, sheet_name="Agenda_Oficial")

      st.download_button(
          label="📥 Baixar em Excel (.xlsx)",
          data=buffer.getvalue(),
          file_name=(
              f"agenda_compromissos_{datetime.now().strftime('%Y%m%d')}.xlsx"
          ),
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
          use_container_width=True,
      )

  st.dataframe(
      df.rename(
          columns={
              "id": "ID",
              "titulo": "Compromisso",
              "categoria": "Categoria",
              "data_evento": "Data",
              "hora_evento": "Hora",
              "concluido": "Concluído?",
          }
      ),
      use_container_width=True,
  )
