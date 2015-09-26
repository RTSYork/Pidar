#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import sys
import signal
import math
from time import sleep
import rpyc
from lidar import Lidar


numberSamples = 16
first = 230
last = 640
positions  = [ 234,  240,  249,  265,  285,  324,  370,  405,  429,  452,  496,  505,  548,  581,  614,  623]
thresholds = [1802, 1687, 1521, 1240, 1030,  836,  775,  812,  965, 1106, 1433, 1565, 2114, 2043, 2043, 2145]
# thresholds = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]


clearString  = '\x1b[2J\x1b[H'
resetString  = '\x1b[4H'
topString    = '╔══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╗'
piString     = '║ pi16 │ pi15 │ pi14 │ pi13 │ pi12 │ pi11 │ pi10 │ pi09 │ pi08 │ pi07 │ pi06 │ pi05 │ pi04 │ pi03 │ pi02 │ pi01 ║'
distString   = '║ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} ║'
divString    = '╟┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄╢'
detString    = '║ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} ║'
bottomString = '╚══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╝'


if len(sys.argv) != 2:
	print 'Usage: pidar.py serialDevice'
	sys.exit(0)


def sigintHandler(signal, frame):
	print 'Exiting...'
	lid.laserOff()
	print 'Lidar laser is OFF!'
	lid.close()
	print 'Closed serial port ' + serialDevice
	sys.exit(0)

signal.signal(signal.SIGINT, sigintHandler)


piglows1 = []
piglows = []
for i in range(1, 17):
	ip = '192.168.50.' + str(i)
	print 'Connecting to', ip
	conn = rpyc.connect(ip, 18861)
	piglows1.append(conn)
	piglows.append(conn.root)

for piglow in piglows:
	piglow.init()
	piglow.all_off()


print clearString


serialDevice = sys.argv[1]
lid = Lidar(serialDevice)
print 'Opened Lidar on serial port', serialDevice

lid.laserOn()
print 'Lidar laser is ON!'

oldDistances = []
for i in range(0, numberSamples):
	oldDistances.append(4095)

while True:
	distances = []
	distances2 = []
	for _ in range(0, 20):
		distances2.append([])

	response = lid.acquire(first, last)

	for i in range(0, numberSamples):
		pos = positions[i]
		s = (pos - first) * 2
		val1 = Lidar.decode2(response[s:s+2])
		if val1 < 300:
			val1 = 4095
		val2 = Lidar.decode2(response[s+2:s+4])
		if val2 < 300:
			val2 = 4095
		val3 = Lidar.decode2(response[s+4:s+6])
		if val3 < 300:
			val3 = 4095
		value = (val1 + val2 + val3) / 3
		dist = (value + oldDistances[i]) / 2
		distances.append(dist)

		thresh = thresholds[i]
		redThresh = thresh + 1920
		orangeThresh = thresh + 1792
		yellowThresh = thresh + 1536
		greenThresh = thresh + 1280
		blueThresh = thresh + 1024
		whiteThresh = thresh + 512

		red = 127
		orange = 0
		yellow = 0
		green = 0
		blue = 0
		white = 0

		if (dist > 300):
			if (dist < redThresh):
				red = min(255, (redThresh - dist) + 127)
				if (dist < orangeThresh):
					orange = min(255, (orangeThresh - dist))
					if (dist < yellowThresh):
						yellow = min(255, (yellowThresh - dist))
						if (dist < greenThresh):
							green = min(255, (greenThresh - dist))
							if (dist < blueThresh):
								blue = min(170, (blueThresh - dist) / 3)
								if (dist < whiteThresh):
									white = min(127, (whiteThresh - dist) / 4)

		piglows[15-i].colours(red, orange, yellow, green, blue, white)

		for i in range(0, len(distances2)):
			base = (thresh - 100) + (i * 100)
			if (dist > base) and (dist <= base + 100):
				distances2[i].append('####')
			else:
				distances2[i].append('    ')

	print resetString
	print topString
	print piString
	print divString
	print distString.format(*distances)
	print divString
	for val in distances2:
		print detString.format(*val)
	print bottomString

	oldDistances = distances
	