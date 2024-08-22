import socket

def get_port():
    ports = range(8050, 8550)
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port

port = get_port()
import os

import pandas as pd
df_median=pd.read_csv('Apartment_data_median.csv')
col_loc = df_median.city.to_list()
df_tmp = df_median.T
df_tmp.columns = col_loc
df_tmp = df_tmp.drop(index='city')
df_tmp.index.name = 'month'
df_tmp = df_tmp.reset_index()
df_median = df_tmp

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input, State, callback, dash_table
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import dash

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# [1] 전역변수
df = df_median
data_len = df.shape[0]
columns = df.columns[1:]
start = df['month'].min()
end = df['month'].max()
monthList = df.month.to_list()
fig = px.line(df, x='month', y='nationWide')


Div_tab2 = html.Div([
    dbc.Button("Download CSV", id="button",className='m-2 p-2'),
    dcc.Download(id="download"),
    dash_table.DataTable(id = 'dtable',
    data=df[['month','nationWide']].to_dict('records'), 
    page_size=12)
])
# [2] layout 설계
header = html.H1('Apartment Price Data (median price)', className='bg-warning text-center m-2 p-2')
left= dbc.Card([
    html.H3('Select City/Province',className='m-2 p-2'),
    dcc.Dropdown(columns,id='city',value=columns[0],placeholder='Select',multi=True,className='m-2 p-2'),
    html.H3('Select Period',className='m-2 p-2'),
    html.Div(id='rangeResult'),
    dcc.RangeSlider(0, data_len-1, 1,id = 'monthRange', value=[0,data_len-1],marks={0:monthList[0],data_len-1:monthList[data_len-1]}),
], className='m-2 p-2')
right= dbc.Card([
    dcc.Tabs(id='tabs', value='tab1', children=[
            dcc.Tab(id='tab1',children = dcc.Graph(figure=fig,id='line'), label='Line Chart', value='tab1'),
            dcc.Tab(id='tab2',children = dcc.Graph(figure=fig,id='bar'), label='Bar Chart', value='tab2'),
            dcc.Tab(id='tab3',children = Div_tab2, label='Table', value='tab3')
    ],className = 'm-2 p-2'),
    html.Div(id='result2')
],className='m-2 p-2')
# left, right 변수로 구성요소를 설계한다

app.layout = html.Div([
    header,
    dbc.Row([
        dbc.Col(left, width=3),
        dbc.Col(right, width=6)
    ], justify='center')
])

@callback(Output('rangeResult', 'children'),
          Input('monthRange','value'))
def func(monthRange): 
    if monthRange:
        return monthList[monthRange[0]]+" ~ "+monthList[monthRange[1]]
@callback(Output('line', 'figure'),Output('bar', 'figure'),Output('dtable', 'data'),
          Input('city','value'),
          Input('monthRange','value'))
def func(city,monthRange): 
    start = monthList[monthRange[0]]
    end = monthList[monthRange[1]]
    if city == []:
        return dash.no_update
    elif isinstance(city, list):
        df_tmp = df.query('month>=@start and month <= @end')
        df_ret = df_tmp[['month']]
        fig1 = go.Figure()
        fig2 = go.Figure()
        for idx, col in enumerate(city):
            fig1.add_trace(go.Scatter(x =df_tmp['month'], y =df_tmp[col], mode ='lines', name = col))
            fig2.add_trace(go.Bar(x =df_tmp['month'], y =df_tmp[col], name = col))
            df_ret=pd.concat([df_ret,df_tmp[[col]]],axis=1)
        fig1.update_layout(title='Median Price of Apartment in South Korea',
                   xaxis_title='Month',
                   yaxis_title='unit(10,000won/m2)')
        fig2.update_layout(title='Median Price of Apartment in South Korea',
                   barmode='stack',
                   xaxis_title='Month',
                   yaxis_title='unit(10,000won/m2)')
        return fig1, fig2, df_ret.to_dict('records')
    else:
        df_tmp = df.query('month>=@start and month <= @end')
        df_ret = df_tmp[['month',city]]
        fig1 = go.Figure()
        fig2 = go.Figure()
        fig1.add_trace(go.Scatter(x =df_tmp['month'], y =df_tmp[city], mode ='lines', name = city))
        fig2.add_trace(go.Bar(x =df_tmp['month'], y =df_tmp[city], name = city))
        fig1.update_layout(title='Median Price of Apartment in South Korea',
                   xaxis_title='Month',
                   yaxis_title='unit(10,000won/m2)')
        fig2.update_layout(title='Median Price of Apartment in South Korea',
                   barmode='stack',
                   xaxis_title='Month',
                   yaxis_title='unit(10,000won/m2)')
        return fig1, fig2, df_ret.to_dict('records')
        
@callback(Output("download", "data"),
         Input("button", "n_clicks"),
         State('dtable','data'),
         prevent_initial_call=True )
def func(button,dtable):
    if button:
        df_tmp = pd.DataFrame(dtable)
        return dcc.send_data_frame(df_tmp.to_csv, "mydata.csv") # csv 파일 다운

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port=port)