import streamlit as st
import pandas as pd
import numpy as np
import plotly as px
import plotly.figure_factory as ff
from bokeh.plotting import figure
import matplotlib.pyplot as plt
import altair as alt
from datetime import datetime, timedelta
import plotly.express as px

st.image("logo.png")
st.title('Reporte Operativo')

fact = pd.read_excel('Info Reto.xlsx',sheet_name='facturacion')
gastos = pd.read_excel('Info Reto.xlsx',sheet_name='gastos y costos')
productos = pd.read_excel('Info Reto.xlsx',sheet_name='productos2022')
saldos = pd.read_excel('Info Reto.xlsx',sheet_name='saldos2023')
notas = pd.read_excel('Info Reto.xlsx',sheet_name='notas credito')
devol = pd.read_excel('Info Reto.xlsx',sheet_name='devoluciones')
clientes = pd.read_excel('clientes.xlsx')
cpp = pd.read_excel('Info Reto.xlsx',sheet_name='proveedores')
cpp['FECHA_VENCIMIENTO'] = pd.to_datetime(cpp['FECHA_VENCIMIENTO'])

st.markdown('Seleccione la información que desea desplegar')

# SALDOS
saldos['FECHA_FACTURA'] = pd.to_datetime(saldos['FECHA_FACTURA'])
saldos['FECHA_VENCIMIENTO'] =pd.to_datetime(saldos['FECHA_VENCIMIENTO'])
suma_por_cliente = saldos.groupby('NOMBRE')['MONTO ADEUDADO'].sum()
saldos['ADEUDO CLIENTE'] = saldos['NOMBRE'].map(suma_por_cliente)
saldos['% DEL ADEUDO'] = saldos['ADEUDO CLIENTE']/saldos['ADEUDO CLIENTE'].sum()
saldos.head()

suma_por_cliente = saldos.groupby('NOMBRE')['MONTO ADEUDADO'].sum()
suma_por_cliente = pd.DataFrame(suma_por_cliente)
suma_por_cliente['% de costo'] = suma_por_cliente['MONTO ADEUDADO']/suma_por_cliente['MONTO ADEUDADO'].sum()*100
psuma_por_cliente = pd.Series(suma_por_cliente['% de costo'])
suma_por_cliente = pd.Series(suma_por_cliente['MONTO ADEUDADO'])
saldos['ADEUDO POR CLIENTE'] = saldos['NOMBRE'].map(suma_por_cliente)
saldos['% DE ADEUDO'] = saldos['NOMBRE'].map(psuma_por_cliente)
saldos['FECHA_FACTURA'] = pd.to_datetime(saldos['FECHA_FACTURA'])
saldos['FECHA_VENCIMIENTO'] =pd.to_datetime(saldos['FECHA_VENCIMIENTO'])
suma_por_cliente = saldos.groupby('NOMBRE')['MONTO ADEUDADO'].sum()
saldos['ADEUDO CLIENTE'] = saldos['NOMBRE'].map(suma_por_cliente)
saldos['% DEL ADEUDO'] = saldos['ADEUDO CLIENTE']/saldos['ADEUDO CLIENTE'].sum()
saldos.head()
suma_por_cliente = saldos.groupby('NOMBRE')['MONTO ADEUDADO'].sum()
suma_por_cliente = pd.DataFrame(suma_por_cliente)
suma_por_cliente['% de costo'] = suma_por_cliente['MONTO ADEUDADO']/suma_por_cliente['MONTO ADEUDADO'].sum()*100
psuma_por_cliente = pd.Series(suma_por_cliente['% de costo'])
suma_por_cliente = pd.Series(suma_por_cliente['MONTO ADEUDADO'])
saldos['ADEUDO POR CLIENTE'] = saldos['NOMBRE'].map(suma_por_cliente)
saldos['% DE ADEUDO'] = saldos['NOMBRE'].map(psuma_por_cliente)

