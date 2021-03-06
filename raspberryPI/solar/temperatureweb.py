#!/usr/bin/env python

import os
import time
import socket

import Utils

HOSTNAME = socket.gethostname()
WIDTH = 400
HEIGHT = 200

DIR = "/mnt/ramdisk/"
OUTDIR = '/mnt/ramdisk/'
LOG_TEMPERATURE = "/mnt/ramdisk/temperature.log"
LOG_WEATHER = "/mnt/ramdisk/weather.log"

# define the desired colors for the graphs
COLLECTIONS = {
    'top-pi':
    {'Attic': ('#FF0000', 57, 'Attic'),
     'AiringCabinet': ('#EA8C09', 57, 'AiringCabinet'),
     'KeevaCupBoard': ('#176C01', 57, 'KeevaCupBoard'),
     'KeevaRoomBack': ('#24AC02', 57, 'KeevaRoomBack'),
     'KeevaRoomTop': ('#31EA03', 57, 'KeevaRoomTop'),
     'NiamhRoomBack': ('#1647EA', 57, 'NiamhRoomBack'),
     'NiamhRoomTop': ('#17A8EA', 57, 'NiamhRoomTop'),
     'LandingTop': ('#10A8E0', 57, 'LandingTop'),
     'HotWater': ('#FF0000', 57, 'HotWater'),
     'BoilerWater': ('#CC0000', 57, 'BoilerWater'),
     },
    'mid-pi':
    {'LivingRoomWindow': ('#FF0000', 55, 'LivingRoomWindow'),
     'LivingRoomCupBoard': ('#990000', 55, 'LivingRoomCupBoard'),
     'LandingMiddle': ('#00AA00', 55, 'LandingMiddle'),
     'LandingBottom': ('#008800', 55, 'LandingBottom'),
     },
    'bottom-pi':
    {'HallwayTop': ('#FF0000', 55, 'HallwayTop'),
     'HallwayBottom': ('#990000', 55, 'HallwayBottom'),
     'BackRoomBack': ('#00AA00', 55, 'BackRoomBack'),
     'BackRoomFront': ('#008800', 55, 'BackRoomFront'),
     },
}

definition = 'DEF:%(key)s=%(DIR)s/temperature.rrd:%(key)s:AVERAGE'
line = 'LINE1:%(key)s%(color)s:"%(description)s [deg C]"'
statements = {'hourly':
              'rrdtool graph %(OUTDIR)s/temperature_%(period)s.png '
              '--width %(WIDTH)i --height %(HEIGHT)i --start -4h',
              'daily':
              'rrdtool graph %(OUTDIR)s/temperature_%(period)s.png  '
              '--width %(WIDTH)i --height %(HEIGHT)i --start -1d',
              'weekly':
              'rrdtool graph %(OUTDIR)s/temperature_%(period)s.png '
              '--width %(WIDTH)i --height %(HEIGHT)i --start -7d', }

for period, statement_prefix in statements.items():
    section = HOSTNAME
    colors = COLLECTIONS[section]

    lines = []
    lines.append(statement_prefix % locals())

    for key, data in colors.items():
        color, networkid, location = data
        description = key

        lines.append(definition % locals())
        lines.append(line % locals())

    # add weather:
    if section == "top-pi":
        lines.append(
            'DEF:outside=%(DIR)s/weather.rrd:temperature:AVERAGE' % locals())
        lines.append('LINE1:outside#0000FF:"Outside"')

    lines.append("> %(OUTDIR)s/dashboard.log" % locals())
    statement = ' '.join(lines)
    os.system(statement)


status = Utils.getStatusFromLog(LOG_TEMPERATURE)

if HOSTNAME == "top-pi":
    status.extend(
        Utils.getStatusFromLog(LOG_WEATHER))

status_string = Utils.statusToHTML(status)
datestring = time.asctime(time.localtime(time.time()))

print "Content-Type: text/html"
print
print '''\
<html>
<body>
<h1>8A Harley Road Dashboard - %(HOSTNAME)s</h1>
%(datestring)s
<p>%(status_string)s</p>
<form><button>Refresh</button></form>
<table>
<tr><th>Hourly</th></tr>
<tr><td><img border="0" title="hourly" alt="hourly" src="../images/temperature_hourly.png"></td></tr>
<tr><th>Daily</th></tr>
<tr><td><img border="0" title="daily" alt="daily" src="../images/temperature_daily.png"></td></tr>
<tr><th>Weekly</th></tr>
<tr><td><img border="0" title="weekly" alt="weekly" src="../images/temperature_weekly.png"></td></tr>
</table>
</body>
</html>
''' % locals()
