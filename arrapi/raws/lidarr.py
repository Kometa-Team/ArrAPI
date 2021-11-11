from requests import Session
from typing import Optional
from .base import BaseRawV1API

class LidarrRawAPI(BaseRawV1API):
    def __init__(self, url: str, apikey: str, session: Optional[Session] = None) -> None:
        super().__init__(url, apikey, session=session)
