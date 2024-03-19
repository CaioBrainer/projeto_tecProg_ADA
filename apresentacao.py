import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json

pio.renderers.default = 'browser' # renderizador mais 'leve' que encontrei na tentativa e erro :)

base_ecomerce = pd.read_parquet('dados/amostra.parquet')
base_ecomerce.dropna(inplace=True)
geojson = json.load(open("geojson/brasil_estados.json"))

compra_por_estado = base_ecomerce.groupby(by='customer_state').size().sort_values(ascending=False).reset_index()
compra_por_estado = compra_por_estado.rename(columns={'customer_state': 'estado do cliente', 0: 'quantidade de compras',})
compra_por_estado['prop'] = compra_por_estado['quantidade de compras'] / compra_por_estado['quantidade de compras'].sum()

tipo_pagamento = base_ecomerce.groupby(by='payment_type').size().reset_index().sort_values(by=0, ascending=False)
tipo_pagamento = tipo_pagamento.rename(columns={'payment_type': 'forma de pagamento', 0: 'quantidade'})
tipo_pagamento['prop'] = tipo_pagamento['quantidade'] / tipo_pagamento['quantidade'].sum()
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
base_ecomerce['day_of_week'] = base_ecomerce['order_purchase_timestamp'].dt.day_name()
sales_by_weekday = base_ecomerce.groupby('day_of_week').size().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index(name='count')


# Converter a coluna de data de compra para datetime
# Criar uma coluna de data agregada (ano-mês) para agrupamento
base_ecomerce['year_month'] = base_ecomerce['order_purchase_timestamp'].dt.to_period('M')
# Agrupar os dados por ano-mês e contar o número de pedidos por mês
monthly_sales = base_ecomerce.groupby('year_month').size()
# Resetar o índice para transformar o índice em uma coluna regular
monthly_sales = monthly_sales.reset_index(name='count')
# Converter 'year_month' para string para facilitar a plotagem
monthly_sales['year_month'] = monthly_sales['year_month'].astype(str)


# Título da página
#st.markdown("<h1 style='text-align: center; color: black;'>Diagramas\n</h1> <br>", unsafe_allow_html=True)
# Menu lateral
opcoes = st.sidebar.selectbox('Escolha uma opção', ['Gráficos','Dados Tabelados'])


