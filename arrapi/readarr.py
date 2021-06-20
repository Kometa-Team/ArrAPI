from arrapi import util
from typing import Optional, Union, List, Tuple
from .api import BaseV1API
from .exceptions import NotFound, Invalid, Exists
from .objs import Movie, RootFolder, QualityProfile, Tag


class ReadarrAPI(BaseV1API):
    """ Primary Class to use when connecting with the Readarr API

        Parameters:
            url (str): URL of Readarr application.
            apikey (str) apikey for the Readarr application.
     """

    def __init__(self, url: str, apikey: str) -> None:
        super().__init__(url, apikey)
