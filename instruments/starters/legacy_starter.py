# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""The manifest contributing the extensions to the main application.

"""
from exopy.utils.traceback import format_exc
from exopy.instruments.api import BaseStarter


class LegacyStarter(BaseStarter):
    """Starter for legacy instruments.

    """
    def start(self, driver_cls, connection, settings):
        """Start the driver by first formatting the connections infos.

        """
        c = self.format_connection_infos(connection)
        c.update(settings)
        return driver_cls(c)

    def check_infos(self, driver_cls, connection, settings):
        """Attempt to open the connection to the instrument.

        """
        c = self.format_connection_infos(connection)
        c.update(settings)
        driver = None
        try:
            driver = driver_cls(c)
            res = driver.connected
        except Exception:
            return False, format_exc()
        finally:
            if driver is not None:
                driver.close_connection()
        return res, ('Instrument does not appear to be connected but no '
                     'exception was raised.')

    def reset(self, driver):
        """Clear the driver cache.

        """
        driver.clear_cache()

    def stop(self, driver):
        """Close the connection.

        """
        driver.close_connection()

    def format_connection_infos(self, infos):
        """Format the connection to match the expectancy of the driver.

        """
        raise NotImplementedError()


class VisaLegacyStarter(LegacyStarter):
    """Starter for legacy visa instruments.

    """
    def format_connection_infos(self, infos):
        """Use pyvisa to build the canonical resource name.

        """
        from pyvisa.rname import assemble_canonical_name
        infos = {k: v for k, v in infos.items() if v}
        if 'resource_name' in infos:
            return {'resource_name': infos['resource_name']}
        else:
            return {'resource_name': assemble_canonical_name(**infos)}

class DllLegacyStarter(LegacyStarter):
    """Starter for legacy dll instruments.

    """
    def format_connection_infos(self, infos):
        """Rename serial_number to instr_id.

        """
        i = infos.copy()
        i['instr_id'] = infos['serial_number']
        del i['serial_number']
        return i
