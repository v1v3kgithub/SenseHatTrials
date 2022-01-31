
import dash
from collections import deque
from dash import dash_table
from dash import dcc
from dash.dependencies import Input, Output
from dash import html
from datetime import datetime as dt
import random
app = dash.Dash(__name__)


data_queue = deque(maxlen=20)

accel_data = {
  "ts": 1643129665.882071,
  "accel": {
    "roll": 0.6891072302335481,
    "pitch": 358.1343982881213,
    "yaw": 161.77001154813885
  },
  "accel_raw": {
    "x": 0.03418487310409546,
    "y": 0.009468910284340382,
    "z": 0.972594141960144
  }
}

app.layout = html.Div(
    html.Div([
        html.H4('Live Sensor Data'),
        html.Div(id='live-update-text'),
        dash_table.DataTable(
            id='sensor-data-table',
            columns=[
                {"name": ["Time", "",""], "id": "ts"},
                {"name": ["Data", "Humidity",""], "id": "humidity"},
                {"name": ["Data", "Temperature",""], "id": "temp"},
                {"name": ["Data", "Pressure",""], "id": "pressure"},
                {"name": ["Data", "North",""], "id": "north"},
                {"name": ["Accel","Degrees", "Roll"], "id": "accel_roll"},
                {"name": ["Accel","Degrees", "Pitch"], "id": "accel_pitch"},
                {"name": ["Accel","Degrees", "Yaw"], "id": "accel_yaw"},
                {"name": ["Accel","Raw", "X"], "id": "accel_x"},
                {"name": ["Accel","Raw", "Y"], "id": "accel_y"},
                {"name": ["Accel","Raw", "Z"], "id": "accel_z"},
                {"name": ["Gyro","Degrees", "Roll"], "id": "gyro_roll"},
                {"name": ["Gyro","Degrees", "Pitch"], "id": "gyro_pitch"},
                {"name": ["Gyro","Degrees", "Yaw"], "id": "gyro_yaw"},
                {"name": ["Gyro","Raw", "X"], "id": "gyro_x"},
                {"name": ["Gyro","Raw", "Y"], "id": "gyro_y"},
                {"name": ["Gyro","Raw", "Z"], "id": "gyro_z"},
            ],
            merge_duplicate_headers=True,
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'textAlign':'center',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
            data=[],
        ),
        dcc.Interval(
            id='interval-component',
            interval=1*2000, # in milliseconds
            n_intervals=0
        )
    ])
)
@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_header(n):
    style = {'padding': '5px', 'fontSize': '18px'}
    i = dt.utcnow()
    date_time = f"""{i:%Y-%m-%d %H:%M:%S}.{"{:03d}".format(i.microsecond // 1000)}"""
    return [
        html.Span('Last Update: ' + date_time, style=style)
    ]

@app.callback(Output('sensor-data-table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_header(n):
    return [
        {
            "ts": dt.fromtimestamp(dt.now().timestamp()).strftime("%d/%m/%Y, %H:%M:%S"),
            "humidity": random.randint(3,10),
            "temp": i * 10 * random.randint(3, 10),
            "pressure": random.randint(3,10)
        }
        for i in range(10)
    ]


if __name__ == '__main__':
    app.run_server(debug=True)