# Opção 1: Gráficos
if opcoes == 'Gráficos':
    # Meu código (Caio)
    st.markdown("<h1 style='text-align: center; color: black;'>Relatório gráfico\n</h3> <br>", unsafe_allow_html=True)

    # Gráfico de Barras Empilhadas
    st.title("Quantidade de compras por estado")

    st.code("base_ecomerce=pd.read_parquet('data/amostra.parquet')\n"
            "compra_por_estado=base_ecomerce.groupby(by='customer_state').size().sort_values(ascending=False)\n"
            "geojson=json.load(open('geojson/brasil_estados.json')")

    # Gráfico compras por estado

    fig_map = px.choropleth(compra_por_estado, geojson=geojson, locations='estado do cliente', color='quantidade de compras', scope="south america")
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(width=600, height=600, dragmode=False, paper_bgcolor="white")
    
    fig_bar = px.bar(compra_por_estado.head(10), x='estado do cliente', y='prop')
    fig_bar.update_layout(width=600, height=600, dragmode=False, paper_bgcolor="white")

    fig_forma = px.bar(tipo_pagamento, x='forma de pagamento', y='prop')
    fig_forma.update_layout(width=600, height=600, dragmode=False, paper_bgcolor="white")
    
    st.plotly_chart(fig_map)
    st.title("Proporção de compras por estado")
    st.code("compra_por_estado = base_ecomerce.groupby(by='customer_state').size().sort_values(ascending=False).reset_index()\n"
                "compra_por_estado = compra_por_estado.rename(columns={'customer_state': 'estado do cliente', 0: 'quantidade de compras',})\n"
                "compra_por_estado['prop'] = compra_por_estado['quantidade de compras'] / compra_por_estado['quantidade de compras'].sum()")
    st.plotly_chart(fig_bar)
    
    st.title("Proporção de formas de pagamento")
    st.code("tipo_pagamento = df_unido_amostra.groupby(by='payment_type').size().reset_index().sort_values(by=0, ascending=False)\n"
            "tipo_pagamento = tipo_pagamento.rename(columns={'payment_type': 'forma de pagamento', 0: 'quantidade',})\n"
            "tipo_pagamento['prop'] = tipo_pagamento['quantidade'] / tipo_pagamento['quantidade'].sum()")
    
    st.plotly_chart(fig_forma)

    
    st.title("Relação entre o número de clientes, vendedores e o valor médio do frete para cada estado")

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
    st.title("Qual a quantidade de vendas por Hora do Dia")
    st.code("base_ecomerce['order_purchase_timestamp'] = pd.to_datetime(base_ecomerce['order_purchase_timestamp'])\n"
            "base_ecomerce['hour_of_day'] = base_ecomerce['order_purchase_timestamp'].dt.hour\n"
            "sales_by_hour = base_ecomerce.groupby('hour_of_day').size().reset_index(name='count')")

    fig = px.bar(sales_by_hour, x='hour_of_day', y='count',
                 labels={'hour_of_day': 'Hora do Dia', 'count': 'Quantidade de Vendas'},
                 color='count')
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    st.plotly_chart(fig, use_container_width=True)

    st.title('Tendência de Vendas Mensais')
    
    st.code("base_ecomerce['year_month'] = base_ecomerce['order_purchase_timestamp'].dt.to_period('M')\n"
                "monthly_sales = base_ecomerce.groupby('year_month').size()\n"
                "monthly_sales = monthly_sales.reset_index(name='count')\n"
                "monthly_sales['year_month'] = monthly_sales['year_month'].astype(str)")
    
    fig = px.line(monthly_sales, x='year_month', y='count', title='Tendência de Vendas Mensais')
    fig.update_layout(xaxis_title='Mês/Ano', yaxis_title='Número de Pedidos', xaxis_tickangle=-45)
    st.plotly_chart(fig)

    # st.caption("<p style='text-align: center; color: black;'>vai rpecisar de legenda?\n</p> <br>",
    #           unsafe_allow_html=True)

    
    
    # Visualização de vendas por dia da semana com Plotly e Streamlit
    
    st.title('Vendas por Dia da Semana')
    st.code("base_ecomerce['order_purchase_timestamp'] = pd.to_datetime(base_ecomerce['order_purchase_timestamp'])\n"
            "base_ecomerce['hour_of_day'] = base_ecomerce['order_purchase_timestamp'].dt.hour\n"
            "sales_by_hour = base_ecomerce.groupby('hour_of_day').size().reset_index(name='count')\n"
            "base_ecomerce['day_of_week'] = base_ecomerce['order_purchase_timestamp'].dt.day_name()\n"
            "sales_by_weekday = base_ecomerce.groupby('day_of_week').size().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index(name='count')")
    fig = px.bar(sales_by_weekday, x='day_of_week', y='count', 
                 labels={'count': 'Quantidade de Pedidos', 'day_of_week': 'Dia da Semana'}, 
                 color='day_of_week', color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

    
    # Código Thaysa
    # Tempo de entrega
    # Talvez tenha que usar a order carrier date...
    base_ecomerce['order_approved_at'] = pd.to_datetime(base_ecomerce['order_approved_at']).dt.date
    base_ecomerce['order_delivered_customer_date'] = pd.to_datetime(base_ecomerce['order_delivered_customer_date']).dt.date
    base_ecomerce['order_estimated_delivery_date'] = pd.to_datetime(base_ecomerce['order_estimated_delivery_date']).dt.date
    
    base_ecomerce['tempo de entrega'] = (pd.to_timedelta(base_ecomerce['order_delivered_customer_date'] - base_ecomerce['order_approved_at']).dt.days).astype(int)
    
    base_ecomerce['tempo estimado'] = (pd.to_timedelta(base_ecomerce['order_estimated_delivery_date'] - 
                                                         base_ecomerce['order_approved_at']).dt.days).astype(int)
    
    tempo_de_entrega = base_ecomerce[['customer_state', 'tempo de entrega', 'tempo estimado']]
    tempo_de_entrega['dias_atrasados'] = base_ecomerce['tempo de entrega'] - base_ecomerce['tempo estimado'] 
    df_atrasados = tempo_de_entrega[tempo_de_entrega['dias_atrasados'] > 0].groupby('customer_state').size().reset_index().sort_values(by='customer_state')
    df_qtd = tempo_de_entrega.groupby('customer_state').size().reset_index().sort_values(by='customer_state')
    df_unido = pd.merge(df_qtd, df_atrasados, how='inner', on='customer_state')
    df_unido['prop'] = df_unido['0_y'] / df_unido['0_x']

    filtro = (tempo_de_entrega['dias_atrasados'] > 0) & (tempo_de_entrega['customer_state'].isin(['MA', 'TO', 'AL', 'SE', 'PI']))
    df_atrasos = tempo_de_entrega[filtro]

    st.title('Estados com a maior proporção de atrasos')
    st.code("base_ecomerce['order_approved_at'] = pd.to_datetime(base_ecomerce['order_approved_at']).dt.date\n"
    "base_ecomerce['order_delivered_customer_date'] = pd.to_datetime(base_ecomerce['order_delivered_customer_date']).dt.date\n"
    "base_ecomerce['order_estimated_delivery_date'] = pd.to_datetime(base_ecomerce['order_estimated_delivery_date']).dt.date\n"
    "base_ecomerce['tempo de entrega'] = (pd.to_timedelta(base_ecomerce['order_delivered_customer_date'] -base_ecomerce['order_approved_at']).dt.days).astype(int)\n"
    "base_ecomerce['tempo estimado'] = (pd.to_timedelta(base_ecomerce['order_estimated_delivery_date'] -  base_ecomerce['order_approved_at']).dt.days).astype(int)\n"
    "tempo_de_entrega = base_ecomerce[['customer_state', 'tempo de entrega', 'tempo estimado']]\n"
    "tempo_de_entrega['dias'] = base_ecomerce['tempo estimado'] - base_ecomerce['tempo de entrega']\n"
    "df_atrasados = tempo_de_entrega[tempo_de_entrega['dias'] < 0].groupby('customer_state').size().reset_index().sort_values(by='customer_state')\n"
    "df_qtd = tempo_de_entrega.groupby('customer_state').size().reset_index().sort_values(by='customer_state')\n"
    "df_unido = pd.merge(df_qtd, df_atrasados, how='inner', on='customer_state')\n"
    "df_unido['prop'] = df_unido['0_y'] / df_unido['0_x'])\n")
    
    fig_t = px.bar(df_unido.sort_values(by='prop', ascending=False).head(), x='customer_state', y='prop', labels={'customer_state': 'Estado', 'prop': 'Proporção de atrasos'})
    
    st.plotly_chart(fig_t)

    fig_box = px.box(df_atrasos, x="customer_state", y="dias_atrasados")
    st.plotly_chart(fig_box)

    

# Opção 2: Dados Tabelados

elif opcoes == "Dados Tabelados (falta implementar)":

    st.subheader("Dados Tabelados")
    st.write(compra_por_estado.head(10))
