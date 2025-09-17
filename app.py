import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Carteira de Investimentos", layout="centered")

# ==============================
# Tema escuro
# ==============================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode
    js_code = f"""
    const theme = window.parent.document.querySelector('body');
    if ({str(st.session_state.dark_mode).lower()}) {{
        theme.setAttribute('data-baseweb-theme', 'dark');
    }} else {{
        theme.setAttribute('data-baseweb-theme', 'light');
    }}
    """
    st.components.v1.html(f"<script>{js_code}</script>")

# Usar checkbox em vez de st.toggle
#st.checkbox("🌙 Modo Escuro", value=st.session_state.dark_mode, key="toggle", on_change=toggle_theme)

# ==============================
# Título
# ==============================
st.title("📊 Calculadora de Investimentos")

# ==============================
# Importar arquivo consolidado
# ==============================
st.subheader("📂 Importar Arquivo Consolidado")
arquivo = st.file_uploader("Escolha um arquivo Excel (com abas) ou CSV", type=["csv", "xlsx"])

if arquivo:
    try:
        if arquivo.name.endswith(".csv"):
            df_arquivo = pd.read_csv(arquivo)
            colunas = set(df_arquivo.columns)

            if {"NOME", "Valor Por Unidade", "Quantidade", "Rendimento por Unidade"} <= colunas:
                st.session_state.acoes = df_arquivo.to_dict(orient="records")
            elif {"NOME", "Valor Investido", "Taxa (%)"} <= colunas:
                st.session_state.renda_fixa = df_arquivo.to_dict(orient="records")
            elif {"Cripto", "Valor Investido (USD)", "Cotação Atual (USD)"} <= colunas:
                st.session_state.cripto = df_arquivo.to_dict(orient="records")
            elif {"Moeda", "Valor Investido", "Cotação Atual"} <= colunas:
                st.session_state.extern = df_arquivo.to_dict(orient="records")

            st.success("✅ Arquivo CSV importado com sucesso!")

        else:
            xls = pd.ExcelFile(arquivo)
            if "Ações" in xls.sheet_names:
                st.session_state.acoes = pd.read_excel(xls, "Ações").to_dict(orient="records")
            if "Renda Fixa" in xls.sheet_names:
                st.session_state.renda_fixa = pd.read_excel(xls, "Renda Fixa").to_dict(orient="records")
            if "Criptos" in xls.sheet_names:
                st.session_state.cripto = pd.read_excel(xls, "Criptos").to_dict(orient="records")
            if "Moedas Estrangeiras" in xls.sheet_names:
                st.session_state.extern = pd.read_excel(xls, "Moedas Estrangeiras").to_dict(orient="records")

            st.success("✅ Arquivo Excel importado com sucesso!")

    except Exception as e:
        st.error(f"Erro ao importar arquivo: {e}")

# ==============================
# Abas
# ==============================
aba1, aba2, aba3, aba4 = st.tabs(["📈 Ações", "🏦 Renda Fixa", "💰 Criptomoedas", "💶 Moedas Externas"])

