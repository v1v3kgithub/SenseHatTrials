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
sensor_data_reader = sensor_data_mqtt_reader.SensorDataReader()

table_data_style = {
    'backgroundColor': 'rgb(50, 50, 50)',
    'color': 'white'
}
table_header_style = {
    'backgroundColor': 'rgb(30, 30, 30)',
    'textAlign': 'center',
    'color': 'white'
}
default_fig = go.Figure(plotly.graph_objs.Scatter3d())


app.layout = html.Div(
    html.Div([
        html.H4('Live Sensor Data'),
        html.Div(id='live-update-text'),
        html.H5('Accelorometer Data'),

        dcc.Graph(id='live-accel-graph', animate=False, figure=default_fig),
        dash_table.DataTable(
            id='sensor-accel-data-table',
            columns=[
                {"name": ["Time", "", ""], "id": "ts"},
                {"name": ["Accel", "Degrees", "Roll"], "id": "accel_roll"},
                {"name": ["Accel", "Degrees", "Pitch"], "id": "accel_pitch"},
                {"name": ["Accel", "Degrees", "Yaw"], "id": "accel_yaw"},
                {"name": ["Accel", "Raw", "X"], "id": "accel_x"},
                {"name": ["Accel", "Raw", "Y"], "id": "accel_y"},
                {"name": ["Accel", "Raw", "Z"], "id": "accel_z"},
            ],
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            merge_duplicate_headers=True,
            style_header=table_header_style,
            style_data=table_data_style,
            data=[],
        ),
        html.H5('Gyroscope Data'),
        dash_table.DataTable(
            id='sensor-gyro-data-table',
            columns=[
                {"name": ["Time", "", ""], "id": "ts"},
                {"name": ["Gyro", "Degrees", "Roll"], "id": "gyro_roll"},
                {"name": ["Gyro", "Degrees", "Pitch"], "id": "gyro_pitch"},
                {"name": ["Gyro", "Degrees", "Yaw"], "id": "gyro_yaw"},
                {"name": ["Gyro", "Raw", "X"], "id": "gyro_x"},
                {"name": ["Gyro", "Raw", "Y"], "id": "gyro_y"},
                {"name": ["Gyro", "Raw", "Z"], "id": "gyro_z"},
            ],
            merge_duplicate_headers=True,
            style_header=table_header_style,
            style_data=table_data_style,
            data=[],
        ),
        html.H5('Orientation Data'),
        dash_table.DataTable(
            id='sensor-orientation-data-table',
            columns=[
                {"name": "Time", "id": "ts"},
                {"name": "Roll", "id": "orientation_roll"},
                {"name": "Pitch", "id": "orientation_pitch"},
                {"name": "Yaw", "id": "orientation_yaw"},
            ],
            merge_duplicate_headers=True,
            style_header=table_header_style,
            style_data=table_data_style,
            data=[],
        ),
        dcc.Interval(
            id='interval-component',
            interval=1 * 2000,  # in milliseconds
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-accel-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_accel_raw(n):
    accel_data = sensor_data_reader.accel_data_q[-1]
    data_3d = plotly.graph_objs.Scatter3d(
        x=[point["accel_yaw"] for point in sensor_data_reader.accel_data_q],
        y=[point["accel_roll"] for point in sensor_data_reader.accel_data_q],
        z=[point["accel_pitch"] for point in sensor_data_reader.accel_data_q],
        mode='markers+lines',
        marker_size=3
    )
    figure = go.Figure(data=data_3d, layout={'uirevision': 'button'})
    figure.update_layout( title="Acc changes", width=1000, height=700,scene_aspectmode='cube',
                               scene=dict(
                                   xaxis=dict(nticks=8, range=[0, 360], ),
                                   yaxis=dict(nticks=8, range=[0, 360], ),
                                   zaxis=dict(nticks=8, range=[0, 360], ), ),
                               )
    return figure

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_header(n):
    style = {'padding': '5px', 'fontSize': '14px'}
    i = dt.utcnow()
    date_time = f"""{i:%Y-%m-%d %H:%M:%S}.{"{:03d}".format(i.microsecond // 1000)}"""
    latest_data = sensor_data_reader.simple_data_q[-1]
    return [
        html.Span(date_time + " Humidity : {:.2f} Temp(C) : {:.2f} Pressure(millibar) {:.3f}".format(latest_data["humidity"],latest_data["temperature_c"],latest_data["pressure_millibars"]) , style=style),
    ]


@app.callback([
                Output('sensor-accel-data-table', 'data'),
                Output('sensor-gyro-data-table', 'data'),
                Output('sensor-orientation-data-table', 'data')],
              Input('interval-component', 'n_intervals'))
def update_sensor_simple_data(n):
    return [list(sensor_data_reader.accel_data_q),list(sensor_data_reader.gyro_data_q),list(sensor_data_reader.ori_data_q)]





if __name__ == '__main__':
    sensor_data_reader.init_and_start_mqtt()
    app.run_server(debug=True)
