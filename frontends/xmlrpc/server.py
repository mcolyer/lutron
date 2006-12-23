from twisted.web import xmlrpc, server
from xml.dom import minidom
from xml.dom.minidom import Document
from xml import xpath
import MySQLdb

class LutronWebservice(xmlrpc.XMLRPC):
    """An example object to be published."""

    def __init__(self):
    	self.databaseConn = MySQLdb.connect (host = "localhost",
        	                user = "lights",
		                passwd = "",
		                db = "lights")

	self.databaseCursor = self.databaseConn.cursor ()
        self.lightingConfiguration = minidom.parse("lights.xml")

    def xmlrpc_getRoomStatus(self, room):
        """Return information concerning a specific room."""
	result={}
	zones = xpath.Evaluate('/lights/area[@room='+str(room)+']/zone', self.lightingConfiguration.documentElement)
	for zone in zones:
		result[zone.attributes["systemNumber"].value] = self.__queryZone__(int(zone.attributes["systemNumber"].value))
        return str(result)

    def __queryZone__(self, zone):
    	self.databaseCursor.execute ("SELECT intensity from log where zone=%d ORDER BY time DESC LIMIT 1" % zone)
	if (self.databaseCursor.rowcount != 0):
		return self.databaseCursor.fetchone()[0]
	return -1
	
if __name__ == '__main__':
    from twisted.internet import reactor
    r = LutronWebservice()
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()
