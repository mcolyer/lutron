#!/usr/bin/env python
from SerialWrapper import Port
import re
import string
import datetime

class Lutron:
	def __init__(self):
		self.port = Port(0)

	def areaStatus(self, area):
		"""Queries the system for an area status and returns a list."""
		areaHex = hex(area)[2:]
		resp = StatusResponse(self.port.command("801 " + areaHex))
		scene = string.atoi(resp.results[1], 16)
		sequence = string.atoi(resp.results[2], 16)
		return (scene, sequence)

	def timeClockStatus(self, clock):
		"""Queries the system for a timeclock status and returns a tuple.  The tuple is
		(Current Schedule, Next Event Type, Next Event Time, Next Script)"""

		clockHex = hex(clock)[2:]
		resp = StatusResponse(self.port.command("802 " + clockHex))

		schedule = string.atoi(resp.results[1], 16)
		nextType = resp.results[2]

		minsSinceMidnight = string.atoi(resp.results[3], 16)
		nextTime = datetime.time(minsSinceMidnight/60, minsSinceMidnight%60)

		nextScript = string.atoi(resp.results[4], 16)

		return (schedule, nextType, nextTime, nextScript)

	def wallStationStatus(self, link, station):
		"""Queries the system for a switch status given a link and station number and returns an integer."""
		stationHex = hex(0x100 * link + station)[2:]
		resp = StatusResponse(self.port.command("803 " + stationHex))
		
		status = []
		for val in resp.results[1:]:
			status.append( string.atoi(val, 16) )
		return status

	def switchStatus(self, link, station, switch):
		"""Queries the system for a switch status given a link and station number and returns an integer."""
		stationHex = hex(0x100 * link + station)[2:]
		switchHex = hex(switch)[2:]
		resp = StatusResponse(self.port.command("804 " + stationHex + " " + switchHex))
		status = string.atoi(resp.results[1], 16)
		return status

	def zoneIntensity(self, zone):
		"""Queries the system for a zone intensity and returns an integer."""
		zoneHex = hex(zone)[2:]
		resp = StatusResponse(self.port.command("805 " + zoneHex))
		intense = string.atoi(resp.results[0], 16)
		return intense

	def timeNow(self):
		"""Queries the system for the time and returns a time object."""
		resp = StatusResponse(self.port.command("808"))
		minsSinceMidnight = string.atoi(resp.results[0], 16)
		now = datetime.time(minsSinceMidnight/60,minsSinceMidnight%60)
		return now

	def astroTimes(self):
		"""Queries the system for the sunrise / set times and returns a tuple of times."""
		resp = StatusResponse(self.port.command("809"))
		sunriseMinsSinceMidnight = string.atoi(resp.results[0], 16)
		sunsetMinsSinceMidnight = string.atoi(resp.results[1], 16)
		sunrise = datetime.time(sunriseMinsSinceMidnight/60,sunriseMinsSinceMidnight%60)
		sunset = datetime.time(sunsetMinsSinceMidnight/60,sunsetMinsSinceMidnight%60)
		return (sunrise, sunset)

	def date(self):
		"""Queries the system for the date and returns a date object."""
		resp = StatusResponse(self.port.command("80A"))

		year = string.atoi(resp.results[2], 16) + 2000
		month = string.atoi(resp.results[0], 16)
		day = string.atoi(resp.results[1], 16)

		now = datetime.date(year, month, day)
		return now

	def codeRevLevel(self):
		"""Queries the system for the code rev level and returns an integer."""
		resp = StatusResponse(self.port.command("811"))
		rev = string.atoi(resp.results[0], 16)
		return rev

	def bootCodeRevLevel(self):
		"""Queries the system for the boot code rev level and returns an integer."""
		resp = StatusResponse(self.port.command("812"))
		rev = string.atoi(resp.results[0], 16)
		return rev

	def serialNumber(self):
		"""Queries the system for the serial Number and returns an integer."""
		resp = StatusResponse(self.port.command("813"))
		ser = string.atoi(resp.results[0], 16)
		return ser

	def systemVariableValue(self, varNum):
		"""Queries the system for a variable value and returns an integer."""
		varHex = hex(varNum)[2:]
		resp = StatusResponse(self.port.command("815 " + varHex))
		val = string.atoi(resp.results[0], 16)
		return val

	def close(self):
		self.port.close()


class Response:
	def __init__(self, response):
		self.parse(response)

	def parse(self, response):
	
		p = re.compile('\xFF~(.*)(\d+) OK')
		m = p.match(response)

		if (m != None):
			self.raw = m.group(0)
			self.status = m.group(1)
			self.commandsExec = int(m.group(2))
			self.isError = False
		else:
			p = re.compile('\xFF~([0-9ABCDEF]*)( OK )?UI ERROR (\d+)\r\n')
			m = p.match(response)

			self.raw = m.group(0)

			if m.group(1) == '':
				self.commandsExec = 0
			else:
				self.commandsExec = int(m.group(1))

			self.errorNum = int(m.group(3))
			self.isError = True

class StatusResponse(Response):
	"""This is represents all of the status reponses from the
	   Lutron."""

	def __init__(self, response):
		self.parse(response)
		self.parseStatus()
	
	def parseStatus(self):
		p = re.compile('^:([0-9ABCDEF]+) (.*) #$')
		m = p.match(self.status)
		self.code = m.group(1)
		self.results = re.split(' ', m.group(2))


if __name__ == '__main__':
	foo = Lutron()
	print foo.timeNow()
	print foo.astroTimes()
	print foo.date()
	print foo.codeRevLevel()
	print foo.bootCodeRevLevel()
	print foo.serialNumber()
	print foo.systemVariableValue(12)
	print foo.zoneIntensity(12)
	print foo.switchStatus(0, 3, 1)
	print foo.wallStationStatus(0,3)
	print foo.areaStatus(18)
	foo.close()
