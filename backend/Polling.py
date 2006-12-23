import MySQLdb
from LutronWrapper import Lutron
from xml.dom import minidom
from xml.dom.minidom import Document
from xml import xpath

lutron = Lutron()

conn = MySQLdb.connect (host = "localhost",
                        user = "lights",
                        passwd = "",
                        db = "lights")

cursor = conn.cursor ()

document = minidom.parse("lights.xml")
zones = xpath.Evaluate('//zone', document.documentElement)

for zone in zones:
	id = int(zone.attributes["systemNumber"].value)
	cursor.execute ("SELECT intensity from log where zone=%d ORDER BY time DESC LIMIT 1" % id)

	lastIntensity = cursor.fetchone()

	if(cursor.rowcount != 0):
		lastIntensity = lastIntensity[0]

	intensity = lutron.zoneIntensity(id)

	if (intensity != lastIntensity):
		cursor.execute ("INSERT INTO log (zone, intensity) VALUES (%d,%d)" % (id, intensity))

cursor.close ()
conn.close ()
