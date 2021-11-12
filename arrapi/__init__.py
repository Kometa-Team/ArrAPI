import pkg_resources

from .exceptions import ArrException, ConnectionFailure, Excluded, Exists, Invalid, NotFound, Unauthorized
from .objs.simple import MetadataProfile, RemotePathMapping, RootFolder, UnmappedFolder, Season
from .objs.reload import QualityProfile, LanguageProfile, SystemStatus, Tag, Movie, Series
from .apis.sonarr import SonarrAPI
from .apis.radarr import RadarrAPI
from .apis.lidarr import LidarrAPI
from .apis.readarr import ReadarrAPI

try:
    __version__ = pkg_resources.get_distribution("arrapi").version
except pkg_resources.DistributionNotFound:
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
    "Excluded",
    "Exists",
    "Invalid",
    "NotFound",
    "Unauthorized"
]
