import io
import os
from datetime import datetime, time
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Compromissos",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Clean, Executiva e Sofisticada
st.markdown(
    """
    <style>
    /* Fundo da Aplicação */
    .stApp {
        background-color: #F8F9FA;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Tipografia e Títulos */
    h1, h2, h3 {
        color: #1E293B !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    /* Cards de Compromissos Minimalistas */
    .card-compromisso {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
    }
    .card-compromisso:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #CBD5E1;
    }

    /* Bordas Indicadoras de Categoria */
    .border-dp { border-top: 4px solid #6366F1; }
    .border-urgente { border-top: 4px solid #EF4444; }
    .border-reuniao { border-top: 4px solid #0EA5E9; }
    .border-rotina { border-top: 4px solid #10B981; }

    /* Elementos Internos do Card */
    .card-title {
        font-size: 1.1em;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 8px;
    }
    .card-info {
        font-size: 0.88em;
        color: #475569;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .card-obs {
        font-size: 0.85em;
        color: #64748B;
        background-color: #F1F5F9;
        padding: 8px 12px;
        border-radius: 6px;
        margin-top: 10px;
    }
    .card-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 600;
        margin-top: 12px;
    }
    .tag-dp { background-color: #EEF2FF; color: #4F46E5; }
    .tag-urgente { background-color: #FEF2F2; color: #DC2626; }
    .tag-reuniao { background-color: #F0F9FF; color: #0284C7; }
    .tag-rotina { background-color: #ECFDF5; color: #059669; }

    /* Estilo dos Botões */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #CBD5E1;
        background-color: #FFFFFF;
        color: #334155;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #F1F5F9;
        color: #0F172A;
        border-color: #94A3B8;
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

st.title("🗓️ Gestão de Atividades & compromissos")
st.caption("Painel centralizado de pendências e rotinas operacionais.")
st.write("---")

# Painel Lateral - Formulário
with st.sidebar:
  st.subheader("➕ Adicionar Compromisso")

  with st.form("form_compromisso", clear_on_submit=True):
    titulo = st.text_input(
        "Título / Descrição:",
        placeholder="ex: Demissão Lucas",
    )

    col_d, col_h = st.columns(2)
    with col_d:
      data_sel = st.date_input("Data:", value=datetime.now())
    with col_h:
      hora_sel = st.time_input("Horário:", value=time(14, 0))

    categoria = st.selectbox(
        "Categoria:",
        options=[
            "Departamento Pessoal 🏢",
            "Urgente ⚠️",
            "Reunião / Alinhamento 🤝",
            "Rotina Diária 🔄",
        ],
    )

    detalhes = st.text_area(
        "Observações extras:",
        placeholder="Informações complementares...",
        height=80,
    )

    submetido = st.form_submit_button(
        "Salvar no Painel", use_container_width=True
    )

    if submetido:
      if titulo.strip():
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
        st.success("Compromisso registado com sucesso!")
        st.rerun()

# Conteúdo Principal - Abas
aba1, aba2 = st.tabs(["📋 Painel de Pendências", "📊 Relatório & Exportação"])

with aba1:
  pendentes = df[df["concluido"] == False]

  if pendentes.empty:
    st.info("Nenhuma pendência registada no momento.")
  else:
    cols = st.columns(3)
    for index, (idx, row) in enumerate(pendentes.iterrows()):
      col_idx = index % 3

      cat = row.get("categoria", "Departamento Pessoal 🏢")

      mapa_estilos = {
          "Departamento Pessoal 🏢": ("border-dp", "tag-dp", "DP"),
          "Urgente ⚠️": ("border-urgente", "tag-urgente", "URGENTE"),
          "Reunião / Alinhamento 🤝": (
              "border-reuniao",
              "tag-reuniao",
              "REUNIÃO",
          ),
          "Rotina Diária 🔄": ("border-rotina", "tag-rotina", "ROTINA"),
      }
      classe_border, classe_tag, label_tag = mapa_estilos.get(
          cat, ("border-dp", "tag-dp", "GERAL")
      )

      with cols[col_idx]:
        obs_html = (
            f"<div class='card-obs'>📝 {row['detalhes']}</div>"
            if pd.notna(row["detalhes"]) and str(row["detalhes"]).strip()
            else ""
        )

        st.markdown(
            f"""
                <div class="card-compromisso {classe_border}">
                    <div class="card-title">{row['titulo']}</div>
                    <div class="card-info">📅 <b>Data:</b> {row['data_evento']}</div>
                    <div class="card-info">⏰ <b>Horário:</b> {row['hora_evento']} h</div>
                    {obs_html}
                    <div><span class="card-tag {classe_tag}">{label_tag}</span></div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(f"✓ Concluir #{row['id']}", key=f"btn_{row['id']}"):
          df.loc[df["id"] == row["id"], "concluido"] = True
          df.to_csv(NOME_ARQUIVO, index=False)
          st.rerun()

with aba2:
  col_t, col_btn = st.columns([3, 1])

  with col_t:
    st.subheader("📊 Histórico de Compromissos")

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
            "Título",
            "Categoria",
            "Data Evento",
            "Hora Evento",
            "Observações",
            "Data Criação",
            "Status",
        ]
        df_export.to_excel(writer, index=False, sheet_name="Compromissos")

      st.download_button(
          label="📥 Exportar Excel (.xlsx)",
          data=buffer.getvalue(),
          file_name=(
              f"relatorio_compromissos_{datetime.now().strftime('%Y%m%d')}.xlsx"
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
              "titulo": "Título",
              "categoria": "Categoria",
              "data_evento": "Data",
              "hora_evento": "Hora",
              "concluido": "Concluído",
          }
      ),
      use_container_width=True,
  )
