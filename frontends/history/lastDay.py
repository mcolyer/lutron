#!/usr/bin/python

import time
import historyGraph

for i in range(0,3):
	day = historyGraph.HistoryGraph(time.time()-(60*60*24*(i+1)),time.time()-(60*60*24*i),3600*2,600)
	file = open('day-%d.svg' % i,'w')
	file.write(day.draw(1))
	file.close()
