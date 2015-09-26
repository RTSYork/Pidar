#!/usr/bin/env python

import rpyc

for i in range(1, 17):
	ip = '192.168.50.' + str(i)
	print 'Connecting to', ip
	conn = rpyc.connect(ip, 18861)
	piglow = conn.root
	piglow.init()
	piglow.all_off()
