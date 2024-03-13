import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import json

pio.renderers.default = 'browser' # renderizador mais 'leve' que encontrei na tentativa e erro :)

base_ecomerce = pd.read_parquet('data/amostra.parquet')
geojson = json.load(open("geojson/brasil_estados.json"))

compra_por_estado = base_ecomerce.groupby(by='customer_state').size().sort_values(ascending=False).reset_index()
compra_por_estado = compra_por_estado.rename(columns={'customer_state': 'estado do cliente', 0: 'quantidade de compras',})

# Título da página
#st.markdown("<h1 style='text-align: center; color: black;'>Diagramas\n</h1> <br>", unsafe_allow_html=True)
# Menu lateral
opcoes = st.sidebar.selectbox('Escolha uma opção', ['Gráficos','Dados Tabelados'])


def customiza_grafico(grafico, titulo_x, titulo_y, titulo_legenda):
    grafico.update_layout(
        xaxis=dict(fixedrange=True, title=titulo_x, tick0=0, dtick=0, tickfont=dict(color='black'),
                   titlefont=dict(color='black', size=25)),

        yaxis=dict(fixedrange=True, title=titulo_y, tickfont=dict(color='black'),
                   titlefont=dict(color='black', size=25)),
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend_title=dict(text=titulo_legenda, font=dict(color='black')),
        legend=dict(
            # title_font_family="Times New Roman",
            font=dict(size=12, color="black"),
            bgcolor="white",
            bordercolor="gray",
            borderwidth=0.75)
    )

    grafico.update_yaxes(showgrid=False, showline=True, linecolor='black', zeroline=False,
                         zerolinecolor='black', ticks="inside", tickson="boundaries", ticklen=5)
    grafico.update_xaxes(showgrid=False, showline=True, zeroline=False)

    return grafico


# Opção 1: Gráficos
if opcoes == 'Gráficos':
    st.markdown("<h1 style='text-align: center; color: black;'>Relatório gráfico\n</h3> <br>", unsafe_allow_html=True)

    # Gráfico de Barras Empilhadas
    st.markdown("<h2 style='text-align: center; color: black;'>Quantidade de compras por estado\n</h1> <br>",
                unsafe_allow_html=True)

    st.code("base_ecomerce=pd.read_parquet('data/amostra.parquet')\n"
            "compra_por_estado=base_ecomerce.groupby(by='customer_state').size().sort_values(ascending=False)\n"
            "geojson=json.load(open('geojson/brasil_estados.json')")

    # Gráfico compras por estado

    fig_map = px.choropleth(compra_por_estado, geojson=geojson, locations='estado do cliente', color='quantidade de compras', scope="south america")
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(width=600, height=600, dragmode=False, paper_bgcolor="white")

    fig_bar = px.bar(compra_por_estado.head(10), x='estado do cliente', y='quantidade de compras', title='Gasdsadas')
    fig_bar.update_layout(width=600, height=600, dragmode=False, paper_bgcolor="white")
    
    st.plotly_chart(fig_map)
    st.plotly_chart(fig_bar)
    # st.caption("<p style='text-align: center; color: black;'>vai rpecisar de legenda?\n</p> <br>",
    #           unsafe_allow_html=True)


# Opção 2: Dados Tabelados
elif opcoes == 'Dados Tabelados':
    st.subheader('Dados Tabelados')

    # Exibindo dados em tabela
    st.write(compra_por_estado.head(10))
