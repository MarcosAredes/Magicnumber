import streamlit as st
import pandas as pd
from io import BytesIO


st.set_page_config(page_title="Carteira de Investimentos", layout="centered")

st.title("📊 Calculadora de Investimentos")

# 📂 Importar Arquivo Único (Ações + Renda Fixa + Criptos + Moedas)
st.subheader("📂 Importar Arquivo Consolidado")
arquivo = st.file_uploader("Escolha um arquivo Excel (com abas) ou CSV", type=["csv", "xlsx"])

if arquivo:
    try:
        if arquivo.name.endswith(".csv"):
            df_arquivo = pd.read_csv(arquivo)

            # Detectar pelo cabeçalho qual aba preencher
            colunas = set(df_arquivo.columns)

            if {"NOME", "Valor Por Unidade", "Quantidade", "Rendimento por Unidade"} <= colunas:
                st.session_state.acoes = df_arquivo.to_dict(orient="records")

            elif {"NOME", "Valor Investido", "Taxa (%)"} <= colunas:
                st.session_state.renda_fixa = df_arquivo.to_dict(orient="records")

            elif {"Cripto", "Valor Investido (USD)", "Cotação Atual (USD)"} <= colunas:
                st.session_state.cripto = df_arquivo.to_dict(orient="records")

            elif {"Moeda", "Valor Investido ", "Cotação Atual "} <= colunas:
                st.session_state.extern = df_arquivo.to_dict(orient="records")

            st.success("✅ Arquivo CSV importado com sucesso!")

        else:
            # Ler todas as abas do Excel
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

