from requests import Session
from typing import Optional
from .base import BaseV1API
from ..raws.readarr import ReadarrRawAPI


class ReadarrAPI(BaseV1API):
    def __init__(self, url: str, apikey: str, session: Optional[Session] = None) -> None:
        super().__init__(ReadarrRawAPI(url, apikey, session=session))
