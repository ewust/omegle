#!/usr/bin/python

import omegle
import asyncore

a = omegle.OmegleClient()
b = omegle.OmegleClient()
#c = OmegleClient()

a.add_partner(b)
#a.add_partner(c)

b.add_partner(a)
#b.add_partner(c)

#c.add_partner(a)
#c.add_partner(b)


asyncore.loop()

