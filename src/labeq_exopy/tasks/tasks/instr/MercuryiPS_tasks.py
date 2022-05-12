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


class ReadFieldPotentialTask(InstrumentTask):
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

    database_entries = set_default({'mag_field_setpoint': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        value = self.driver.read_field_potential()
        self.write_in_database('mag_field_setpoint', value)

class ReadFieldActualTask(InstrumentTask):
    """     
        Read actual field strength produced by energized SC coils. This value 
    corresponds to "Magnet (T)" on the iPS UI. This value is the strength of 
    the field produced by the SC magnet coils measured by a magnetometer inside the system.


    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the operation.

    """
    # Time to wait before operation.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'mag_field_actual': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        value = self.driver.read_field_actual()
        self.write_in_database('mag_field_actual', value)

class RampMagFieldTask(InstrumentTask):
    """Ramp magnetic field to set value. Drives current from PSU to achieve
    desired field strength in the coils. The set field and the actual field 
    must be equal before ramping otherwise the magnet may quench.The switch 
    needs to be open in order to energize coils. 

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