## Info útil
topdeudores = saldos.copy()
def replace_deudores(x):
    top_10 = topdeudores.groupby('NOMBRE')['ADEUDO POR CLIENTE'].sum().nlargest(10).index
    if x not in top_10:
        return 'OTROS'  # Valor de reemplazo
    else:
        return x
topdeudores['NOMBRE'] = topdeudores['NOMBRE'].apply(replace_deudores)
topdeudores.groupby('NOMBRE')['ADEUDO POR CLIENTE'].sum()


agree = st.button('Saldos')
if agree:
    click = alt.selection_multi(encodings=['color'])
    tomorrow = pd.to_datetime(pd.to_datetime('2023-01-01') + timedelta(days=1))
    datas = saldos[saldos['FECHA_VENCIMIENTO'] >= tomorrow ]

    # Define tu esquema de colores personalizado
    custom_colors = ['#ba1424','#9f4d4c','#746c6c']

    # Crea una escala de colores utilizando tu esquema personalizado
    color_scale = alt.Scale(domain=list(datas['MAG_PLAZO'].unique()), range=custom_colors)

    hist = alt.Chart(datas).mark_bar().encode(
        y=alt.Y('sum(MONTO ADEUDADO)', title = 'Total adudado por plazo'),
        x=alt.X('MAG_PLAZO', title = 'Plazo'),
        color=alt.condition(click, 'MAG_PLAZO', alt.value('lightgray'))
    ).add_selection(
        click
    )

    # Utiliza la escala de colores en tu gráfica
    chart = alt.Chart(datas).mark_bar().encode(
        x=alt.X('FECHA_VENCIMIENTO:T', title = 'Fecha de vencimiento'),
        y='MONTO ADEUDADO',
        color=alt.Color('MAG_PLAZO', scale=color_scale),  # Utiliza la escala de colores personalizada
        tooltip = ['FECHA_VENCIMIENTO:T','MONTO ADEUDADO','NOMBRE']
    ).transform_filter(
        click
    ).properties(
        title="Monto adeudado por fecha y plazo"
    )    

    hist|chart
    
    monto_sorted = saldos.sort_values(by='MONTO ADEUDADO', ascending=False)
    # Crear el gráfico de barras
    monto_graf = alt.Chart(monto_sorted).mark_bar().encode(
        x=alt.X(
            'NOMBRE',
            title='Nombre del cliente',
            axis=alt.Axis(titleColor='black', labelAngle=45),
            sort=alt.EncodingSortField(field='MONTO ADEUDADO', order='descending')
        ),
        y=alt.Y(
            'MONTO ADEUDADO',
            title="Monto adeudado",
            axis=alt.Axis(titleColor="black")
        ),
        color=alt.Color('MAG_PLAZO', scale=color_scale),
        tooltip = ['MONTO ADEUDADO','FECHA_VENCIMIENTO']

    ).properties(
        title="Monto Adeudado por Cliente"
    )
    monto_graf


