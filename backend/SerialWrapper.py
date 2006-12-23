#!/usr/bin/env python
import serial
import time

class Port:
	def __init__(self, portNumber):
		# Open the serial port
		self.ser = serial.Serial(
			port=portNumber,
			baudrate=38400,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=1
		)

		# Make sure that it has a second to actually open!
		time.sleep(0.1)

	def command(self, command):
		time.sleep(0.002)
		sent = '~11h ' + command + '\r\n'
		self.ser.write(sent)
		received = self.ser.readline()
		return received

	def close(self):
		self.ser.close()
