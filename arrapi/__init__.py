import os, pkg_resources

from .exceptions import ArrException, ConnectionFailure, Exists, Invalid, NotFound, Unauthorized
from .objs import QualityProfile, LanguageProfile, MetadataProfile, RemotePathMapping, RootFolder, UnmappedFolder, SystemStatus, Tag, Movie, Series, Season
from .sonarr import SonarrAPI
from .radarr import RadarrAPI
from .lidarr import LidarrAPI
from .readarr import ReadarrAPI

try:
    __version__ = pkg_resources.get_distribution("arrapi").version
except pkg_resources.DistributionNotFound:
    if os.path.exists("../VERSION"):
        with open("../VERSION") as handle:
            for line in handle.readlines():
                line = line.strip()
                if len(line) > 0:
                    __version__ = line
                    break
    else:
        __version__ = ""
__author__ = "Nathan Taggart"
__credits__ = "meisnate12"
__package_name__ = "arrapi"
__project_name__ = "ArrAPI"
__description__ = "Python wrapper for Radarr and Sonarr APIs:"
__url__ = "https://github.com/meisnate12/ArrAPI"
__email__ = 'meisnate12@gmail.com'
__license__ = 'MIT License'
__all__ = [
    "RadarrAPI",
    "SonarrAPI",
    "QualityProfile",
    "LanguageProfile",
    "MetadataProfile",
    "RemotePathMapping",
    "RootFolder",
    "UnmappedFolder",
    "SystemStatus",
    "Tag",
    "Movie",
    "Series",
    "Season",
    "ArrException",
    "ConnectionFailure",
    "Exists",
    "Invalid",
    "NotFound",
    "Unauthorized"
]