# PRODUCTOS
productos['VENTA TOTAL'] = productos['CANT'] * productos['PRECIO_UNITARIO']
productos['COSTO TOTAL'] = productos['CANT'] * productos['COSTO_UNITARIO_CALCULADO']
productos['MARGEN TOTAL'] = productos['CANT'] * productos['MARGEN_UNITARIO_CALCULADO']
productos['MARGEN %'] = productos['MARGEN_UNITARIO_CALCULADO']/productos['PRECIO_UNITARIO']*100
suma_por_cliente = productos.groupby('NOMBRE_CLIENTE')['MARGEN_UNITARIO_CALCULADO'].sum()
productos['MARGEN CLIENTE'] = productos['NOMBRE_CLIENTE'].map(suma_por_cliente)
productos['% DEL MARGEN CLIENTE'] = productos['MARGEN CLIENTE']/productos['MARGEN CLIENTE'].sum()
venta_por_producto = productos.groupby('CVE_ART')['VENTA TOTAL'].sum()
venta_por_producto = pd.DataFrame(venta_por_producto)
venta_por_producto['% de venta'] = venta_por_producto['VENTA TOTAL']/venta_por_producto['VENTA TOTAL'].sum()*100
pventa_por_producto = pd.Series(venta_por_producto['% de venta'])
venta_por_producto = pd.Series(venta_por_producto['VENTA TOTAL'])
productos['VENTA POR PRODUCTO'] = productos['CVE_ART'].map(venta_por_producto)
productos['% DE VENTA PRODUCTO'] = productos['CVE_ART'].map(pventa_por_producto)
costo_por_producto = productos.groupby('CVE_ART')['COSTO TOTAL'].sum()
costo_por_producto = pd.DataFrame(costo_por_producto)
costo_por_producto['% de costo'] = costo_por_producto['COSTO TOTAL']/costo_por_producto['COSTO TOTAL'].sum()*100
pcosto_por_producto = pd.Series(costo_por_producto['% de costo'])
costo_por_producto = pd.Series(costo_por_producto['COSTO TOTAL'])
productos['COSTO POR PRODUCTO'] = productos['CVE_ART'].map(costo_por_producto)
productos['% DE COSTO PRODUCTO'] = productos['CVE_ART'].map(pcosto_por_producto)
margen_por_producto = productos.groupby('CVE_ART')['MARGEN TOTAL'].sum()
margen_por_producto = pd.DataFrame(margen_por_producto)
margen_por_producto['% de margen'] = margen_por_producto['MARGEN TOTAL']/margen_por_producto['MARGEN TOTAL'].sum()*100
pmargen_por_producto = pd.Series(margen_por_producto['% de margen'])
margen_por_producto = pd.Series(margen_por_producto['MARGEN TOTAL'])
productos['MARGEN POR PRODUCTO'] = productos['CVE_ART'].map(margen_por_producto)
productos['% DE MARGEN PRODUCTO'] = productos['CVE_ART'].map(pmargen_por_producto)

## Info útil
nclientes = productos.drop_duplicates(subset='NOMBRE_CLIENTE')
prod = productos.drop_duplicates(subset='CVE_ART')
topclientes = productos.copy()
topproductos = productos.copy()
def replace_clientes(x):
    top_10 = topclientes.groupby('NOMBRE_CLIENTE')['MARGEN CLIENTE'].sum().nlargest(10).index
    if x not in top_10:
        return 'OTRO CLIENTE'  # Valor de reemplazo
    else:
        return x
topclientes['NOMBRE_CLIENTE'] = topclientes['NOMBRE_CLIENTE'].apply(replace_clientes)
def replace_productos(x):
    top_10 = topproductos.groupby('CVE_ART')['MARGEN POR PRODUCTO'].sum().nlargest(10).index
    if x not in top_10:
        return 'OTROS'  # Valor de reemplazo
    else:
        return x
topproductos['CVE_ART'] = topproductos['CVE_ART'].apply(replace_productos)


agree2 = st.button('Productos')
if agree2:
    margenu = topproductos[topproductos['MARGEN_UNITARIO_CALCULADO']>0]
    margenu['% DE MARGEN PRODUCTO'] = margenu['% DE MARGEN PRODUCTO'].round(2)

    interval=alt.selection_interval()
    precio =alt.Chart(margenu).mark_point().encode(
        x = alt.X('COSTO_UNITARIO_CALCULADO', title ='Costo Unitario', axis = alt.Axis(titleColor = 'black')),
        y = alt.Y('PRECIO_UNITARIO', title = ' Precio unitario', axis = alt.Axis(titleColor= 'black')),
        color=alt.condition(interval,'NOMBRE_VENDEDOR',alt.value('lightgrey')),
        tooltip = ['MARGEN_UNITARIO_CALCULADO','NOMBRE_VENDEDOR','CANT','MARGEN TOTAL','CVE_DOC'],
        size = 'CANT'
    ).properties(
        title='Productos Vendidos', width=800
    ).add_selection(
        interval
    )

    barras =alt.Chart(margenu).mark_arc().encode(
        angle='sum(MARGEN TOTAL)',
        color='NOMBRE_VENDEDOR',
        tooltip = ['sum(MARGEN TOTAL)','sum(CANT)','count(NOMBRE_VENDEDOR)'],
    ).transform_filter(
        interval
    ).properties(title='Aportación a utilidad bruta por vendedor', width=400)

    barras2 =alt.Chart(margenu).mark_arc().encode(
        angle='sum(MARGEN TOTAL)',
        color='CVE_ART',
        tooltip = ['sum(MARGEN TOTAL)','sum(CANT)'],
    ).transform_filter(
        interval
    ).properties(title='Aportación a utilidad bruta por producto', width=400)

    precio & (barras | barras2)
    
