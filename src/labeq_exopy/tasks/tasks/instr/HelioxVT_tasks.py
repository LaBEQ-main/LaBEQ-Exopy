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

class ReadVTITemperatureTask_HelioxVT(InstrumentTask):
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

class SetVTITemperatureTask_HelioxVT(InstrumentTask):
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

class ReadVTIPressureTask_HelioxVT(InstrumentTask):
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

class SetVTIPressureTask_HelioxVT(InstrumentTask):
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

class ReadVTIValvePercentageTask_HelioxVT(InstrumentTask):
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

class ReadHe3PotTemperatureTask_HelioxVT(InstrumentTask):
    """
        Read He3Pot temperature.

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'he3pot_temp': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the temperature.

        """
        sleep(self.wait_time)

        
        value = self.driver.read_he3pot_temp()
        self.write_in_database('he3pot_temp', value)

class SetHe3PotTemperatureTask_HelioxVT(InstrumentTask):
    """
        Sets the He3Pot temp set point. 

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    temp_setpoint = Str().tag(pref=True)

    database_entries = set_default({'he3pot_temp_setpoint': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and set the temperature.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.temp_setpoint)

        self.driver.set_he3pot_temp(value)
        self.write_in_database('he3pot_temp_setpoint', value)

class Read1KPlateTemperatureTask_HelioxVT(InstrumentTask):
    """
        Read 1KPlate temperature.

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'1Kplate_temp': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the temperature.

        """
        sleep(self.wait_time)

        value = self.driver.read_1Kplate_temp()
        self.write_in_database('1Kplate_temp', value)

class ReadHe3PotRuOx_HelioxVT(InstrumentTask):
    """
        Read He3PotRuOx temperature.

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'he3potRuOx_temp': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the temperature.

        """
        sleep(self.wait_time)

        value = self.driver.read_he3potRuOx_temp()
        self.write_in_database('he3potRuOx_temp', value)

class ReadHe3PotCernox_HelioxVT(InstrumentTask):
    """
        Read He3PotCernox temperature.

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'he3potCernox_temp': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the temperature.

        """
        sleep(self.wait_time)

        value = self.driver.read_he3potCernox_temp()
        self.write_in_database('he3potCernox_temp', value)

class ReadHe3SorbTemp_HelioxVT(InstrumentTask):
    """
        Read He3SorbTemp temperature.

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'he3sorb_temp': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the temperature.

        """
        sleep(self.wait_time)

        value = self.driver.read_he3sorb_temp()
        self.write_in_database('he3sorb_temp', value)

class SetHe3SorbTemp_HelioxVT(InstrumentTask):
    """
        Set He3SorbTemp temperature.

        Wait for any parallel operation before execution and then wait the
    specified time before execution

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    temp_setpoint = Str().tag(pref=True)

    database_entries = set_default({'he3sorb_temp_setpoint': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and set the temperature.

        """
        sleep(self.wait_time)
        # self.write_in_database('he3sorb_temp', self.temp_setpoint)

        value = self.format_and_eval_string(self.temp_setpoint)
        self.driver.set_he3sorb_temp(value)

        self.write_in_database('he3sorb_temp_setpoint', value)