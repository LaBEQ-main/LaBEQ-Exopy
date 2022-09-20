# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

from time import sleep
from atom.api import Float, Str, Enum, set_default
from exopy.tasks.api import InstrumentTask, InterfaceableTaskMixin, TaskInterface

class ReadVTITemperatureTask(InstrumentTask):
    """
        Read the VTI temperature. 

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'vti_temp': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the temperature.

        """
        sleep(self.wait_time)
        value = self.driver.read_VTI_temp()
        self.write_in_database('vti_temp', value)

class SetVTITemperatureTask(InstrumentTask):
    """
        Sets the target VTI temp set point. 

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    temp_setpoint = Str().tag(pref=True)

    database_entries = set_default({'vti_temp_setpoint': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and set the temperature.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.temp_setpoint)

        self.driver.set_VTI_temp(value)
        self.write_in_database('vti_temp_setpoint', value)

class ReadVTIPressureTask(InstrumentTask):
    """
        Read the VTI pressure. 

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'vti_pres': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """
        Wait and read the pressure.

        """
        sleep(self.wait_time)
        value = self.driver.read_VTI_pres()
        self.write_in_database('vti_pres', value)

class SetVTIPressureTask(InstrumentTask):
    """
        Set the VTI pressure. 

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    pres_setpoint = Str().tag(pref=True)

    database_entries = set_default({'vti_pres_setpoint': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """
        Wait and set the pressure.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.pres_setpoint)
        self.driver.set_VTI_pres(value)
        self.write_in_database('vti_pres_setpoint', value)

class ReadVTIValvePercentageTask(InstrumentTask):
    """
        Read the VTI valve percentage. 

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'vti_valve_perc': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """
        Wait and read the valve percentage.

        """
        sleep(self.wait_time)
        value = self.driver.read_VTI_valv_perc()
        self.write_in_database('vti_valve_perc', value)

class ReadProbeTemperatureTask(InstrumentTask):
    """
        Read probe temperature.

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'probe_temp': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the temperature.

        """
        sleep(self.wait_time)

        
        value = self.driver.read_probe_temp()
        self.write_in_database('probe_temp', value)

class SetProbeTemperatureTask(InstrumentTask):
    """
        Sets the probe temp set point. 

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    temp_setpoint = Str().tag(pref=True)

    database_entries = set_default({'probe_temp_setpoint': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and set the temperature.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.temp_setpoint)

        self.driver.set_probe_temp(value)
        self.write_in_database('probe_temp_setpoint', value)