# GASTOS
lista_gc = pd.read_excel('Lista de gastos.xlsx')
gastos = pd.merge(gastos, lista_gc, on='TIPO_GASTO')

gastos['FECHA'] = pd.to_datetime(gastos['FECHA'])
gastos['AÑO'] = gastos['FECHA'].dt.year
gastos['MES'] = gastos['FECHA'].dt.month

egreso_por_proveedor = gastos.groupby('PROVEEDOR')['TOTAL_SAT'].sum()
egreso_por_proveedor = pd.DataFrame(egreso_por_proveedor)
egreso_por_proveedor['% de egreso'] = egreso_por_proveedor['TOTAL_SAT']/egreso_por_proveedor['TOTAL_SAT'].sum()*100
pegreso_por_proveedor = pd.Series(egreso_por_proveedor['% de egreso'])
egreso_por_proveedor = pd.Series(egreso_por_proveedor['TOTAL_SAT'])
gastos['EGRESO POR PROVEEDOR'] = gastos['PROVEEDOR'].map(egreso_por_proveedor)
gastos['% DE EGRESO PROVEEDOR'] = gastos['PROVEEDOR'].map(pegreso_por_proveedor)

egreso_por_clase = gastos.groupby('CLASIFICACION')['TOTAL_SAT'].sum()
egreso_por_clase = pd.DataFrame(egreso_por_clase)
egreso_por_clase['% de egreso'] = egreso_por_clase['TOTAL_SAT']/egreso_por_clase['TOTAL_SAT'].sum()*100
pegreso_por_clase = pd.Series(egreso_por_clase['% de egreso'])
egreso_por_clase = pd.Series(egreso_por_clase['TOTAL_SAT'])
gastos['EGRESO POR TIPO GASTO/COSTO'] = gastos['CLASIFICACION'].map(egreso_por_clase)
gastos['% DE EGRESO TIPO GASTO/COSTO'] = gastos['CLASIFICACION'].map(pegreso_por_clase)

gastos = gastos.drop(['Unnamed: 2','Unnamed: 3','Unnamed: 4','Unnamed: 5'],axis = 1)

gastos.head()

# Info útil
proveedores = gastos.drop_duplicates(subset='PROVEEDOR')
g_c = gastos.drop_duplicates(subset='CLASIFICACION')
topproveedores = gastos.copy()
def replace_proveedores(x):
    top_10 = topproveedores.groupby('PROVEEDOR')['EGRESO POR PROVEEDOR'].sum().nlargest(20).index
    if x not in top_10:
        return 'OTROS'  # Valor de reemplazo
    else:
        return x
topproveedores['PROVEEDOR'] = topproveedores['PROVEEDOR'].apply(replace_proveedores)

