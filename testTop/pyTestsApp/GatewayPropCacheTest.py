#!/usr/bin/env python
import os
import unittest
import epics
import SIOCControl
import GatewayControl
import gwtests
import time
import subprocess

class GatewayPropCacheTest(unittest.TestCase):
    '''The gateway caches the properties; we want it to establish a DBE_PROP monitor no matter what and update its internal property cache
    Establish no monitors - make a change to the HIGH outside of the gateway; then ca_get the value of the PV's HIGH from the gateway; received changed value
    '''

    def setUp(self):
        self.siocControl = SIOCControl.SIOCControl()
        self.gatewayControl = GatewayControl.GatewayControl()
        self.siocControl.startSIOCWithDefaultDB("12782")
        self.gatewayControl.startGateway(os.environ['EPICS_CA_SERVER_PORT'], "12782")
        time.sleep(2)
        epics.ca.initialize_libca()

        
    def tearDown(self):
        time.sleep(1)
        epics.ca.finalize_libca()
        self.siocControl.stop()
        time.sleep(1)
        self.gatewayControl.stop()
        
    def testGatewayPropCache(self):
        '''Establish no monitors - make a change to the HIGH outside of the gateway; then ca_get the value of the PV's HIGH from the gateway; received changed value'''
        if gwtests.verbose:
                print "Running GatewayPropCacheTest.testGatewayPropCache"
        pvHIGH = epics.PV("gateway:gwcachetest.HIGH", auto_monitor=None)
        time.sleep(1)
        highVal = pvHIGH.get()
        time.sleep(1)
        self.assertTrue(highVal == 10.0, "We expect the HIGH to be 10. Instead it is " + str(highVal))
        # make a change to the HIGH outside the gateway; so we talk to the IOC directly. 
        if gwtests.verbose:
                print "After the first assert"
        caputEnv = os.environ.copy()
        caputEnv['EPICS_CA_SERVER_PORT'] = "12782"
        caputEnv['EPICS_CA_ADDR_LIST'] = "localhost"
        for val in range(10, 100, 10):
            subprocess.Popen(['caput', 'gateway:gwcachetest.HIGH', str(val)], env=caputEnv)
            time.sleep(1)
            highVal = pvHIGH.get()
            time.sleep(1)
            self.assertTrue(highVal == val, "We expect the HIGH to be " + str(val) + " Instead it is " + str(highVal))
        
        