from time import sleep

from atom.api import Float, Str, set_default

from exopy.tasks.api import InstrumentTask


class MeasMagFieldTask(InstrumentTask):
    """Measure an applied magnetic field.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'mag_field': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        value = self.driver.read_mag_field()
        self.write_in_database('mag_field', value)

class RampMagFieldTask(InstrumentTask):
    """Ramp magnetic field.

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