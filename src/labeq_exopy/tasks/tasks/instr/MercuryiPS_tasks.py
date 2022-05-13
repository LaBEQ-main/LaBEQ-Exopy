# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

from time import sleep

from atom.api import Float, Str, set_default

from exopy.tasks.api import InstrumentTask


class ReadPotentialFieldTask(InstrumentTask):
    """     
        Read the current field potential of the system. This value corresponds 
    to "Field (T)" on the iPS UI. It represents the maximum field strength that
    would be produced if the switch was opened to allow the PSU to drive the 
    present circulating current through the coils. It is proportional to the
    current driven by the PSU. 

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'potential_field': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        value = self.driver.read_potential_field()
        self.write_in_database('potential_field', value)

class ReadPotentialFieldRateTask(InstrumentTask):
    """     
        Read the potential field rate of the system in T/min. This value gives
    the target rate of change of the potential field during ramping. 

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'mag_field_setpoint': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        value = self.driver.read_potential_field_rate()
        self.write_in_database('mag_field_setpoint', value)

class ReadActualFieldTask(InstrumentTask):
    """     
        Read actual field strength produced by energized SC coils. This value 
    corresponds to "Magnet (T)" on the iPS UI. This value is the strength of 
    the field produced by the SC magnet coils measured by a magnetometer inside the system.


        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'actual_field': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        value = self.driver.read_actual_field()
        self.write_in_database('actual_field', value)

class ReadSupplyVoltageTask(InstrumentTask):
    """     
        Read voltage supplied by magnet PSU in units of volts (V).
    
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_supply_voltage': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the supply voltage.

        """
        sleep(self.wait_time)

        value = self.driver.read_supply_voltage()
        self.write_in_database('ips_supply_voltage', value)

class ReadSupplyCurrentTask(InstrumentTask):
    """     
        Read current supplied by magnet PSU in units of Amps (A).
    
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_supply_current': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the supply current.

        """
        sleep(self.wait_time)

        value = self.driver.read_supply_current()
        self.write_in_database('ips_supply_current', value)

class ReadSupplyCurrentRateTask(InstrumentTask):
    """     
        Read supply current rate provided by PSU in units of volts per min (A/min).
    
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_supply_current_rate': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the supply current rate.

        """
        sleep(self.wait_time)

        value = self.driver.read_supply_current_rate()
        self.write_in_database('ips_supply_current_rate', value)

class ReadCoilCurrentTask(InstrumentTask):
    """     
        Read current in coils in units of Amps (A). 
    
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_coil_current': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the coil current.

        """
        sleep(self.wait_time)

        value = self.driver.read_supply_current()
        self.write_in_database('ips_coil_current', value)

class ReadTargetCurrentTask(InstrumentTask):
    """     
        Read target current in units of Amps (A). The target current is a 
    quantity stored in memory. It is the amount of current that the 
    iPS will ramp up to if commanded to do so.
        
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_target_current': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the target current.

        """
        sleep(self.wait_time)

        value = self.driver.read_target_current()
        self.write_in_database('ips_target_current', value)

class ReadTargetCurrentRateTask(InstrumentTask):
    """     
        Read target current rate in units of Amps/minute (A/m). The target 
    current rate is a quantity stored in memory. It is the rate at which the 
    iPS will ramp the current when commanded to do so.
        
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_target_current_rate': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the target current rate.

        """
        sleep(self.wait_time)

        value = self.driver.read_target_current_rate()
        self.write_in_database('ips_target_current_rate', value)

class ReadTargetFieldTask(InstrumentTask):
    """     
        Read target field in units of Tesla (T). The target field is a
    quantity stored in memory. It's an implicit target current. When the
    iPS is commanded to ramp to this set point, it will drive the current 
    necessary to produce the target field value in the coils. The switch 
    heater must be open in order for the coils to be energized.
        
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_target_field': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the target field.

        """
        sleep(self.wait_time)

        value = self.driver.read_target_field()
        self.write_in_database('ips_target_field', value)

class RampMagFieldTask(InstrumentTask):
    """
        Ramps the magnetic field to target field value in Tesla (T). It drives 
    current from the PSU to achieve the target field strength at the target rate. 
    The supply field and the magnet field must be equal before ramping otherwise 
    the magnet may quench.The switch heater must be open in order to energize the 
    magnet coils. 

        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the mramp.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    ramp_val = Str().tag(pref=True)

    database_entries = set_default({'mag_field_ramp_val': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.ramp_val)

        self.driver.ramp_mag_field(value)
        self.write_in_database('mag_field_ramp_val', value)