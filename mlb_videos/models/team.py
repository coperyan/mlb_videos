import os
import pandas as pd
import logging
import logging.config

import constants as Constants

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

class Team:
    def __init__(self, t: str = None):
        """Pass team abbreviation to class
        Grabs metadata from Team constants
        """
        self.abbreviation = t
        self.metadata = {}
        self.get_metadata()

    def get_metadata(self):
        """Filters down to values you want
        Calls out missing teams (if any)
        """
        self.metadata = (
            Constants.Team.Data.get(self.abbreviation,{})
        )
        if not self.metadata:
            raise Exception('Team not found..')

    def get_data(self):
        """Return dict
        """
        return self.metadata

    def get_df(self):
        """Return df
        """
        self.df = pd.DataFrame([self.metadata])