agree3 = st.button('Gastos')
if agree3:
    color_scale = ['green','yellow', 'red']

    graf = px.sunburst(gastos, color='TOTAL_SAT', values='TOTAL_SAT',
                      path=['CLASIFICACION', 'TIPO_GASTO'], hover_name='TIPO_GASTO',
                      title='Gastos y costos', color_continuous_scale=color_scale)
    
    graf2 = px.treemap(topproveedores, values='TOTAL_SAT', path=['AÑO', 'CLASIFICACION', 'PROVEEDOR'],
           hover_name='PROVEEDOR', color_discrete_sequence=['red', 'yellow', 'green', 'blue'])
    
    graf
    graf2
 
 
# FACTURACIÓN
fact = pd.merge(fact, clientes, on='CVE_CLPV')
fact['CVE_VEND'] = fact['CVE_VEND'].astype('category')
fact['FECHA_ENT'] = pd.to_datetime(fact['FECHA_ENT'])
fact['FECHA_DOC'] = pd.to_datetime(fact['FECHA_DOC'])
fact['FECHA_VEN'] = pd.to_datetime(fact['FECHA_VEN'])
fact['AÑO'] = fact['FECHA_DOC'].dt.year
fact['MES'] = fact['FECHA_DOC'].dt.month

fact['TOTAL'] = fact['CAN_TOT'] - fact['DES_TOT']
suma_por_cliente = fact.groupby('NOMBRE CLIENTE')['TOTAL'].sum()
suma_por_cliente = pd.DataFrame(suma_por_cliente)
suma_por_cliente['% de fact'] = suma_por_cliente['TOTAL']/suma_por_cliente['TOTAL'].sum()*100
psuma_por_cliente = pd.Series(suma_por_cliente['% de fact'])
suma_por_cliente = pd.Series(suma_por_cliente['TOTAL'])
fact['FACTURACION POR CLIENTE'] = fact['NOMBRE CLIENTE'].map(suma_por_cliente)
fact['% DE FACTURACION'] = fact['NOMBRE CLIENTE'].map(psuma_por_cliente)

suma_por_vendedor = fact.groupby('CVE_VEND')['TOTAL'].sum()
suma_por_vendedor = pd.DataFrame(suma_por_vendedor)
suma_por_vendedor['% de fact'] = suma_por_vendedor['TOTAL']/suma_por_vendedor['TOTAL'].sum()*100
psuma_por_vendedor = pd.Series(suma_por_vendedor['% de fact'])
suma_por_vendedor = pd.Series(suma_por_vendedor['TOTAL'])
fact['FACTURACION POR VENDEDOR'] = fact['CVE_VEND'].map(suma_por_vendedor)
fact['% DE FACTURACION VENDEDOR'] = fact['CVE_VEND'].map(psuma_por_vendedor)

tclif = fact.copy()
def replace_clientesf(x):
    top_10 = tclif.groupby('NOMBRE CLIENTE')['CAN_TOT'].sum().nlargest(10).index
    if x not in top_10:
        return 'OTRO CLIENTE'  # Valor de reemplazo
    else:
        return x
tclif['NOMBRE CLIENTE'] = tclif['NOMBRE CLIENTE'].apply(replace_clientesf)


