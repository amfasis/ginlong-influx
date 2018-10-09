#!/usr/bin/python3 -O

import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient


config = configparser.RawConfigParser(allow_no_value=True)
config.read("config.ini")


###########################
# Variables

# What address to listen to (0.0.0.0 means it will listen on all addresses)
listen_address = config.get('DEFAULT', 'listen_address')
listen_port = int(config.get('DEFAULT', 'listen_port'))

log_path = config.get('Logging', 'log_path', fallback='/var/log/ginlong/')
do_raw_log = config.getboolean('Logging', 'do_raw_log')

influx_server = config.get('InfluxDB', 'influx_server')
influx_port = int(config.get('InfluxDB', 'influx_port'))
influx_database = config.get('InfluxDB', 'database')
influx_measurement = config.get('InfluxDB', 'measurement')

if __debug__:
    print("running with debug")
    print(listen_address)
    print(listen_port)
    print(influx_server)
    print(influx_port)
    print(influx_database)
    print(influx_measurement)
    print(log_path)
    print(do_raw_log)
else:
    print("running without debug")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((listen_address, listen_port))
sock.listen(1)

while True:
    # Wait for a connection
    if __debug__:
        print('waiting for a connection')
    conn, addr = sock.accept()
    try:
        print('connection from', addr)

        # Read in a chunk of data
        rawdata = conn.recv(1000)
        # Convert to hex for easier processing
        hexdata = binascii.hexlify(rawdata)

        timestamp = (time.strftime("%F %H:%M"))		# get date time

        if __debug__:
            print('Time: %s' % timestamp)
            print('Length: %s' % len(hexdata))
            print('Hex data: %s' % hexdata.decode())

        if do_raw_log:
            logfile = open(os.path.join(log_path, 'raw.log'), 'a')
            logfile.write(timestamp + ' ' + hexdata.decode() + '\n')
            logfile.close()

        if len(hexdata) >= 270:
            values = dict()
            print(str(hexdata[30:60]))
            # Serial number is used as InfluxDB tag,
            # allowing multiple inverters to connect to a single instance
            serial = binascii.unhexlify(hexdata[30:60])

            values['temp'] = float(int(hexdata[62:66], 16))/10
            values['vpv1'] = float(int(hexdata[66:70], 16))/10
            values['vpv2'] = float(int(hexdata[70:74], 16))/10
            values['vpv3'] = float(int(hexdata[74:78], 16))/10
            values['ipv1'] = float(int(hexdata[78:82], 16))/10
            values['ipv2'] = float(int(hexdata[82:86], 16))/10
            values['ipv3'] = float(int(hexdata[86:90], 16))/10
            values['iac1'] = float(int(hexdata[90:94], 16))/10
            values['iac2'] = float(int(hexdata[94:98], 16))/10
            values['iac3'] = float(int(hexdata[98:102], 16))/10
            values['vac1'] = float(int(hexdata[102:106], 16))/10
            values['vac2'] = float(int(hexdata[106:110], 16))/10
            values['vac3'] = float(int(hexdata[110:114], 16))/10
            values['fac'] = float(int(hexdata[114:118], 16))/100
            values['pac1'] = float(int(hexdata[118:122], 16))
            values['pac2'] = float(int(hexdata[122:126], 16))
            values['pac3'] = float(int(hexdata[126:130], 16))
            #unknown = float(int(hexdata[130:134],16))/100
            values['kwhtoday'] = float(int(hexdata[138:142], 16))/100
            values['kwhyesterday'] = float(int(hexdata[134:138], 16))/100
            values['kwhtotal'] = float(int(hexdata[142:150], 16))/10

            print(values)

            json_body = {'points': [{'tags': {'serial': serial.decode()},
                                     'fields': {k: v for k, v in values.items()}
                                     }],
                         'measurement': influx_measurement
                         }

            client = InfluxDBClient(host=influx_server,
                                    port=influx_port)
            success = client.write(json_body,
                                   # params isneeded, otherwise error 'database is required' happens
                                   params={'db': influx_database})  

            if not success:
                print('error writing to database')

    except Exception as e:
        print(e)
        print("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        if __debug__:
            print("Finally")
