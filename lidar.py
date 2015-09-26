from serial import Serial

class Lidar():

	def __init__(self, serialDevice):
		self.ser = Serial(serialDevice, 115200, timeout=5)
		self.ser.flushInput()
		self.ser.flushOutput()

	@staticmethod
	def decode2(encoded):
		byte1 = ord(encoded[0]) - 0x30
		byte2 = ord(encoded[1]) - 0x30
		return (byte1 << 6) + byte2

	@staticmethod
	def decode3(encoded):
		byte1 = ord(encoded[0]) - 0x30
		byte2 = ord(encoded[1]) - 0x30
		byte3 = ord(encoded[2]) - 0x30
		return (byte1 << 12) + (byte2 << 6) + byte3

	def laserOn(self):
		self.ser.write("BM\n")
		self.ser.readline()
		self.ser.readline()
		self.ser.readline()

	def laserOff(self):
		self.ser.write("QT\n")
		self.ser.readline()
		self.ser.readline()

	def acquire(self, first, last):
		self.ser.write('GS{:0>4}{:0>4}00\n'.format(first, last))
		self.ser.readline()
		self.ser.readline()
		self.ser.readline()
		buf = ''
		while True:
			line = self.ser.readline()
			if len(line) == 1:
				break
			else:
				buf += line[0:-2]
		return buf

	def close(self):
		self.ser.flushInput()
		self.ser.flushOutput()
		self.ser.close()