agree4 = st.button('Facturación')
if agree4:
    
    ## Gráfica 1
    alt.data_transformers.enable('default', max_rows=None)
    # Convertir las columnas 'AÑO' y 'MES' a enteros
    fact['AÑO'] = fact['AÑO'].astype(int)
    fact['MES'] = fact['MES'].astype(int)
    # Crear una selección de año con un menú desplegable
    year_selection = alt.binding_select(options=list(fact['AÑO'].unique()), name='Año:')
    year_selector = alt.selection_single(fields=['AÑO'], bind=year_selection, init={'AÑO': fact['AÑO'].max()})
    # Crear el gráfico de barras
    a = alt.Chart(fact).mark_bar().encode(
        x=alt.X('FECHA_DOC', title='Fecha'),
        y=alt.Y('TOTAL', title='Monto acumulado de facturas vencidas'),
        color=alt.Color('MAG_FACT', scale=alt.Scale(scheme='reds'), title='Tipo de factura'),
        tooltip=['TOTAL', 'NOMBRE CLIENTE', 'CVE_DOC', 'CVE_VEND'],
    ).properties(
        title='Facturas emitidas',
        height=400,
        width=800
    ).add_selection(year_selector).transform_filter(year_selector)
    
    ## Gráfica 2
    # Crear una selección de año con un menú desplegable
    year_selection = alt.binding_select(options=list(fact['AÑO'].unique()), name='Año:')
    year_selector = alt.selection_single(fields=['AÑO'], bind=year_selection, init={'AÑO': fact['AÑO'].max()})
    # Crear el gráfico de barras
    b = alt.Chart(fact).mark_bar().encode(
        x=alt.X('MES:O', title='MES'),
        y=alt.Y('sum(CAN_TOT)', title='Monto acumulado de facturas vencidas'),
        color=alt.Color('MES:O', scale=alt.Scale(scheme='tableau20'), title='Tipo de factura'),
        tooltip=['sum(TOTAL)', 'count(CVE_DOC)'],
    ).properties(
        title='Total de facturas por mes',
        height=400,
        width=200
    ).add_selection(year_selector).transform_filter(year_selector)

    ## Gráfica 3
    alt.data_transformers.enable('default', max_rows=None)
    # Convertir la columna 'AÑO' a entero
    tclif['AÑO'] = tclif['AÑO'].astype(int)
    # Crear una selección de año con un menú desplegable
    year_selection = alt.binding_select(options=list(tclif['AÑO'].unique()), name='Año:')
    year_selector = alt.selection_single(fields=['AÑO'], bind=year_selection, init={'AÑO': tclif['AÑO'].max()})
    # Crear el gráfico de barras
    c = alt.Chart(tclif).mark_arc().encode(
        angle='sum(TOTAL)',
        color=alt.Color('NOMBRE CLIENTE', scale=alt.Scale(scheme='tableau20')),
        tooltip=['sum(CAN_TOT)', 'NOMBRE CLIENTE'],
    ).properties(
        title='Facturación por cliente',
        width=400
    ).add_selection(year_selector).transform_filter(year_selector)

    ## Gráfica 4
    alt.data_transformers.enable('default', max_rows=None)

    # Crear una selección de año con un menú desplegable
    year_selection = alt.binding_select(options=list(tclif['AÑO'].unique()), name='Año:')
    year_selector = alt.selection_single(fields=['AÑO'], bind=year_selection, init={'AÑO': tclif['AÑO'].max()})

    # Crear el gráfico de barras
    d = alt.Chart(tclif).mark_arc().encode(
        angle='sum(CAN_TOT)',
        color=alt.Color('CVE_VEND', scale=alt.Scale(scheme='tableau20')),
        tooltip=['sum(CAN_TOT)','CVE_VEND'],
    ).properties(
        title='Facturación por Vendedor',
        width=400
    ).add_selection(year_selector).transform_filter(year_selector)

    a
    b
    c
    d
    
# NOTAS DE CRÉDITO
notas = pd.merge(notas, clientes, on='CVE_CLPV')
notas['CVE_VEND'] = notas['CVE_VEND'].astype('category')
notas['FECHA_DOC'] = pd.to_datetime(notas['FECHA_DOC'])
notas['AÑO'] = notas['FECHA_DOC'].dt.year
notas['MES'] = notas['FECHA_DOC'].dt.month

suma_por_cliente = notas.groupby('NOMBRE CLIENTE')['CAN_TOT'].sum()
suma_por_cliente = pd.DataFrame(suma_por_cliente)
suma_por_cliente['% de fact'] = suma_por_cliente['CAN_TOT'] / suma_por_cliente['CAN_TOT'].sum() * 100
psuma_por_cliente = pd.Series(suma_por_cliente['% de fact'])
suma_por_cliente = pd.Series(suma_por_cliente['CAN_TOT'])
notas['FACTURACION POR CLIENTE'] = notas['NOMBRE CLIENTE'].map(suma_por_cliente)
notas['% DE FACTURACION'] = notas['NOMBRE CLIENTE'].map(psuma_por_cliente)

