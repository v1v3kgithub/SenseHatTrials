from sense_hat import SenseHat
import json
from datetime import datetime as dt
import time
import argparse
import paho.mqtt.client as mqtt
import logging as l
import traceback

DEFAULT_MQTT_SERVER = "pi-fw.local"
READ_FREQUENCY_SEC = 0

SENSOR_TOPIC_BASE = "sense_hat/data"
SENSOR_TOPIC_BASIC_DATA = SENSOR_TOPIC_BASE + "/basic"
ACC_TOPIC = SENSOR_TOPIC_BASE + "/accel"
ACC_RAW_TOPIC = SENSOR_TOPIC_BASE + "/accel_raw"
GYRO_TOPIC = SENSOR_TOPIC_BASE + "/gyro"
GYRO_RAW_TOPIC = SENSOR_TOPIC_BASE + "/gyro_raw"
ORIENTATION_TOPIC = SENSOR_TOPIC_BASE + "/orientation"

SENSOR_BASIC = 'basic_sensor'
ACCEL = 'accel'
ACCEL_RAW = 'accel_raw'
GYRO = 'gyro'
GYRO_RAW = 'gyro_raw'
ORIENTATION = 'gyro_raw'

list_of_sensors = {SENSOR_BASIC, ACCEL, ACCEL_RAW, GYRO, GYRO_RAW, ORIENTATION}


def read_basic_sensor_data(sense):
    humidity = sense.get_humidity()
    temp = sense.get_temperature()
    temp_from_pressure = sense.get_temperature_from_pressure()
    pressure = sense.get_pressure()
    north = sense.get_compass()
    return {
        "humidity": humidity,
        "temperature_c": temp,
        "temperature_from_pressure": temp_from_pressure,
        "pressure_millibars": pressure,
        "compass_north": north
    }


def read_accel(sense):
    return sense.accel


def read_accel_raw(sense):
    return sense.accel_raw


def read_gyro(sense):
    return sense.gyroscope


def read_gyro_raw(sense):
    return sense.gyroscope_raw


def read_orientation(sense):
    return sense.get_orientation_degrees()


sensor_function_map = {
    SENSOR_BASIC: (read_basic_sensor_data, SENSOR_TOPIC_BASIC_DATA),
    ACCEL: (read_accel, ACC_TOPIC),
    ACCEL_RAW: (read_accel_raw, ACC_RAW_TOPIC),
    GYRO: (read_gyro, GYRO_TOPIC),
    GYRO_RAW: (read_gyro_raw, GYRO_RAW_TOPIC),
    ORIENTATION: (read_orientation, ORIENTATION_TOPIC)
}


def setup_sensehat():
    l.info("Setting up Sense Hat")
    sense = SenseHat()
    sense.set_imu_config(True, True, True)
    return sense


def setup_mqtt(server):
    # MQTT call backs
    def on_connect(client, userdata, flags, rc):
        l.info("MQTT Connected")

    def on_disconnect(client, userdata, rc):
        l.info("MQTT Disconnected")

    l.info("Setting up Connection to MQTT server %s " % server)
    mqtt_client = mqtt.Client()
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(server)
    return mqtt_client


def publish_data(topic, data):
    # l.info("Publishing data to " + topic)
    data["ts"] = dt.now().timestamp()
    mqtt_client.publish(topic, json.dumps(data), retain=True)


def log_sensor_readings(humidity, temp, temp_from_pressure, pressure, north, compass_raw,
                        orientation_deg, gyro, gyro_raw, accel, accel_raw):
    print("--------------------------------------------------------")
    print("Humidity: %s" % humidity)

    print("Temperature: %s C" % temp)
    print("Temperature from Pressure: %s C" % temp_from_pressure)
    print("Pressure: %s Millibars" % pressure)

    print("===== Compass ======")
    print("Compass (North): %s" % north)
    print("Compass Raw Magnetic Intensity in microteslas (µT):" + json.dumps(compass_raw))

    print("===== Orientation ======")
    print("Orientation Degrees:" + json.dumps(orientation_deg))

    print("===== Gyroscope ======")
    print("Gyroscope:" + json.dumps(gyro))
    print("Gyroscope Raw (Radians per second):" + json.dumps(gyro_raw))

    print("===== Accelerometer ======")
    print("Accelerometer:" + json.dumps(accel))
    print("Accelerometer Raw (Gs):" + json.dumps(accel_raw))


