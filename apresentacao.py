import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json

pio.renderers.default = 'browser' # renderizador mais 'leve' que encontrei na tentativa e erro :)

base_ecomerce = pd.read_parquet('dados/amostra.parquet')
geojson = json.load(open("geojson/brasil_estados.json"))

compra_por_estado = base_ecomerce.groupby(by='customer_state').size().sort_values(ascending=False).reset_index()
compra_por_estado = compra_por_estado.rename(columns={'customer_state': 'estado do cliente', 0: 'quantidade de compras',})

tipo_pagamento = base_ecomerce.groupby(by='payment_type').size().reset_index().sort_values(by=0, ascending=False)
tipo_pagamento = tipo_pagamento.rename(columns={'payment_type': 'forma de pagamento', 0: 'quantidade'})
mapeamento = {'credit_card': 'crédito', 'debit_card': 'débito', 'voucher':'voucher', 'boleto':'boleto'}
tipo_pagamento['forma de pagamento'] = tipo_pagamento['forma de pagamento'].map(mapeamento)

# Código da Luana
clientes_por_estado = base_ecomerce.groupby('customer_state')['customer_id'].nunique().sort_values(
    ascending=False).reset_index()
media_frete_por_estado = base_ecomerce.groupby('customer_state')['freight_value'].mean().sort_values(
    ascending=False).reset_index()
vendedores_por_estado = base_ecomerce.groupby('seller_state')['seller_id'].nunique().sort_values(
    ascending=False).reset_index()

merged_df = clientes_por_estado.merge(media_frete_por_estado, on='customer_state')
merged_df = merged_df.merge(vendedores_por_estado, how='outer', left_on='customer_state', right_on='seller_state')
merged_df.rename(columns={'customer_id': 'clientes_unicos', 'freight_value': 'valor_medio_frete', 'seller_id': 'num_vendedores'}, inplace=True)
merged_df = merged_df.sort_values(by='clientes_unicos', ascending=False)

# Código Alex Amaro
base_ecomerce['order_purchase_timestamp'] = pd.to_datetime(base_ecomerce['order_purchase_timestamp'])
# Create a new column for the hour of the day
base_ecomerce['hour_of_day'] = base_ecomerce['order_purchase_timestamp'].dt.hour
# Grouping by hour of the day
sales_by_hour = base_ecomerce.groupby('hour_of_day').size().reset_index(name='count')

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

    fig_forma = px.bar(tipo_pagamento, x='forma de pagamento', y='quantidade', title='teste')
    fig_forma.update_layout(width=600, height=600, dragmode=False, paper_bgcolor="white")
    
    st.plotly_chart(fig_map)
    st.plotly_chart(fig_bar)
    st.plotly_chart(fig_forma)

    
    st.markdown("<h3 style='text-align: center; color: black;'>Qual a relação entre o número de clientes, \n"
    "vendedores e o valor médio do frete para cada estado?\n</h2> <br>",unsafe_allow_html=True)

    st.code("df_unido_amostra = pd.read_parquet('data/amostra.parquet')\n"
        "clientes_por_estado = df_unido_amostra.groupby('customer_state')['customer_id'].nunique().sort_values(ascending=False).reset_index()\n"
        "media_frete_por_estado = df_unido_amostra.groupby('customer_state')['freight_value'].mean().sort_values(ascending=False).reset_index()\n"
        "vendedores_por_estado = df_unido_amostra.groupby('seller_state')['seller_id'].nunique().sort_values(ascending=False).reset_index()\n"
        "merged_df = clientes_por_estado.merge(media_frete_por_estado, on='customer_state')\n"
        "merged_df = merged_df.merge(vendedores_por_estado, how='outer', left_on='customer_state', right_on='seller_state')")

    # Figura Luana
    fig_frete = go.Figure()    
    # Gráfico de barras
    fig_frete.add_trace(go.Bar(
        x=merged_df['customer_state'],
        y=merged_df['clientes_unicos'],
        name='Número de Clientes',
        marker_color='blue'
    ))
    
    fig_frete.add_trace(go.Bar(
        x=merged_df['customer_state'],
        y=merged_df['num_vendedores'],
        name='Número de Vendedores',
        marker_color='red'
    ))
    
    # Gráfico de linhas
    fig_frete.add_trace(go.Scatter(
        x=merged_df['customer_state'],
        y=merged_df['valor_medio_frete'],
        mode='lines+markers',
        name='Valor Médio do Frete',
        yaxis='y2',
        marker=dict(color='green'),
        line=dict(dash='dash')
    ))
    
    fig_frete.update_layout(
        title='Quantidade de Clientes, Vendedores e Valor Médio do Frete por Estado',
        xaxis=dict(title='Estados', tickangle=35),
        yaxis=dict(title='Número de Clientes e Vendedores', side='left', showgrid=False),
        yaxis2=dict(title='Valor Médio do Frete', overlaying='y', side='right', showgrid=False),
        legend=dict(x=0, y=1.1, traceorder="normal")
    )

    st.plotly_chart(fig_frete)

    # Figura Alex Amaro
    st.markdown("<h3 style='text-align: center; color: black;'>Qual a quantidade de vendas por Hora do Dia\n</h2> <br>",
                unsafe_allow_html=True)
    st.code("base_ecomerce['order_purchase_timestamp'] = pd.to_datetime(base_ecomerce['order_purchase_timestamp'])\n"
            "base_ecomerce['hour_of_day'] = base_ecomerce['order_purchase_timestamp'].dt.hour\n"
            "sales_by_hour = base_ecomerce.groupby('hour_of_day').size().reset_index(name='count')")

    fig = px.bar(sales_by_hour, x='hour_of_day', y='count',
                 labels={'hour_of_day': 'Hora do Dia', 'count': 'Quantidade de Vendas'},
                 color='count')
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    st.plotly_chart(fig, use_container_width=True)

    # st.caption("<p style='text-align: center; color: black;'>vai rpecisar de legenda?\n</p> <br>",
    #           unsafe_allow_html=True)


# Opção 2: Dados Tabelados

elif opcoes == "Dados Tabelados\n":

    st.subheader("Dados Tabelados")
    st.write(compra_por_estado.head(10))