suma_por_vendedor = notas.groupby('CVE_VEND')['CAN_TOT'].sum()
suma_por_vendedor = pd.DataFrame(suma_por_vendedor)
suma_por_vendedor['% de fact'] = suma_por_vendedor['CAN_TOT'] / suma_por_vendedor['CAN_TOT'].sum() * 100
psuma_por_vendedor = pd.Series(suma_por_vendedor['% de fact'])
suma_por_vendedor = pd.Series(suma_por_vendedor['CAN_TOT'])
notas['FACTURACION POR VENDEDOR'] = notas['CVE_VEND'].map(suma_por_vendedor)
notas['% DE FACTURACION VENDEDOR'] = notas['CVE_VEND'].map(psuma_por_vendedor)
    
agree5 = st.button('Notas de crédito')
if agree5:
    
    ## Gráfica 1
    alt.data_transformers.enable('default', max_rows=None)
    # Convertir las columnas 'AÑO' y 'MES' a enteros
    notas['AÑO'] = notas['AÑO'].astype(int)
    notas['MES'] = notas['MES'].astype(int)

    # Crear una selección de lista desplegable para seleccionar el año
    year_selection = alt.binding_select(options=list(notas['AÑO'].unique()), name='Año:')
    year_selector = alt.selection_single(fields=['AÑO'], bind=year_selection, init={'AÑO': notas['AÑO'].max()})

    # Crear el gráfico de barras
    g1 = alt.Chart(notas).mark_bar().encode(
        x=alt.X('FECHA_DOC', title='Fecha'),
        y=alt.Y('CAN_TOT', title='Monto acumulado de facturas vencidas'),
        color=alt.Color('MAG_NOTAS', scale=alt.Scale(scheme='reds'), title='Tipo de factura'),
        tooltip='CAN_TOT',
    ).properties(
        title='Notas de crédito',
        height=400,
        width=800
    ).add_selection(year_selector).transform_filter(year_selector)

    
    ## Gráfica 2
    g2 = alt.Chart(x).mark_bar().encode(
        x=alt.X('MES:O',
                title='MES',
    ),
        y=alt.Y('sum(CAN_TOT)',
                title='Monto acumulado de notas de crédito'),
        color=alt.Color('MES:O',scale=alt.Scale(scheme='tableau20'),
                        title='Tipo de factura'),
        tooltip=['sum(CAN_TOT)','count(CAN_TOT)'],
    ).properties(
        title='Total de notas de crédito por mes',
        height=400,
        width=200
    ).add_selection(year_selector).transform_filter(year_selector)
    
    g1
    g2
    
# PROVEEDORES

agree5 = st.button('Proveedores')
if agree5:
    
    ## Gráfica 1
    datap = cpp[cpp['FECHA_VENCIMIENTO'] >= tomorrow ]

    # Utiliza la escala de colores en tu gráfica
    pago = alt.Chart(datap).mark_bar(color = '#ba1424').encode(
        x=alt.X('FECHA_VENCIMIENTO:T', title = 'Fecha de vencimiento'),
        y=alt.Y('MONTO ADEUDADO', title = 'Monto a pagar'),
        #color=alt.Color('MAG_PLAZO', scale=color_scale),  # Utiliza la escala de colores personalizada
        tooltip = ['FECHA_VENCIMIENTO:T','MONTO ADEUDADO'])

    pago

     ## Gráfica 2
    chart = alt.Chart(datas).mark_bar().encode(
        x=alt.X('FECHA_VENCIMIENTO:T', title='Fecha de vencimiento'),
        y=alt.Y('sum(MONTO ADEUDADO)', title='Monto adeudado'),
        color=alt.value('green'),
        tooltip=['FECHA_VENCIMIENTO:T', 'MONTO ADEUDADO', 'NOMBRE']
    )

    pago = alt.Chart(datap).mark_bar().encode(
        x=alt.X('FECHA_VENCIMIENTO:T', title='Fecha de vencimiento'),
        y=alt.Y('MONTO ADEUDADO', title='Monto a pagar'),
        color=alt.value('red'),
        tooltip=['FECHA_VENCIMIENTO:T', 'MONTO ADEUDADO']
    )


    legend = alt.Chart(pd.DataFrame({'label': ['Proveedores', 'Saldos'], 'color': ['red', 'green']})).mark_text().encode(
        y=alt.Y('label:N', axis=None, title=None),
        color=alt.Color('color:N', scale=None),
        text='label:N'
    ).properties(height = 40, width = 100)

    combined_chart = (chart + pago)| legend

    combined_chart

