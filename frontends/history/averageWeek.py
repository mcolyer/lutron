#!/usr/bin/python

import time
import historyGraph

day = historyGraph.HistoryGraph(time.time()-(60*60*24*7),time.time(),3600*24,1200)
file = open('averageWeek.svg','w')
file.write(day.draw(4))
file.close()