def read_sensor_data(sense):
    humidity = sense.get_humidity()
    temp = sense.get_temperature()
    temp_from_pressure = sense.get_temperature_from_pressure()
    pressure = sense.get_pressure()
    north = sense.get_compass()
    compass_raw = sense.get_compass_raw()
    orientation_deg = sense.get_orientation_degrees()
    gyro = sense.gyroscope
    gyro_raw = sense.gyroscope_raw
    accel = sense.accel
    accel_raw = sense.accel_raw
    return [humidity, temp, temp_from_pressure, pressure, north, compass_raw, orientation_deg, gyro, gyro_raw, accel,
            accel_raw]


def format_and_publish_data(mqtt_client, humidity, temp, temp_from_pressure, pressure, north, compass_raw,
                            orientation_deg,
                            gyro, gyro_raw, accel, accel_raw):
    now = dt.now().timestamp()
    sensor_data = {
        "ts": now,
        "humidity": humidity,
        "temperature_c": temp,
        "temperature_from_pressure": temp_from_pressure,
        "pressure_millibars": pressure,
        "compass_north": north
    }

    accel_data = {
        "ts": now,
        "accel": accel,
        "accel_raw": accel_raw
    }
    gyro_data = {
        "ts": now,
        "gyro": gyro,
        "gyro_raw": gyro_raw
    }
    orientation_data = {
        "ts": now,
        "orientation_degrees": orientation_deg
    }
    publish_data(SENSOR_TOPIC, sensor_data)
    publish_data(ACC_TOPIC, accel_data)
    publish_data(GYRO_TOPIC, gyro_data)
    publish_data(ORIENTATION_TOPIC, orientation_data)


if __name__ == '__main__':
    # Logging formatter
    l.basicConfig(
        format='%(asctime)s %(levelname)-4s %(message)s',
        level=l.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(description="Optionally specify the MQTT server and update frequency")
    parser.add_argument("-m", "--mqtt_server", help="MQTT Server location", default=DEFAULT_MQTT_SERVER)
    parser.add_argument("-f", "--update_freq_secs", type=int, help="Update frequency in Seconds",
                        default=READ_FREQUENCY_SEC)
    parser.add_argument("-s", "--sensors_to_read", nargs='+', type=str,
                        help="List of Sensors to read " + str(list_of_sensors),
                        default=list_of_sensors)
    args = parser.parse_args()

    invalid_sensors_provided = set(args.sensors_to_read).difference(list_of_sensors)
    if bool(invalid_sensors_provided):
        l.error("Ignoring Invalid Sensors " + str(invalid_sensors_provided))

    l.info("Reading sensors " + str(list_of_sensors))
    sense = setup_sensehat()
    try:
        mqtt_client = setup_mqtt(args.mqtt_server)
        l.info("Starting the loop every %d sec to capture and publish sensor data " % args.update_freq_secs)
        while (True):  # Main loop
            for s in list_of_sensors:
                sensor_function_and_topic = sensor_function_map.get(s)
                readings = sensor_function_and_topic[0](sense)
                publish_data(sensor_function_and_topic[1], readings)

            time.sleep(args.update_freq_secs)

    except Exception as e:
        traceback.print_exc()
        l.error("Error connecting to MQTT Server " + args.mqtt_server + " exiting")

    sensors_to_read = list_of_sensors.difference(args.sensors_to_read)
    if bool(sensors_to_read):
        None
    else:
        l.error("No valid sensors provided " + str(args.sensors_to_read))