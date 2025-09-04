import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Calculadora de Dividendos", layout="centered")

st.title("📊 Calculadora de Dividendos + Planilha Automatizada")

# Lista de ações
if "acoes" not in st.session_state:
    st.session_state.acoes = []

# 1️⃣ Leitor de arquivo
st.subheader("📂 Importar Ações de Arquivo")
arquivo = st.file_uploader("Escolha um arquivo CSV ou Excel", type=["csv", "xlsx"])
if arquivo:
    try:
        if arquivo.name.endswith(".csv"):
            df_arquivo = pd.read_csv(arquivo)
        else:
            df_arquivo = pd.read_excel(arquivo)
        
        # Espera colunas: NOME, Valor Por Unidade, Quantidade, Rendimento por Unidade
        for _, row in df_arquivo.iterrows():
            nome = str(row["NOME"]).upper()
            existe = next((acao for acao in st.session_state.acoes if acao["NOME"] == nome), None)
            if existe:
                existe["Valor Por Unidade"] = row["Valor Por Unidade"]
                existe["Quantidade"] = row["Quantidade"]
                existe["Rendimento por Unidade"] = row["Rendimento por Unidade"]
            else:
                st.session_state.acoes.append({
                    "NOME": nome,
                    "Valor Por Unidade": row["Valor Por Unidade"],
                    "Quantidade": row["Quantidade"],
                    "Rendimento por Unidade": row["Rendimento por Unidade"]
                })
        st.success("Arquivo importado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

# 2️⃣ Formulário para adicionar/atualizar ação
st.subheader("➕ Adicionar Ação/Cota")
with st.form("form_acao"):
    nome = st.text_input("Nome da ação/cota:")
    preco_acao = st.number_input("Valor por unidade (R$):", min_value=0.01, step=0.01, format="%.2f")
    quantidade = st.number_input("Quantidade:", min_value=1, step=1)
    dividendo = st.number_input("Rendimento por unidade (R$):", min_value=0.01, step=0.01, format="%.2f")
    adicionar = st.form_submit_button("Adicionar / Atualizar")

    if adicionar and nome:
        nome = nome.upper()
        existe = next((acao for acao in st.session_state.acoes if acao["NOME"] == nome), None)
        if existe:
            existe["Valor Por Unidade"] = preco_acao
            existe["Quantidade"] = quantidade
            existe["Rendimento por Unidade"] = dividendo
            st.success(f"Ação {nome} atualizada!")
        else:
            st.session_state.acoes.append({
                "NOME": nome,
                "Valor Por Unidade": preco_acao,
                "Quantidade": quantidade,
                "Rendimento por Unidade": dividendo
            })
            st.success(f"Ação {nome} adicionada!")

# 3️⃣ Excluir ação específica
if st.session_state.acoes:
    st.subheader("❌ Remover Ação")
    nomes_acoes = [acao["NOME"] for acao in st.session_state.acoes]
    acao_remover = st.selectbox("Selecione a ação para remover:", [""] + nomes_acoes)
    if st.button("Remover Ação") and acao_remover:
        st.session_state.acoes = [acao for acao in st.session_state.acoes if acao["NOME"] != acao_remover]
        st.success(f"Ação {acao_remover} removida!")

# Mostrar tabela e cálculos
if st.session_state.acoes:
    df = pd.DataFrame(st.session_state.acoes)
    df["Quantidade Total (R$)"] = df["Valor Por Unidade"] * df["Quantidade"]
    df["Expectativa de Recebimentos (R$)"] = df["Rendimento por Unidade"] * df["Quantidade"]
    df["Magic Number (Qtd. Necessária)"] = df.apply(
        lambda row: row["Valor Por Unidade"] / row["Rendimento por Unidade"]
        if row["Rendimento por Unidade"] > 0 else 0, axis=1
    )

    total_investido = df["Quantidade Total (R$)"].sum()
    total_recebimentos = df["Expectativa de Recebimentos (R$)"].sum()

    st.subheader("📌 Resultado das Ações")
    st.dataframe(df, use_container_width=True)

    st.subheader("📊 Totais Gerais")
    st.write(f"💰 **Investimento Total:** R$ {total_investido:,.2f}")
    st.write(f"📈 **Expectativa Total de Recebimentos:** R$ {total_recebimentos:,.2f}")

    st.bar_chart({
        "Totais (R$)": {
            "Investimento Total": total_investido,
            "Expectativa de Recebimentos": total_recebimentos
        }
    })

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    st.download_button(
        label="📥 Baixar Planilha Excel",
        data=output,
        file_name="planilha_acoes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("➡️ Adicione pelo menos uma ação para ver os resultados.")
