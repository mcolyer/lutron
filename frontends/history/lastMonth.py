#!/usr/bin/python

import time
import historyGraph

day = historyGraph.HistoryGraph(time.time()-(60*60*24*7),time.time(),3600*24,600)
file = open('month.svg','w')
file.write(day.draw(4))
file.close()
