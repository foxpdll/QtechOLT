#!/usr/bin/env python
# -*- coding: UTF8 -*-
#---------------------------------------------------------------------------------------------------------------------------------------
from qtech import *
o=OLT("172.16.199.191","user","password",0)
rrr=o.showONTBrief()
for i in rrr:
    print i,rrr[i]
rrr=o.showONTBrief()
for i in rrr:
    print i,rrr[i]
#pprint.pprint(ontbrief)
#addSNMPData(ontbrief,"172.16.199.119","public")
#pprint.pprint(ontbrief)
#print o.setONTDefConf("0/1/1")
#o.setONTDescr("0/2/10","test")
#o.setONTIfAcessVlan("0/2/10",1,34)
#o.setONTIfAcessVlan("0/2/10",2,100)
#o.setONTIfAcessVlan("0/2/10",3,200)
#o.setONTIfAcessVlan("0/2/10",4,99)
#o.setONTIfTrunk("0/2/10",4)
#o.uploadFW()
#o.ONTUpdateFW("0/2/10")
#o.ONTReboot("0/2/10")
#print o.showONTConf("0/2/10")
#o.saveConf()
