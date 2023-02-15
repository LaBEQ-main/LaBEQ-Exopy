#Jake Macdonald 7/8/22
"""Yokogawa GS200 tasks

"""

from time import sleep

from atom.api import (Enum, Float, Str, set_default)

from exopy.tasks.api import InstrumentTask


class SetRampTaskYoko(InstrumentTask):
    """ Set Ramp Task for Yokogawa GS200

    """
    func_v = Enum('Voltage', 'Current').tag(pref=True)
    default_v = Enum('True', 'False').tag(pref=True)
    ramp_v = Str().tag(pref=True)
    goal_v = Float().tag(pref=True)

    database_entries = set_default({'set_ramp': 1.0})



    def perform(self):
      
        funcVal = ''
        if (self.func_v == 'Voltage'):
            funcVal = 'VOLT'
        else: 
            funcVal = 'CURR'

        value = self.driver.set_ramp(self.ramp_v,funcVal, self.default_v, self.goal_v)
        self.write_in_database('set_ramp', value)

class SetRangeTaskYoko(InstrumentTask):
    """Set Ramp Task for Yokogawa GS200

    """

    wait_time = Float().tag(pref=True)
    func_v = Enum('Voltage', 'Current', 'Both').tag(pref=True)
    set_range_val = Str().tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
        
    database_entries = set_default({'set_range_val': 1.0})

    def perform(self):
        sleep(self.wait_time)

        funcVal = ''
        if self.func_v == 'Voltage':
            funcVal = 'VOLT'
        elif self.func_v == 'Current': 
            funcVal = 'CURR'
        
        if self.func_v == 'Both' :
            self.driver.set_range_yoko(self.set_range_val,'VOLT')
            value = self.driver.set_range_yoko(self.set_range_val,'CURR')
        else :
            value = self.driver.set_range_yoko(self.set_range_val,funcVal)

        self.write_in_database('set_range_val', value)

class SetComplianceTaskYoko(InstrumentTask):
    """Set Ramp Task for Yokogawa GS200

    """

    func_v = Enum('Voltage', 'Current').tag(pref=True)
    set_limit_val = Str().tag(pref=True)

        
    database_entries = set_default({'set_limit_val': 1.0})

    def perform(self):
        value = self.format_and_eval_string(self.set_limit_val)
        self.driver.set_compliance_yoko(value, self.func_v)
        self.write_in_database('set_limit_val', value)

