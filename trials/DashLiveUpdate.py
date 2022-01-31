import datetime

import dash
from dash import dcc
from dash import html
import plotly
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#https://dash.plotly.com/live-updates

# pip install pyorbital
from pyorbital.orbital import Orbital
satellite = Orbital('TERRA')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('TERRA Satellite Live Feed'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*5000, # in milliseconds
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    now = datetime.datetime.now()
    lon, lat, alt = satellite.get_lonlatalt(now)
    style = {'padding': '5px', 'fontSize': '16px'}
    i = datetime.datetime.utcnow()
    date_time = f"""{i:%Y-%m-%d %H:%M:%S}.{"{:03d}".format(i.microsecond // 1000)}"""
    return [
        html.Span('Longitude: {0:.2f}'.format(lon), style=style),
        html.Span('Latitude: {0:.2f}'.format(lat), style=style),
        html.Span('Altitude: {0:0.2f}'.format(alt), style=style),
        html.Span('Timestamp: ' + date_time, style=style)
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    satellite = Orbital('TERRA')
    data = {
        'time': [],
        'Latitude': [],
        'Longitude': [],
        'Altitude': []
    }

    # Collect some data
    for i in range(180):
        time = datetime.datetime.now() - datetime.timedelta(seconds=i*20)
        lon, lat, alt = satellite.get_lonlatalt(
            time
        )
        data['Longitude'].append(lon)
        data['Latitude'].append(lat)
        data['Altitude'].append(alt)
        data['time'].append(time)

    # Create the graph with subplots
    fig = make_subplots(rows=3, cols=1,
                                        row_heights=[0.3, 0.3,0.7],
                                        specs=[[{'is_3d': False}],
                                               [{'is_3d': False}],
                                               [{'is_3d': True}]],
                                        vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    time_alt = go.Scatter(name='Altitude',mode='lines+markers')

    fig.append_trace(time_alt,1,1)
    time_alt.x = [data['time'][-1]]
    time_alt.y = [data['Altitude'][-1]]
    # fig.append_trace({
    #     'x': data['time'],
    #     'y': data['Altitude'],
    #     'name': 'Altitude',
    #     'mode': 'lines+markers',
    #     'type': 'scatter'
    # }, 1, 1)
    fig.append_trace({
        'x': data['Longitude'],
        'y': data['Latitude'],
        'text': data['time'],
        'name': 'Longitude vs Latitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)
    fig.append_trace(
        go.Scatter3d(x=data['Longitude'],y=data['Latitude'],z=data['Altitude'])
        , 3, 1)
    fig.update_layout(width=700, height=800)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)