import dash


from dash import dash_table
from dash import dcc
from dash.dependencies import Input, Output
from dash import html
from datetime import datetime as dt
import plotly
import plotly.graph_objs as go
import sensor_data_mqtt_reader

app = dash.Dash(__name__, title="Live Sensor Updates")
sensor_data_reader = sensor_data_mqtt_reader.SensorDataReader(queue_len=50)


app.layout = html.Div(
    html.Div([
        html.H4('Plotted Sensor Data'),
        html.Div(id='live-update-text'),
        html.H5('Orientation Data'),


        dcc.Graph(id='live-gyro-yaw-graph', animate=False),
        dcc.Graph(id='live-gyro-roll-graph', animate=False),
        dcc.Graph(id='live-gyro-pitch-graph', animate=False),
        dcc.Graph(id='live-gyro-graph', animate=False),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        )
    ])
)
@app.callback([
    Output('live-gyro-yaw-graph','figure'),
    Output('live-gyro-roll-graph','figure'),
    Output('live-gyro-pitch-graph','figure'),
               ],
    Input('interval-component', 'n_intervals')
)
def update_gyro_graphs(n):
    yaw = go.Scatter(
        y=[point["yaw"] for point in sensor_data_reader.gyro_data_q],
        x=[point["ts"] for point in sensor_data_reader.gyro_data_q],
        name='Scatter',
        mode='lines+markers'
    )
    figure = go.Figure(layout={'uirevision': 'button'})
    figure.add_trace(go.Scatter(
        y=[point["yaw"] for point in sensor_data_reader.gyro_data_q],
        x=[point["ts"] for point in sensor_data_reader.gyro_data_q],
        name='Yaw',
        mode='lines+markers'
    ))
    figure.add_trace(go.Scatter(
        y=[point["roll"] for point in sensor_data_reader.gyro_data_q],
        x=[point["ts"] for point in sensor_data_reader.gyro_data_q],
        name='Roll',
        mode='lines+markers'
    ))
    figure.add_trace(go.Scatter(
        y=[point["pitch"] for point in sensor_data_reader.gyro_data_q],
        x=[point["ts"] for point in sensor_data_reader.gyro_data_q],
        name='Pitch',
        mode='lines+markers'
    ))
    figure.update_layout(title="Gyro"
                         )
    figure.update_yaxes(range=[0, 370])
    return [figure, None,None]

@app.callback([
                Output('live-gyro-graph', 'figure'),
                Output('live-update-text', 'children')
                ],
              Input('interval-component', 'n_intervals'))
def update_sensor_simple_data(n):
    roll = go.Scatterpolar(
        r=[point["pitch"] for point in sensor_data_reader.gyro_data_q],
        theta=[point["roll"] for point in sensor_data_reader.gyro_data_q],
        mode='markers',
        #marker = dict(size=[point["yaw"] for point in sensor_data_reader.gyro_data_q],)
    )
    figure = go.Figure(data=roll, layout={'uirevision': 'button'})
    figure.update_layout(
        title='R = Pitch, Theta = Roll',
        polar=dict(
            radialaxis=dict(range=[0, 370]),
        ),
        width=500, height=500
    )
    latest_data = sensor_data_reader.gyro_data_q[-1]
    style = {'padding': '5px', 'fontSize': '14px'}
    return [figure,
            [
                html.Span("Pitch : {:.2f} Yaw : {:.2f} Roll {:.3f}".format(
                    latest_data["pitch"], latest_data["yaw"], latest_data["roll"]),
                          style=style),
            ]
            ]

if __name__ == '__main__':
    sensor_data_reader.init_and_start_mqtt()
    app.run_server(debug=True)