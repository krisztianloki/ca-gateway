#!/usr/bin/env python
'''Controls the gateway'''
import subprocess
import time
import os
import epics
import SIOCControl
import gwtests


class GatewayControl:
    gatewayProcess = None
    def startGateway(self, gatewaySIPPort, iocPort):
        '''Starts the gateway'''
        gateway_executable = "../../bin/{0}/gateway".format(os.environ['EPICS_HOST_ARCH'])
        print "Testing the gateway executable at", gateway_executable
        gateway_commands = [gateway_executable]
        # -debug 10 -archive -sip 127.0.0.1 -sport 12001 -cip 127.0.0.1 -cport 5066
        gateway_commands.extend(["-sip", "127.0.0.1", "-sport", gatewaySIPPort, "-cip", "127.0.0.1", "-cport", iocPort])
        gateway_commands.extend(["-access", "access.txt"])
        gateway_commands.extend(["-archive"])
        if gwtests.verbose:
            gateway_commands.extend(["-debug", "10"]);
        print "Starting the gateway using", gateway_commands
        self.gatewayProcess = subprocess.Popen(gateway_commands)

    def stop(self):
        self.gatewayProcess.terminate()

if __name__ == "__main__":
    siocControl = SIOCControl.SIOCControl()
    siocControl.startSIOCWithDefaultDB("12782")
    gatewayControl = GatewayControl()
    gatewayControl.startGateway(os.environ['EPICS_CA_SERVER_PORT'], "12782")
    time.sleep(10)
    epics.ca.initialize_libca()
    print epics.caget('gateway:auto')
    epics.caput('gateway:passive0', 10)
    time.sleep(1)
    print epics.caget('gateway:passive0')
    epics.caput('gateway:passive0', 11)
    time.sleep(1)
    print epics.caget('gateway:passive0')
    time.sleep(1)
    epics.ca.finalize_libca()
    siocControl.stop()
    time.sleep(1)
    gatewayControl.stop()
