"""Task to read a magnetic field.

"""
from time import sleep

from atom.api import Float, set_default

from exopy.tasks.api import InstrumentTask


class MeasMagFieldTask(InstrumentTask):
    """Measure an applied magnetic field.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'field': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the magnetic field.

        """
        sleep(self.wait_time)

        value = self.driver.persistent_field
        self.write_in_database('field', value)