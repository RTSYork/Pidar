# Based on https://github.com/Boeeerb/PiGlow

from smbus import SMBus
import RPi.GPIO as rpi
import rpyc

class PiGlowService(rpyc.Service):

	def on_connect(self):
		pass

	def on_disconnect(self):
		pass

	def exposed_init(self):
		self.bus = SMBus(1)
		self.bus.write_byte_data(0x54, 0x00, 0x01)
		self.bus.write_byte_data(0x54, 0x13, 0xFF)
		self.bus.write_byte_data(0x54, 0x14, 0xFF)
		self.bus.write_byte_data(0x54, 0x15, 0xFF)

	def exposed_colours(self, red, orange, yellow, green, blue, white):
		try:
			self.bus.write_i2c_block_data(0x54, 0x01, [red, orange, yellow, green, blue, green, red, orange, yellow, white, white, blue, white, green, blue, yellow, orange, red])
			self.bus.write_byte_data(0x54, 0x16, 0xFF)
		except IOError:
			pass

	def exposed_all_off(self):
		try:
			self.bus.write_i2c_block_data(0x54, 0x01, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
			self.bus.write_byte_data(0x54, 0x16, 0xFF)
		except IOError:
			pass
