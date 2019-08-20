# Overview
 
This is a daemon that will listen on a port for connections from a Ginlong Solar Inverter. Currently tested with a Solis 4G Mini Single Phase Inverter (Solis-mini-1500-4G)

The code was directly copied from dpoulson from https://github.com/dpoulson/ginlong-mqtt 
Many thanks for your work!
And as well to ashleysommer for his view on the decoding. https://gist.github.com/ashleysommer/2e11f232abc5509243ea408d5a33dbc0

# Details
The Solis solar inverters come with the option for wired or wireless monitoring 'sticks'. These are designed to talk to their own portal at http://www.ginlongmonitoring.com/ where
the stats will gather. This software allows you to run your own gatherer on a server and push these stats into an InfluxDB. 

You will need a system running python with the following modules:
* InfluxDBClient
* socket
* binascii
* time
* sys

You will also need a running InfluxDB server.


# Setup

## Logging
In `config.ini` you can set the location of the `raw.log` file. Note that the script does not create the directory if it doesn't exist.
Personally I use this script on a Raspberry Pi and have set up the logging directory to be a tmpfs and thus need `/etc/tmpfiles.d/ginlong.conf` with `D /var/log/ginlong 0755 root root`

## Daemon
1. You can run this python script as daemon by placing the file `ginlong-listen.service` in `/etc/systemd/system/ginlong-listen.service`
2. You should enable the service: `sudo systemctl ginlong-listen.service enable` (you can reboot to check if it works)
3. You can start the service: `sudo systemctl ginlong-listen.service start`

## Data collection
1. Log into the WiFi stick, and configure the second IP (Server B) option to point to the server that this daemon is running on. (Daemon defaults to port 9999). I'm not sure, but maybe it's worth noting the stick is configured for 'data-collection' (other option for me is transparency).
2. You can check if data is coming in by examining the raw log, which is by config-ini-default in `/var/log/ginlong/raw.log`. Note that the WiFi stick sends data roughly every 6 minutes (in my case) if there is enough solar power to keep the inverter on for long enough.
3. These items should now be(/become) accessible in your database. If you have grafana set up, you should also be able to start producing graphs


## Known issues
Occasionally I have to restart the service, the inverter still says the server is pingable, no error is reported but data is not passed to Influx. I setup some checking to see when I have to restart it (taking into account the hours that the sun is shining etc ;-) )

# More protocols
I had the idea to make the script such that other people could write a protocol-config file and select that through the config.ini. 
However, I only have one invertor so can't really help on that. I'm happy to help out in case someone wants so.
