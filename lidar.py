#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import sys
import signal
import serial
import math
from time import sleep
import rpyc


numberSamples = 16
resolution = 26
# centre = 384
centre = 400

thresholds = [2000, 1800, 1600, 1400, 1300, 1100, 900, 800, 1000, 1300, 1500, 1700, 1900, 1900, 1900, 1900]
# thresholds = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]


clearString  = '\x1b[2J\x1b[H'
resetString  = '\x1b[4H'
topString    = '╔══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╤══════╗'
piString     = '║ pi16 │ pi15 │ pi14 │ pi13 │ pi12 │ pi11 │ pi10 │ pi09 │ pi08 │ pi07 │ pi06 │ pi05 │ pi04 │ pi03 │ pi02 │ pi01 ║'
distString   = '║ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} │ {:>4} ║'
divString    = '╟┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄┼┄┄┄┄┄┄╢'
detString    = '║ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} │ {} ║'
bottomString = '╚══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╧══════╝'


def decode2(encoded):
	byte1 = ord(encoded[0]) - 0x30
	byte2 = ord(encoded[1]) - 0x30
	return (byte1 << 6) + byte2

def decode3(encoded):
	byte1 = ord(encoded[0]) - 0x30
	byte2 = ord(encoded[1]) - 0x30
	byte3 = ord(encoded[2]) - 0x30
	return (byte1 << 12) + (byte2 << 6) + byte3

def laserOn():
	ser.write("BM\n")
	return ser.read(8)

def laserOff():
	ser.write("QT\n")
	return ser.read(8)

def acquire(step):
	ser.write('GD{:0>4}{:0>4}00\n'.format(step, step))
	return ser.read(29)

def acquireAll(first, last, cluster):
	ser.write('GS{:0>4}{:0>4}{:0>2}\n'.format(first, last, cluster))
	return ser.read(58)

def sigintHandler(signal, frame):
	print 'Exiting...'
	laserOff()
	print 'Lidar laser is OFF!'
	ser.close()
	print 'Closed serial port ' + ser.name
	sys.exit(0)


if len(sys.argv) != 2:
	print 'Usage: lidar.py serialDevice'
	exit()

signal.signal(signal.SIGINT, sigintHandler)


positions = []
start = centre - ((numberSamples - 1) * (resolution / 2))
end = start + (resolution * (numberSamples - 1))
for pos in range(0, numberSamples):
	positions.append(start + (resolution * pos))


# piglows1 = []
# piglows = []
# for i in range(1, 17):
# 	ip = '192.168.50.' + str(i)
# 	print 'Connecting to', ip
# 	conn = rpyc.connect(ip, 18861)
# 	piglows1.append(conn)
# 	piglows.append(conn.root)

# for piglow in piglows:
# 	piglow.init()
# 	piglow.all_off()

print clearString

serialDevice = sys.argv[1]
ser = serial.Serial(serialDevice, 115200, timeout=5)
ser.flushInput()
ser.flushOutput()
print 'Opened serial port ' + ser.name

laserOn()
print 'Lidar laser is ON!'

while True:
	distances = []
	distances2 = []
	for _ in range(0, 20):
		distances2.append([])

	response = acquireAll(start, end, resolution)
	for i in range(0, numberSamples):
		s = 23 + (i * 2)
		value = decode2(response[s:s+2])
		distances.append(value)

	for i in range(0, numberSamples):
		dist = distances[i]
		thresh = thresholds[i]
		redThresh = thresh + 1408
		orangeThresh = thresh + 1280
		yellowThresh = thresh + 1024
		greenThresh = thresh + 768
		blueThresh = thresh + 512
		whiteThresh = thresh + 256

		red = 127
		orange = 0
		yellow = 0
		green = 0
		blue = 0
		white = 0

		if (dist > 100):
			if (dist < redThresh):
				red = min(255, (redThresh - dist) + 127)
				if (dist < orangeThresh):
					orange = min(255, (orangeThresh - dist))
					if (dist < yellowThresh):
						yellow = min(255, (yellowThresh - dist))
						if (dist < greenThresh):
							green = min(255, (greenThresh - dist))
							if (dist < blueThresh):
								blue = min(255, (blueThresh - dist))
								if (dist < whiteThresh):
									white = min(255, (whiteThresh - dist))

		piglows[15-i].colours(red, orange, yellow, green, blue, white)

		for i in range(0, len(distances2)):
			base = thresh + (i * 100) - 30
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

	#sleep(2)


laserOff()
print 'Lidar laser is OFF!'

ser.close()
print 'Closed serial port ' + ser.name
