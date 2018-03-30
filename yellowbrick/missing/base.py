# yellowbrick.missing.base
# Base Visualizer for missing values
#
# Author:  Nathan Danielsen <nathan.danielsen@gmail.com>
# Created: Fri Mar 29 5:17:36 2018 -0500
#
# Copyright (C) 2018 District Data Labs
# For license information, see LICENSE.txt
#
# ID: base.py [] nathan.danielsen@gmail.com.com $

"""
Base classes for missing values visualizers and related tools.
"""

##########################################################################
## Imports
##########################################################################

from yellowbrick.features.base import DataVisualizer

##########################################################################
## Feature Visualizers
##########################################################################

class MissingDataVisualizer(DataVisualizer):
    """
    """

    def __init__(self, ax=None, features=None, classes=None, color=None,
                 colormap=None, **kwargs):
        """
        Initialize the data visualization with many of the options required
        in order to make most visualizations work.
        """
        super(MissingDataVisualizer, self).__init__(ax=ax, features=features, **kwargs)
