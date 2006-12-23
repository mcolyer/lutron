#!/usr/bin/python

import time
import historyGraph

for i in range(0,3):
	week = historyGraph.HistoryGraph(time.time()-(60*60*24*7*(i+1)),time.time()-(60*60*24*7*i),3600*24,600)
	file = open('week-%d.svg' % i,'w')
	file.write(week.draw())
	file.close()