# Criar abas
aba1, aba2, aba3, aba4 = st.tabs(["📈 Ações", "🏦 Renda Fixa", "💰 Criptomoedas", "💶Moedas Externas"])

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

    if st.session_state.acoes:
        df_acoes = pd.DataFrame(st.session_state.acoes)
        df_acoes["Quantidade Total (R$)"] = df_acoes["Valor Por Unidade"] * df_acoes["Quantidade"]
        df_acoes["Expectativa de Recebimentos (R$)"] = df_acoes["Rendimento por Unidade"] * df_acoes["Quantidade"]

    if st.session_state.acoes:
        df_acoes = pd.DataFrame(st.session_state.acoes)
        df_acoes["Quantidade Total (R$)"] = df_acoes["Valor Por Unidade"] * df_acoes["Quantidade"]
        df_acoes["Expectativa de Recebimentos (R$)"] = df_acoes["Rendimento por Unidade"] * df_acoes["Quantidade"]
        df_acoes["Magic Number"] = df_acoes.apply(
            lambda row: row["Valor Por Unidade"] / row["Rendimento por Unidade"]
            if row["Rendimento por Unidade"] > 0 else 0, axis=1
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
    else:
        st.info("➡️ Adicione Ações ou FII para ver os resultados.")



    if st.session_state.acoes:
        st.subheader("❌ Remover Ação")
        remover = st.selectbox("Selecione a ação para remover:", [r["NOME"] for r in st.session_state.acoes])

        if st.button("Remover Ação"):
            st.session_state.acoes = [r for r in st.session_state.acoes if r["NOME"] != remover]
            st.warning(f"Ação {remover} removida!")



        # 📥 Download individual
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

# ==============================
# 🏦 RENDA FIXA
# ==============================
with aba2:
    st.header("🏦 Controle de Renda Fixa")

    if "renda_fixa" not in st.session_state:
        st.session_state.renda_fixa = []

    with st.form("form_renda_fixa"):
        nome = st.text_input("Nome do título (Tesouro, CDB, etc):")
        valor = st.number_input("Valor investido (R$):", min_value=0.01, step=0.01, format="%.2f")
        taxa = st.number_input("Taxa de rendimento mensal (%):", min_value=0.00, step=0.01, format="%.2f")
        add_rf = st.form_submit_button("Adicionar / Atualizar")
# Atualizar / Adicionar Renda Fixa
    if add_rf and nome:
            nome = nome.upper()
            existe = next((inv for inv in st.session_state.renda_fixa if inv["NOME"] == nome), None)
            if existe:
                existe["Valor Investido"] = valor
                existe["Taxa (%)"] = taxa
                st.success(f"Renda fixa {nome} atualizada!")
            else:
                st.session_state.renda_fixa.append({
                    "NOME": nome,
                    "Valor Investido": valor,
                    "Taxa (%)": taxa
                })
                st.success(f"Renda fixa {nome} adicionada!")

        # Remover Renda Fixa
    if st.session_state.renda_fixa:
            st.subheader("❌ Remover Renda Fixa")
            remover = st.selectbox("Selecione o título para remover:", [r["NOME"] for r in st.session_state.renda_fixa])
            if st.button("Remover Renda Fixa"):
                st.session_state.renda_fixa = [r for r in st.session_state.renda_fixa if r["NOME"] != remover]
                st.warning(f"Renda Fixa {remover} removida!")

    if st.session_state.renda_fixa:
        df_rf = pd.DataFrame(st.session_state.renda_fixa)
        df_rf["Rendimento Mensal (R$)"] = df_rf["Valor Investido"] * (df_rf["Taxa (%)"] / 100)

        total_rf = df_rf["Valor Investido"].sum()
        total_rend_rf = df_rf["Rendimento Mensal (R$)"].sum()

        st.subheader("📌 Resultado da Renda Fixa")
        st.dataframe(df_rf, use_container_width=True)

        st.subheader("📊 Totais Gerais")
        st.write(f"💵 **Total Investido em Renda Fixa:** R$ {total_rf:,.2f}")
        st.write(f"📈 **Rendimento Mensal Total:** R$ {total_rend_rf:,.2f}")

        st.bar_chart({
            "Totais (R$)": {
                "Investimento Total": total_rf,
                "Rendimento Mensal": total_rend_rf
            }
        })
    else:
        st.info("➡️ Adicione uma Renda Fixa para ver os resultados.")

    if st.session_state.renda_fixa:
            df_rf = pd.DataFrame(st.session_state.renda_fixa)
            df_rf["Rendimento Mensal (R$)"] = df_rf["Valor Investido"] * (df_rf["Taxa (%)"] / 100)

            # 📥 Download individual
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

with aba3:
    st.header("💰 Criptomoedas")

    # Inicializar lista
    if "cripto" not in st.session_state:
        st.session_state.cripto = []

    # Formulário
    with st.form("form_cripto"):
        nome = st.text_input("Nome da Cripto (ex: BTC, ETH)")
        valor = st.number_input("Valor Investido (USD):", min_value=0.0, step=10.0)
        cotacao = st.number_input("Cotação Atual (USD):", min_value=0.0, step=0.01)
        adicionar = st.form_submit_button("Adicionar/Atualizar")

    # Atualizar / Adicionar Criptos
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

    # Remover Cripto
    if st.session_state.cripto:
        st.subheader("❌ Remover Cripto")
        remover = st.selectbox("Selecione a Cripto para remover:", [c["Cripto"] for c in st.session_state.cripto])
        if st.button("Remover Cripto"):
            st.session_state.cripto = [c for c in st.session_state.cripto if c["Cripto"] != remover]
            st.warning(f"Cripto {remover} removida!")

    # Mostrar tabela e gráficos
    if st.session_state.cripto:
        df_cripto = pd.DataFrame(st.session_state.cripto)

        total_crypto = df_cripto["Valor Investido (USD)"].sum()
        st.write(f"🔗 Total em Criptos: **${total_crypto:,.2f} USD**")

        st.dataframe(df_cripto, use_container_width=True)

        # Gráfico
        st.bar_chart({
            "Criptos (USD)": dict(zip(df_cripto["Cripto"], df_cripto["Valor Investido (USD)"]))
        })
    else:
        st.info("➡️ Adicione uma cripto para ver os resultados.")

    if st.session_state.cripto:
        df_cripto = pd.DataFrame(st.session_state.cripto)

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

with aba4:
    st.header("💶 Moedas Estrangeiras")

    # Inicializar lista
    if "extern" not in st.session_state:
        st.session_state.extern = []

    # Formulário
    with st.form("form_extern"):
        nome = st.text_input(" sigla da moeda, 'USD' 'EUR' 'GBP' ")
        valor = st.number_input("Valor Comprado:", min_value=0.0, step=10.0)
        cotacao = st.number_input("Cotação Atual :", min_value=0.0, step=0.01)
        adicionar = st.form_submit_button("Adicionar/Atualizar")


    # Atualizar / Adicionar Moeda Estrangeira
    if adicionar and nome:
        nome = nome.upper()
        existe = next((m for m in st.session_state.extern if m["Moeda"] == nome), None)
        if existe:
            existe["Valor Investido "] = valor
            existe["Cotação Atual "] = cotacao
            existe["Quantidade"] = valor / cotacao if cotacao > 0 else 0
            st.success(f"Moeda {nome} atualizada!")
        else:
            st.session_state.extern.append({
                "Moeda": nome,
                "Valor Investido ": valor,
                "Cotação Atual ": cotacao,
                "Quantidade": valor / cotacao if cotacao > 0 else 0
            })
            st.success(f"Moeda {nome} adicionada!")


    # Remover Moeda Estrangeira
    if st.session_state.extern:
        st.subheader("❌ Remover Moeda")
        remover = st.selectbox("Selecione a moeda para remover:", [m["Moeda"] for m in st.session_state.extern])
        if st.button("Remover Moeda"):
            st.session_state.extern = [m for m in st.session_state.extern if m["Moeda"] != remover]
            st.warning(f"Moeda {remover} removida!")


    # Mostrar tabela e gráficos
    if st.session_state.extern:
        df_extern = pd.DataFrame(st.session_state.extern)

        total_extern = df_extern["Valor Investido "].sum()
        st.write(f"🔗 Total em Moedas: **${total_extern:,.2f} **")

        st.dataframe(df_extern, use_container_width=True)

        # Gráfico
        st.bar_chart({
            "Moedas": dict(zip(df_extern["Moeda"], df_extern["Valor Investido "]))
        })
    else:
        st.info("➡️ Adicione uma Moeda Externa para ver os resultados.")

    if st.session_state.extern:
            df_extern = pd.DataFrame(st.session_state.extern)

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

        # 📥 Download Consolidado
if st.session_state.acoes or st.session_state.renda_fixa or st.session_state.cripto or st.session_state.extern:
    output_all = BytesIO()
    with pd.ExcelWriter(output_all, engine="openpyxl") as writer:
        if st.session_state.acoes:
            df_acoes.to_excel(writer, index=False, sheet_name="Ações")
        if st.session_state.renda_fixa:
            df_rf.to_excel(writer, index=False, sheet_name="Renda Fixa")
        if st.session_state.cripto:
            df_cripto.to_excel(writer, index=False, sheet_name="Criptos")
        if st.session_state.extern:
            df_extern.to_excel(writer, index=False, sheet_name="Moedas Estrangeiras")
    output_all.seek(0)

    st.download_button(
        "📥 Baixar Planilha Consolidada (Ações + Renda Fixa + Criptos + Moedas)",
        data=output_all,
        file_name="carteira_investimentos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


    )

# ==============================
# 🎨 Toggle de Tema
# ==============================
tema_escuro = st.toggle("🌙 Modo Escuro", value=False)

if tema_escuro:
    # 🌙 CSS Dark Refinado
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0f172a;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            color: #f8fafc !important;
        }
        h1, h2, h3, h4, h5, h6, label, p, span, div {
            color: #f8fafc !important;
        }

        /* Botões principais */
        .stButton button {
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: white !important;
            border-radius: 14px;
            padding: 10px 22px;
            border: none;
            font-weight: 500;
            box-shadow: 0 4px 10px rgba(79,70,229,0.25);
            transition: all 0.3s ease;
            transform: translateY(0);
        }
        .stButton button:hover {
            background: linear-gradient(135deg, #4f46e5, #312e81);
            box-shadow: 0 6px 14px rgba(79,70,229,0.4);
            transform: translateY(-2px);
        }
        .stButton button:disabled {
            background: #334155 !important;
            color: #94a3b8 !important;
            opacity: 0.7;
            box-shadow: none;
            transform: none;
        }

        /* Download button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white !important;
            border-radius: 14px;
            border: none;
            padding: 10px 22px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(16,185,129,0.25);
            transition: all 0.3s ease;
            transform: translateY(0);
        }
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #059669, #047857);
            box-shadow: 0 6px 16px rgba(16,185,129,0.4);
            transform: translateY(-2px);
        }
        .stDownloadButton > button:disabled {
            background: #334155 !important;
            color: #94a3b8 !important;
            opacity: 0.7;
            box-shadow: none;
        }

        /* Inputs */
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 10px;
            border: 1px solid #334155;
            padding: 8px;
            background-color: #1e293b;
            color: #f8fafc !important;
            transition: all 0.2s ease;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput input:focus,
        .stSelectbox div[data-baseweb="select"]:focus {
            border: 1px solid #6366f1;
            box-shadow: 0 0 6px rgba(99,102,241,0.6);
        }

        /* Uploader */
        .stFileUploader {
            background: #1e293b !important;
            border-radius: 14px;
            padding: 14px;
            border: 2px dashed #475569;
            color: #f1f5f9 !important;
            transition: border 0.3s ease;
        }
        .stFileUploader div, .stFileUploader label {
            color: #f1f5f9 !important;
        }
        .stFileUploader:hover {
            border: 2px dashed #6366f1;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background-color: #1e293b;
            border-radius: 12px 12px 0 0;
            color: #e2e8f0;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6366f1 !important;
            color: white !important;
        }

        /* Containers */
        .stForm, .stDataFrame {
            background: #1e293b;
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.5);
            color: #f8fafc;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 📊 Tema escuro para gráficos
    import matplotlib.pyplot as plt
    plt.style.use("dark_background")

else:
    # ☀️ CSS Claro
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f8fafc;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            color: #1e293b;
        }
        h1, h2, h3 {
            color: #0f172a;
            font-weight: 600;
        }

        /* Botões */
        .stButton button {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white !important;
            border-radius: 14px;
            padding: 10px 22px;
            border: none;
            font-weight: 500;
            box-shadow: 0 4px 10px rgba(37,99,235,0.25);
            transition: all 0.3s ease;
            transform: translateY(0);
        }
        .stButton button:hover {
            background: linear-gradient(135deg, #2563eb, #1e40af);
            box-shadow: 0 6px 16px rgba(37,99,235,0.35);
            transform: translateY(-2px);
        }

        /* Containers */
        .stForm, .stDataFrame {
            background: #ffffff;
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.06);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background-color: #e2e8f0;
            border-radius: 12px 12px 0 0;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6 !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 📊 Tema claro para gráficos
    import matplotlib.pyplot as plt
    plt.style.use("default")


# Rodapé
st.markdown(
    """
    <div style="text-align: center; font-size: 14px; margin-top: 35px; color: #475569;">
        By <b style="color:#2563eb;">MASS</b> 🚀 | 
        <a href="https://m4ss.netlify.app" target="_blank" style="text-decoration: none; color:#3b82f6;">Portfólio</a>
    </div>
    """,
    unsafe_allow_html=True
)

