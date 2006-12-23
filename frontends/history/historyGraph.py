from SVGdraw import *
from xml.dom import minidom
from xml.dom.minidom import Document
from xml import xpath
import time
import datetime
import MySQLdb
import colorsys

class HistoryGraph:
	def __init__(self, start, stop, interval, width=740):
		""" start - the starting time of the graph (datetime)
		    end - the ending time of the graph (datetime)
		    interval - time interval (timedelta)"""
		self.start = start
		self.stop = stop
		self.interval = interval
		self.width = width
		self.scale = (width-40)/(stop-start)
		
		self.yLabelSize = 10 #pixels
		self.roomHeight = 20 #pixels
		
		self.lightingConfiguration = minidom.parse("lights.xml")

	def setRowHeight(self, height):
		"""Sets the height of the each row on the graph in pixels"""
		self.roomHeight = height
	
	def draw(self, average = 1, floor=0, room=0):
		"""Determine which floors are displayed.
		   floor - 0 represents all floors, otherwise represents floor number to be drawn
		   room - 0 represents all rooms, otherwise only the specified room is drawn. Overides floor."""
		
		# Don't start the labels at the top of the of graph
		self.lastDrawnY = 10
		
		# Connect to the database
		self.databaseConn = MySQLdb.connect (host = "localhost", user = "lights", passwd = "spandex", db = "lights")	
		self.databaseCursor = self.databaseConn.cursor ()

		# Draw a single room
		if room != 0:
			self.__createSVGDocument__(0)
			self.__drawIntervals__()
			self.__drawRoomLabel__(room.value)
			
			for i in range(0,average):
				self.__drawRoom__(room.value, (1./average))
				if i+1 != average:
					span = self.stop-self.start
					self.stop -= span
					self.start -= span
			
			self.databaseConn.close()
			self.d.setSVG(self.s) 
			return self.d.toXml()
		
		# Otherwise select a single floor
		if floor != 0:
			rooms = xpath.Evaluate('/lights/area[starts-with(@room, %d)]/@room' % floor, self.lightingConfiguration.documentElement)
		# Otherwise select all floors
		else:
			rooms = xpath.Evaluate('/lights/area/@room', self.lightingConfiguration.documentElement)

		# Create the SVG document
		self.__createSVGDocument__(len(rooms))
		self.__drawIntervals__()
		
		# Sort the list in ascending order
		rooms.sort()
		rooms.reverse()

		# Iterate through the rooms
		origStart = self.start
		origStop = self.stop
		for room in rooms:
			self.__drawRoomLabel__(room.value)
			for i in range(0,average):
				print room.value
				print self.stop
				self.__drawRoom__(int(room.value), (1./average))
				if i+1 != average:
					span = self.stop-self.start
					self.stop -= span
					self.start -= span
			self.start = origStart
			self.stop = origStop
			self.lastDrawnY += self.roomHeight

		self.databaseConn.close()
		self.d.setSVG(self.s) 
		return self.d.toXml()

	def __createSVGDocument__(self, rooms):
		"""Initializes the SVG document."""
		self.d = drawing()
		self.height = self.roomHeight*rooms+40
		self.s = svg(None,'%d px' % self.width,'%d px' % self.height)
		ds=description('Light History Graph')
		self.s.addElement(ds)
	
	def __drawRoomLabel__(self, room):
		# Draw centered horizontal line 
		yCoordinate = self.lastDrawnY+(self.roomHeight/2)
		line = rect('25px','%d px' % yCoordinate,'%d px' % (self.width-35),'1px', '#f0f0f0')
		self.s.addElement(line)

		# Draw room label
		roomLabel = text('2px','%d px' % (yCoordinate+self.yLabelSize/2), room, '%d px' % self.yLabelSize,'arial')
		self.s.addElement(roomLabel)
	
	def __drawRoom__(self, room, transparency):
		"""Draws a single row of the graph"""
		
		yCoordinate = self.lastDrawnY+(self.roomHeight/2)
		
		# Calculate the top of the bar so that it is centered
		zones = xpath.Evaluate('/lights/area[@room=%d]/zone' % room, self.lightingConfiguration.documentElement)
		yCoordinate = self.lastDrawnY+(((6-len(zones))*((self.roomHeight-4)/6.)+4)/2)+.5
		
		for zone in zones:
			systemNumber =  zone.getAttribute('systemNumber')
			
			self.databaseCursor.execute ('(SELECT zone, UNIX_TIMESTAMP(time) as time, intensity FROM log WHERE' + 
			  '(zone=' + systemNumber + ') && (UNIX_TIMESTAMP(time) <= ' + str(self.start) + ') ORDER BY time DESC LIMIT 1)' +
			  'UNION DISTINCT (SELECT zone, UNIX_TIMESTAMP(time) as time, intensity FROM log WHERE' +
			  '(zone=' + systemNumber + ') && (UNIX_TIMESTAMP(time) > ' + str(self.start) + ') && (UNIX_TIMESTAMP(time) <= ' + str(self.stop) + '))'+
			  ' ORDER BY time ASC;')
			  
			# No records found for this zone during this period
			if (self.databaseCursor.rowcount == 0):
				continue
			
			# Otherwise retrieve all events
			events = self.databaseCursor.fetchall()
				
			# The database only records changes, so we have to group
			# changes into periods in which the lights are on
			periods = []
			for event in events:
				if event[2] != 0 and len(periods) == 0:
					periods.append([event[1],event[2],0])
				elif event[2] != 0 and periods[-1][2] == 0:
					periods[-1][2] = event[1]
					periods.append([event[1],event[2],0])
				elif event[2] != 0: 
					periods.append([event[1],event[2],0])
				elif len(periods) != 0:
					periods[-1][2] = event[1]

			# Make sure the period gets closed if the lights are currently on
			if len(periods) > 0 and periods[-1][2] == 0:
					periods[-1][2] = self.stop
			
			# Draw each period on the graph.
			for period in periods:
				xCoordinate = (period[0]-self.start)*self.scale
				
				# The SQL statement will select on-events even if they do not lie within start and stop times
				if xCoordinate < 0:
					xCoordinate = 0
				
				width = (period[2]-self.start)*self.scale - xCoordinate
				color = self.__determineColor__(room, period[1], transparency)
				periodRect=rect('%f px' % (xCoordinate+30),'%f px' % yCoordinate,'%f px' % width,'%f px' % ((self.roomHeight-4)/6.+.1)) 
				periodRect.attributes['style'] = "fill: %s;fill-opacity: %f" % color
				self.s.addElement(periodRect)
			
			yCoordinate += (self.roomHeight-4)/6.

		
	def __drawIntervals__(self):
		"""Draws all of the intervals on the graph."""
		
		interval = self.stop - (self.stop % self.interval)
		
		# Creates the y-axis label
		yAxisLabel = text('%d px' % (self.width/2),'%d px' % (self.height-5), self.__getLabel__(interval)[1], '%d px' % self.yLabelSize,'arial')
		yAxisLabel.attributes['style'] = 'text-anchor:middle'
		self.s.addElement(yAxisLabel)
		
		# Creates all of the intervals
		while (interval > self.start):
			xCoordinate = (interval-self.start)*self.scale
			
			# Line
			line=rect('%d px' % (xCoordinate+30),'0 px','1 px','%d px' % (self.height-30),'#c8c8c8') #define a rectangle
			self.s.addElement(line)
			
			# Line label
			intervalLabel = text('%d px' % (xCoordinate+30),'%d px' % (self.height-20), self.__getLabel__(interval)[0], '%d px' % self.yLabelSize,'arial')
			intervalLabel.attributes['style'] = 'text-anchor:middle'
			self.s.addElement(intervalLabel)
			
			interval -= self.interval

	def __determineColor__(self, room, intensity, transparency):
		"""Colors each floor a different color."""
		
		if room > 400:
			color = colorsys.hsv_to_rgb(81/255., (intensity/127.), 1.)
		elif room > 300:
			color = colorsys.hsv_to_rgb(29/255., (intensity/127.), 1.)
		elif room > 200:
			color = colorsys.hsv_to_rgb(163/255., (intensity/127.), 1.)
		elif room > 100:
			color = colorsys.hsv_to_rgb(0.0, (intensity/127.), 1.)
		
		return ('#%02x%02x%02x' % ((color[0]*255),(color[1]*255),(color[2]*255)), transparency)

	def __getLabel__(self, instant):
		"""Decides whether to return minutes, hours or days based on interval and returns the appropriate label"""
		
		instantDT = datetime.datetime.fromtimestamp(instant)
		
		if (self.interval/60 < 60):
			return ('%d' % instantDT.minute, "Minutes")
		elif (self.interval/(3600) < 24):
			return ('%d' % instantDT.hour, "Hours")
		elif (self.interval/(3600*24) < 7):
			return ('%d/%d' % (instantDT.month, instantDT.day), "Days")
		elif (self.interval/(3600*24*7) < 4):
			return ('%d' % instantDT.month, "Months")
