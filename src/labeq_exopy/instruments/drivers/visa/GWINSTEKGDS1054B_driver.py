# -----------------------------------------------------------------------------
# Jake Macdonald, 7/9/2022

#first parallel program with visa!!
# -----------------------------------------------------------------------------
"""Driver for GWINSTEK GDS-1054B instruments using VISA library.

"""
import time
import pyvisa
from time import sleep
from multiprocessing import Process
from multiprocessing import current_process


from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument




def ramp (name, duration, initVal, goal) : 
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource(name)
    inst.read_termination = '\n' 

    start = time.time()
    dif = goal - initVal
    percent = 0
    while percent < 1 :
        percent = (time.time() - start) /duration
        inst.write ('CURS:H1Position ' + str(initVal + (dif * percent)))
        sleep(.05)

class GWINSTEKGDS1054B(VisaInstrument):

    caching_permissions = {'function': True}

    protocoles = {'TCPIP': 'INSTR'}

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(GWINSTEKGDS1054B, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @secure_communication()
    def check_connection(self):
        """
        """
        return False

    @secure_communication()
    def read_mean(self):       
        value = self.query('meas:mean?')
        print (value)

        if value:
            return float(value)
        else:
            raise InstrIOError('GWINSTEK GDS-1054B: throwed a fit')

    @secure_communication()
    def ramp_cursor(self, duration, goal):   
        if __name__ == 'labeq_exopy.instruments.drivers.visa.GWINSTEKGDS1054B_driver':
            print (self.connection_str)
            thisProcess = current_process()
            thisProcess.daemon = False
            self.write('CURS:MOD H')
            initVal = self.query('CURS:H1Position?')
            process = Process(target=ramp, args=(self.connection_str, duration, float(initVal), goal))
            process.start()