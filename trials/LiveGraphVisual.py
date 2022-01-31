import datetime

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import datetime

d = deque(maxlen=20)
now = datetime.datetime.now()
d.append((0,0,0,now))


default_fig = go.Figure(plotly.graph_objs.Scatter3d())

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.Button('Reset View',id="reset-button"),
        dcc.Graph(id='live-graph', animate=False,figure=default_fig),
        dcc.Graph(id='line-graph', animate=False),
        dcc.Interval(
            id='interval-component',
            interval=1 * 2000,  # in milliseconds
            n_intervals=5
        )
    ]
)

@app.callback([Output('live-graph', 'figure'),
            Output('line-graph', 'figure')],
                Input('reset-button', 'value'),
              Input('interval-component', 'n_intervals')
              )
def update_graph_scatter(button,n):
    #print(n)

    #d.append((0,0,0))
    d.append((random.uniform(-0.1,0.1),random.uniform(-0.1,0.1),random.uniform(-0.1,0.1),datetime.datetime.now()))

    x_data = [point[0] for point in d]
    data_3d = plotly.graph_objs.Scatter3d(
        x=x_data,
        y=[point[1] for point in d],
        z=[point[2] for point in d],
        mode='markers+lines',
        marker_size=3,
    )

    figure = go.Figure(data=data_3d, layout={'uirevision': 'button'})
    figure.update_layout(template="plotly_dark", title="Acc changes", width=1000,height=700)
    x_data = plotly.graph_objs.Scatter(x=[point[3] for point in d], y=x_data, name='Scatter',
                                        mode='lines+markers')
    line_fig = go.Figure(x_data, layout={'uirevision': 'button','title':'Changes in X'})
    return [figure,line_fig]



if __name__ == '__main__':
    app.run_server(debug=True)