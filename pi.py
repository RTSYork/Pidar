#!/usr/bin/env python

import rpyc
import piglow
from rpyc.utils.server import ThreadedServer

t = ThreadedServer(piglow.PiGlowService, port = 18861)
t.start()