# FLUJO
agree6 = st.button('Flujo de Efectivo')
if agree6:
    
    saldos['FECHA_VENCIMIENTO'] = pd.to_datetime(saldos['FECHA_VENCIMIENTO'])
    saldos['AÑO'] = saldos['FECHA_VENCIMIENTO'].dt.year
    saldos['MES'] = saldos['FECHA_VENCIMIENTO'].dt.month

    cpp['FECHA_VENCIMIENTO'] = pd.to_datetime(cpp['FECHA_VENCIMIENTO'])
    cpp['AÑO'] = cpp['FECHA_VENCIMIENTO'].dt.year
    cpp['MES'] = cpp['FECHA_VENCIMIENTO'].dt.month
    
    f = pd.DataFrame(fact.groupby(['AÑO','MES'])['CAN_TOT'].sum())
    g = pd.DataFrame(gastos.groupby(['AÑO','MES'])['TOTAL_SAT'].sum())
    n = pd.DataFrame(notas.groupby(['AÑO','MES'])['CAN_TOT'].sum())
    s = pd.DataFrame(saldos.groupby(['AÑO','MES'])['MONTO ADEUDADO'].sum())

    fg = pd.merge(f,g, on = ['AÑO','MES'], how = 'outer')
    ns = pd.merge(n,s, on = ['AÑO','MES'], how = 'outer')
    flujo = pd.merge(fg,ns, on = ['AÑO','MES'], how = 'outer')

    ## Gráfica
    # Convertir los datos en un formato adecuado para la visualización
    df_melted = flujo.melt(id_vars=['AÑO', 'MES'], var_name='Tipo', value_name='Monto')

    # Definir el orden deseado para los tipos
    orden_tipos = ['INGRESOS', 'EGRESOS', 'FLUJO']

    # Asignar un orden específico a los valores de la columna "Tipo"
    df_melted['Tipo'] = pd.Categorical(df_melted['Tipo'], categories=orden_tipos, ordered=True)

    # Ordenar el DataFrame por "Tipo" y luego por "MES"
    df_sorted = df_melted.sort_values(['Tipo', 'MES'])

    # Crear el control de selección de año
    year_selection = alt.binding_select(options=list(flujo['AÑO'].unique()), name='Año:')
    year_selector = alt.selection_single(fields=['AÑO'], bind=year_selection, init={'AÑO': flujo['AÑO'].max()})

    # Crear la gráfica principal
    main_chart = alt.Chart(df_sorted).mark_bar().encode(
        x=alt.X('MES:N', title='Mes'),
        y=alt.Y('Monto:Q', title='Monto'),
        color=alt.Color('Tipo:N', legend=alt.Legend(title='Tipo')),
        column=alt.Column('Tipo:N', title='Tipo'),
        tooltip=['AÑO:O', 'MES:O', 'Tipo:N', 'Monto:Q']
    ).transform_filter(
        year_selector
    ).add_selection(
        year_selector
    ).properties(
        width=200,
        height=400,
        title='Desglose de Ingresos, Egresos y Flujo por Mes'
    )

    # Mostrar la gráfica principal
    main_chart

    ## Flujo
    flujo
