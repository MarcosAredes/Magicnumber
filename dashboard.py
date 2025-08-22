import streamlit as st

st.set_page_config(page_title="Calculadora de Dividendos", layout="centered")

st.title("📊 Calculadora de Dividendos")

# Entradas do usuário
preco_acao = st.number_input("Valor da ação/cota (R$):", min_value=0.01, step=0.01, format="%.2f")
dividendo = st.number_input("Valor do rendimento por ação/cota (R$):", min_value=0.01, step=0.01, format="%.2f")

if preco_acao > 0 and dividendo > 0:
    # Quantidade mínima de ações para o rendimento superar o preço de uma ação
    n_acoes = int(preco_acao / dividendo) + 1
    investimento = n_acoes * preco_acao
    rendimento = n_acoes * dividendo

    st.subheader("📌 Resultado:")
    st.write(f"✅ Quantidade mínima de ações/cotas: **{n_acoes}**")
    st.write(f"💰 Valor a investir: **R$ {investimento:,.2f}**")
    st.write(f"📈 Rendimento estimado: **R$ {rendimento:,.2f}**")

    # Gráfico simples comparando valores
    st.bar_chart({
        "Valores (R$)": {
            "Preço de 1 Ação/Cota": preco_acao,
            "Rendimento Total": rendimento,
            "Investimento Total": investimento
        }
    })
else:
    st.info("➡️ Insira os valores para calcular.")