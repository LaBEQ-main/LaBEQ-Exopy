# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Compatibility package providing HQCMeas tasks and drivers in Exopy.

"""


def list_manifests():
    """List the manifest that should be regsitered when the main Exopy app is
    started.

    """
    import enaml

    with enaml.imports():
        from .manifest import LaBEQManifest

    manifests = [LaBEQManifest]

    return manifests
