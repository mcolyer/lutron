import xmlrpclib
from xml.dom import minidom
from xml.dom.minidom import Document
from xml import xpath

s = xmlrpclib.Server('http://lights.acl.olin.edu:7080/')
document = minidom.parse("/home/mcolyer/SVG/ac.svg")

# The following wigged out, I think it is a bug in python 2.3.4 but not 2.3.5
#nodes = xpath.Evaluate('//g[@id="rooms"]/*', document.documentElement)

nodes = xpath.Evaluate('descendant::g[@id="rooms"]/*', document.documentElement)

for node in nodes:
        room =  node.attributes["id"].value
	intensity = eval(s.getRoomStatus(int(room))).values()
	
	# If the room is not off
	if (len(intensity) != 0):
		#Get the style string
		styleString = node.attributes["style"].value

		#Split it out into pairs
		styles = styleString.split(";")
		
		#Create a dictionary of the pairs
		stylePairs = {}
		for style in styles:
			attribute, value = style.split(":")
			stylePairs[attribute] = value
		
		#Set the new values
		stylePairs["fill"] = "#f7f4a4"
		stylePairs["fill-opacity"] = str(intensity[0]/127.000)
		
		#Concentate the dictionary into a string
		styleString = ""
		for key,value in stylePairs.iteritems():
			styleString += key+":"+value+";"
			
		node.setAttribute("style", styleString)
		#print
		#print styleString

print document.toxml()
