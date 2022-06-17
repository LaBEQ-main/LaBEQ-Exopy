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

from exopy.tasks.api import InstrumentTask, InterfaceableTaskMixin

class SetSensAndDynResrvTask(InstrumentTask):
    """ Sets sensitivity mode. OFF - sensitivity and dynamic reserve chosen by device. ON - chosen by user."""

    # Time to wait before execution
    wait_time = Float().tag(pref=True)

    sensitivity = Str().tag(pref=True)
    dynres = Enum('LOW', 'MED', 'HIGH').tag(pref=True)
    mode = Enum('OFF', 'ON').tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
    
    database_entries = set_default({'val': 0.0})
    database_entries = set_default({'mode': 'none'})

    def perform(self):
        
        sleep(self.wait_time)

        if self.mode == "OFF":
            val = self.format_and_eval_string(self.sensitivity)
            
            self.driver.set_sensitivity(val)
            self.driver.set_dynres(self.dynres)
            self.write_in_database('val', val)
        elif self.mode == "ON":
            self.driver.set_sens_mode(self.mode)
            self.write_in_database('mode', self.mode)

class SetTimeConstantTask(InstrumentTask):
    """ Sets time constant (s) and slope (dB)"""

    # Time to wait before execution
    wait_time = Float().tag(pref=True)

    tc = Str().tag(pref=True)
    slope = Enum('6', '12', '18', '24').tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
    
    database_entries = set_default({'tc': 0.0})
    database_entries = set_default({'slope': 0.0})

    def perform(self):
        
        sleep(self.wait_time)

        tc = self.format_and_eval_string(self.tc)
        self.driver.set_tc(tc)

        slope = self.format_and_eval_string(self.slope)
        self.driver.set_tc_slope(slope)

        self.write_in_database('tc', tc)
        self.write_in_database('slope', slope)

            

class ReadSupplyFieldTask(InstrumentTask):
    """     
        Read the current field supply of the system. This value corresponds 
    to "Field (T)" on the iPS UI. It represents the maximum field strength that
    would be produced if the switch was opened to allow the PSU to drive the 
    present circulating current through the coils. It is proportional to the
    current driven by the PSU. 

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_supply_field': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the supply field.

        """
        sleep(self.wait_time)

        value = self.driver.read_supply_field()
        self.write_in_database('ips_supply_field', value)

class ReadSupplyFieldRateTask(InstrumentTask):
    """     
        Read the Supply field rate of the system in T/min. This value gives
    the target rate of change of the supply field during ramping. 

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

        value = self.driver.read_supply_field_rate()
        self.write_in_database('mag_field_setpoint', value)

class ReadMagnetFieldTask(InstrumentTask):
    """     
        Read the magnetic field strength produced by the energized SC coils. 
    This value corresponds to "Magnet (T)" on the iPS UI. This value is the 
    strength of the field produced by the SC magnet coils measured by a 
    magnetometer inside the system.


        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'magnet_field': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field produced by SC coils.

        """
        sleep(self.wait_time)

        value = self.driver.read_magnet_field()
        self.write_in_database('magnet_field', value)

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

class ReadMagnetCurrentTask(InstrumentTask):
    """     
        Read the current circulating through the magnet coils in units of Amps (A).
    
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_magnet_current': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnet current.

        """
        sleep(self.wait_time)

        value = self.driver.read_supply_current()
        self.write_in_database('ips_magnet_current', value)

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

class SetTargetCurrentTask(InstrumentTask):
    """
        Sets the target. 

        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the mramp.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    target_current = Str().tag(pref=True)

    database_entries = set_default({'ips_target_current': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.target_current)

        self.driver.set_target_current(value)
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

class SetTargetCurrentRateTask(InstrumentTask):
    """
        Sets the target current ramp rate. 

        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the mramp.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    target_current_rate = Str().tag(pref=True)

    database_entries = set_default({'ips_target_current_rate': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and set the target current ramp rate.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.target_current_rate)

        self.driver.set_target_current_rate(value)
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

class SetTargetFieldTask(InstrumentTask):
    """
        Sets the target field. 

        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the mramp.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    target_field = Str().tag(pref=True)

    database_entries = set_default({'ips_target_field': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and set the target field.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.target_field)

        self.driver.set_target_field(value)
        self.write_in_database('ips_target_field', value)

class ReadTargetFieldRateTask(InstrumentTask):
    """     
        Read target field rate in units of Tesla/minute (T/m). The target field
    rate is a quantity stored in memory. It's an implicit target current rate. 
    It is the rate at which the iPS will ramp the field to the target field by 
    driving current when commanded to do so.
        
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_target_field_rate': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the target field rate.

        """
        sleep(self.wait_time)

        value = self.driver.read_target_field_rate()
        self.write_in_database('ips_target_field_rate', value)

class SetTargetFieldRateTask(InstrumentTask):
    """
        Sets the target field rate. 

        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the mramp.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)
    target_field_rate = Str().tag(pref=True)

    database_entries = set_default({'ips_target_field_rate': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and set the target field rate.

        """
        sleep(self.wait_time)

        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.target_field_rate)

        self.driver.set_target_field_rate(value)
        self.write_in_database('ips_target_field_rate', value)

class ReadSwitchHeaterStatusTask(InstrumentTask):
    """     
        Read switch heater status. Will return "ON" or "OFF" and store
    in the database.w
        
        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'ips_switch_heater_status': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the switch heater status.

        """
        sleep(self.wait_time)

        value = self.driver.read_switch_status()
        self.write_in_database('ips_switch_heater_status', value)

class RampToTargetTask(InstrumentTask):
    """
        Ramps the magnetic field to target field value in Tesla (T). It drives 
    current from the PSU to achieve the target field strength at the target rate. 
    If the switch heater is OFF, then the operation will throw an error. If the 
    target field is greater than 0.1T, the operaton will throw an error. The 
    supply field and the magnet field must be equal before ramping otherwise the 
    magnet may quench.The switch heater must be open in order to energize the 
    magnet coils. 

        Setting the target current in favor of the target field before executing 
    the RampToTargetTask has the same effect. The quantities are coupled. When one 
    is set, the other changes to reflect the corresponding current or field.

        Wait for any parallel operation before execution and then wait the
    specified time before perfoming the mramp.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)
        self.driver.ramp_to_target()