# ==============================
# 📈 AÇÕES
# ==============================
with aba1:
    st.header("📈 Controle de Ações")
    if "acoes" not in st.session_state:
        st.session_state.acoes = []

    with st.form("form_acoes"):
        nome = st.text_input("Nome da ação/cota:")
        preco = st.number_input("Valor por unidade (R$):", min_value=0.01, step=0.01, format="%.2f")
        qtd = st.number_input("Quantidade:", min_value=1, step=1)
        dividendo = st.number_input("Rendimento por unidade (R$):", min_value=0.00, step=0.01, format="%.2f")
        add = st.form_submit_button("Adicionar / Atualizar")

        if add and nome:
            nome = nome.upper()
            existe = next((acao for acao in st.session_state.acoes if acao["NOME"] == nome), None)
            if existe:
                existe["Valor Por Unidade"] = preco
                existe["Quantidade"] = qtd
                existe["Rendimento por Unidade"] = dividendo
                st.success(f"Ação {nome} atualizada!")
            else:
                st.session_state.acoes.append({
                    "NOME": nome,
                    "Valor Por Unidade": preco,
                    "Quantidade": qtd,
                    "Rendimento por Unidade": dividendo
                })
                st.success(f"Ação {nome} adicionada!")

    # Remover Ação
    if st.session_state.acoes:
        st.subheader("❌ Remover Ação")
        nomes_acoes = [acao["NOME"] for acao in st.session_state.acoes]
        acao_remover = st.selectbox("Selecione a ação para remover:", [""] + nomes_acoes)
        if st.button("Remover Ação") and acao_remover:
            st.session_state.acoes = [acao for acao in st.session_state.acoes if acao["NOME"] != acao_remover]
            st.success(f"Ação {acao_remover} removida!")

    # Mostrar tabela e gráficos
    if st.session_state.acoes:
        df_acoes = pd.DataFrame(st.session_state.acoes)
        df_acoes["Quantidade Total (R$)"] = df_acoes["Valor Por Unidade"] * df_acoes["Quantidade"]
        df_acoes["Expectativa de Recebimentos (R$)"] = df_acoes["Rendimento por Unidade"] * df_acoes["Quantidade"]
        df_acoes["Magic Number"] = df_acoes.apply(
            lambda row: row["Valor Por Unidade"] / row["Rendimento por Unidade"] if row["Rendimento por Unidade"] > 0 else 0,
            axis=1
        )

        total_invest = df_acoes["Quantidade Total (R$)"].sum()
        total_receb = df_acoes["Expectativa de Recebimentos (R$)"].sum()

        st.subheader("📌 Resultado das Ações")
        st.dataframe(df_acoes, use_container_width=True)

        st.subheader("📊 Totais Gerais")
        st.write(f"💰 **Investimento Total:** R$ {total_invest:,.2f}")
        st.write(f"📈 **Recebimento Total Esperado:** R$ {total_receb:,.2f}")

        st.bar_chart({
            "Totais (R$)": {
                "Investimento Total": total_invest,
                "Recebimentos": total_receb
            }
        })

        # Download
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_acoes.to_excel(writer, index=False, sheet_name="Ações")
        output.seek(0)

        st.download_button(
            label="📥 Baixar Planilha de Ações",
            data=output,
            file_name="acoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("➡️ Adicione Ações ou FII para ver os resultados.")

# ==============================
# 🏦 Renda Fixa
# ==============================
# ==============================
# 🏦 Renda Fixa
# ==============================
with aba2:
    st.header("🏦 Controle de Renda Fixa")
    if "renda_fixa" not in st.session_state:
        st.session_state.renda_fixa = []

    with st.form("form_renda_fixa"):
        nome = st.text_input("Nome do título (Tesouro, CDB, etc):")
        valor = st.number_input("Valor investido (R$):", min_value=0.01, step=0.01, format="%.2f")
        taxa_anual = st.number_input("Taxa de rendimento anual (%):", min_value=0.00, step=0.01, format="%.2f")
        add_rf = st.form_submit_button("Adicionar / Atualizar")

    if add_rf and nome:
        nome = nome.upper()
        existe = next((inv for inv in st.session_state.renda_fixa if inv["NOME"] == nome), None)
        if existe:
            existe["Valor Investido"] = valor
            existe["Taxa Anual (%)"] = taxa_anual
        else:
            st.session_state.renda_fixa.append({
                "NOME": nome,
                "Valor Investido": valor,
                "Taxa Anual (%)": taxa_anual
            })
        st.success(f"Renda fixa {nome} registrada/atualizada!")

    if st.session_state.renda_fixa:  # só roda se houver dados
        df_rf = pd.DataFrame(st.session_state.renda_fixa)

        # Converter taxa anual para mensal
        df_rf["Taxa Mensal (%)"] = ((1 + (df_rf["Taxa Anual (%)"] / 100)) ** (1 / 12) - 1) * 100

        # Rendimentos
        df_rf["Rendimento Mensal (R$)"] = df_rf["Valor Investido"] * (df_rf["Taxa Mensal (%)"] / 100)
        df_rf["Rendimento Anual (R$)"] = df_rf["Valor Investido"] * (df_rf["Taxa Anual (%)"] / 100)

        # Totais
        total_rf = df_rf["Valor Investido"].sum()
        total_rend_mensal = df_rf["Rendimento Mensal (R$)"].sum()
        total_rend_anual = df_rf["Rendimento Anual (R$)"].sum()

        st.subheader("📌 Resultado da Renda Fixa")
        st.dataframe(df_rf, use_container_width=True)

        st.subheader("📊 Totais Gerais")
        st.write(f"💵 **Total Investido em Renda Fixa:** R$ {total_rf:,.2f}")
        st.write(f"📈 **Rendimento Mensal Total:** R$ {total_rend_mensal:,.2f}")
        st.write(f"📆 **Rendimento Anual Total:** R$ {total_rend_anual:,.2f}")

        st.bar_chart({
            "Totais (R$)": {
                "Investimento Total": total_rf,
                "Rendimento Mensal": total_rend_mensal,
                "Rendimento Anual": total_rend_anual
            }
        })

        # 🔽 Só gera Excel se houver dados
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_rf.to_excel(writer, index=False, sheet_name="Renda Fixa")
        output.seek(0)

        st.download_button(
            label="📥 Baixar Planilha de Renda Fixa",
            data=output,
            file_name="renda_fixa.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("➡️ Adicione Renda Fixa para ver os resultados.")


# ==============================
# 💰 Criptomoedas
# ==============================
with aba3:
    st.header("💰 Criptomoedas")
    if "cripto" not in st.session_state:
        st.session_state.cripto = []

    with st.form("form_cripto"):
        nome = st.text_input("Nome da Cripto (ex: BTC, ETH)")
        valor = st.number_input("Valor Investido (USD):", min_value=0.0, step=10.0)
        cotacao = st.number_input("Cotação Atual (USD):", min_value=0.0, step=0.01)
        adicionar = st.form_submit_button("Adicionar/Atualizar")

    if adicionar and nome:
        nome = nome.upper()
        existe = next((c for c in st.session_state.cripto if c["Cripto"] == nome), None)
        if existe:
            existe["Valor Investido (USD)"] = valor
            existe["Cotação Atual (USD)"] = cotacao
            existe["Quantidade"] = valor / cotacao if cotacao > 0 else 0
            st.success(f"Cripto {nome} atualizada!")
        else:
            st.session_state.cripto.append({
                "Cripto": nome,
                "Valor Investido (USD)": valor,
                "Cotação Atual (USD)": cotacao,
                "Quantidade": valor / cotacao if cotacao > 0 else 0
            })
            st.success(f"Cripto {nome} adicionada!")

    if st.session_state.cripto:
        st.subheader("❌ Remover Cripto")
        remover = st.selectbox("Selecione a Cripto para remover:", [c["Cripto"] for c in st.session_state.cripto])
        if st.button("Remover Cripto"):
            st.session_state.cripto = [c for c in st.session_state.cripto if c["Cripto"] != remover]
            st.warning(f"Cripto {remover} removida!")

    if st.session_state.cripto:
        df_cripto = pd.DataFrame(st.session_state.cripto)
        total_crypto = df_cripto["Valor Investido (USD)"].sum()
        st.write(f"🔗 Total em Criptos: **${total_crypto:,.2f} USD**")
        st.dataframe(df_cripto, use_container_width=True)
        st.bar_chart({"Criptos (USD)": dict(zip(df_cripto["Cripto"], df_cripto["Valor Investido (USD)"]))})

        # Download
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_cripto.to_excel(writer, index=False, sheet_name="Criptos")
        output.seek(0)
        st.download_button(
            label="📥 Baixar Planilha de Criptos",
            data=output,
            file_name="criptos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("➡️ Adicione uma cripto para ver os resultados.")

# ==============================
# 💶 Moedas Estrangeiras
# ==============================
with aba4:
    st.header("💶 Moedas Estrangeiras")

    # Inicializar lista
    if "extern" not in st.session_state:
        st.session_state.extern = []

    # Formulário para adicionar/atualizar
    with st.form("form_extern"):
        nome = st.text_input("Sigla da moeda (USD, EUR, GBP)")
        valor = st.number_input("Valor Comprado (R$):", min_value=0.0, step=10.0)
        cotacao = st.number_input("Cotação Atual:", min_value=0.0, step=0.01)
        adicionar = st.form_submit_button("Adicionar/Atualizar")

    if adicionar and nome:
        nome = nome.upper()
        existe = next((m for m in st.session_state.extern if m.get("Moeda") == nome), None)
        if existe:
            existe["Valor Investido"] = valor
            existe["Cotação Atual"] = cotacao
            existe["Quantidade"] = valor / cotacao if cotacao > 0 else 0
            st.success(f"Moeda {nome} atualizada!")
        else:
            st.session_state.extern.append({
                "Moeda": nome,
                "Valor Investido": valor,
                "Cotação Atual": cotacao,
                "Quantidade": valor / cotacao if cotacao > 0 else 0
            })
            st.success(f"Moeda {nome} adicionada!")

    # Remover moeda
    if st.session_state.extern:
        st.subheader("❌ Remover Moeda")
        remover = st.selectbox("Selecione a moeda para remover:", [m["Moeda"] for m in st.session_state.extern])
        if st.button("Remover Moeda"):
            st.session_state.extern = [m for m in st.session_state.extern if m["Moeda"] != remover]
            st.warning(f"Moeda {remover} removida!")

    # Mostrar tabela e gráfico
    if st.session_state.extern:
        df_extern = pd.DataFrame(st.session_state.extern)

        # Padronizar nomes das colunas: remove espaços e renomeia para o padrão
        df_extern.columns = df_extern.columns.str.strip()
        rename_map = {
            "Valor Comprado": "Valor Investido",
            "Cotação Atual": "Cotação Atual"
        }
        df_extern.rename(columns={k: v for k, v in rename_map.items() if k in df_extern.columns}, inplace=True)

        total_extern = df_extern["Valor Investido"].sum()
        st.write(f"🔗 Total em Moedas: **R$ {total_extern:,.2f}**")

        st.dataframe(df_extern, use_container_width=True)

        st.bar_chart({
            "Moedas": dict(zip(df_extern["Moeda"], df_extern["Valor Investido"]))
        })

        # Download Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_extern.to_excel(writer, index=False, sheet_name="Moedas")
        output.seek(0)

        st.download_button(
            label="📥 Baixar Planilha de Moedas Estrangeiras",
            data=output,
            file_name="moedas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("➡️ Adicione uma Moeda Externa para ver os resultados.")


# ==============================
# Download consolidado
# ==============================
if st.session_state.acoes or st.session_state.renda_fixa or st.session_state.cripto or st.session_state.extern:
    output_all = BytesIO()
    with pd.ExcelWriter(output_all, engine="openpyxl") as writer:
        if st.session_state.acoes:
            df_acoes = pd.DataFrame(st.session_state.acoes)
            df_acoes.to_excel(writer, index=False, sheet_name="Ações")
        if st.session_state.renda_fixa:
            df_rf = pd.DataFrame(st.session_state.renda_fixa)
            df_rf.to_excel(writer, index=False, sheet_name="Renda Fixa")
        if st.session_state.cripto:
            df_cripto = pd.DataFrame(st.session_state.cripto)
            df_cripto.to_excel(writer, index=False, sheet_name="Criptos")
        if st.session_state.extern:
            df_extern = pd.DataFrame(st.session_state.extern)
            df_extern.to_excel(writer, index=False, sheet_name="Moedas Estrangeiras")
    output_all.seek(0)

    st.download_button(
        "📥 Baixar Planilha Consolidada (Ações + Renda Fixa + Criptos + Moedas)",
        data=output_all,
        file_name="carteira_investimentos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================
# Rodapé
# ==============================
st.markdown(
    """
    <div style="text-align: center; font-size: 14px; margin-top: 35px; color: #475569;">
        By <b style="color:#2563eb;">MASS</b> 🚀 | 
        <a href="https://m4ss.netlify.app" target="_blank">Portfólio</a>
    </div>
    """, unsafe_allow_html=True
)
