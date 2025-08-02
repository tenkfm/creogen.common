from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from common.services.firebase.firebase_object import FirebaseObject

class Project(FirebaseObject):
    user_id: Optional[str] = None
    name: str
    dir: Optional[str] = None

    @staticmethod
    def collection_name():
        return "projects"


class AssetType(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"
    video_reading = "video_reading"
    audio_reading = "audio_reading"


class Asset(FirebaseObject):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    name: str
    path: str
    type: AssetType
    
    @staticmethod
    def collection_name():
        return "assets"
    
    
class Script(FirebaseObject):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    name: str
    language: str
    content: str
    
    @staticmethod
    def collection_name():
        return "scripts"
    

class ReadingType(str, Enum):
    voice = "voice"
    video = "video"


class ReadingStatus(str, Enum):
    new = "new"
    generating = "generating"
    postprocessing = "postprocessing"
    done = "done"
    error = "error"
    

class ReadingAvatarPlatform(str, Enum):
    heygen = "heygen"


class ReadingAvatarInfo(BaseModel):
    platform: ReadingAvatarPlatform = ReadingAvatarPlatform.heygen
    avatar_id: str
    avatar_name: Optional[str] = None
    preview_image_url: Optional[str] = None
    avatar_video_id: Optional[str] = None

    
class Reading(FirebaseObject):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    script_id: Optional[str] = None
    type: ReadingType
    info: ReadingAvatarInfo
    duration: Optional[int] = None
    status: ReadingStatus = ReadingStatus.new
    error: Optional[str] = None
    assets: Optional[List[Asset]] = None

    @staticmethod
    def collection_name():
        return "readings"
    
    
class PublicationPhase(str, Enum):
    new = "new"
    preparing_assets = "preparing_assets"
    creating_subtitles = "creating_subtitles"
    generating = "generating"
    done = "done"
    error = "error"


class PublicationRatio(str, Enum):
    _9X16 = "9x16"
    _1x1 = "1x1"

    @property
    def width(self) -> int:
        return 720
    
    @property
    def height(self) -> int:
        return 1280 if self == PublicationRatio._9X16 else 720


class PublicationTemplate(str, Enum):
    frames_stepper = "frames_stepper"


class Publication(FirebaseObject):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    script_id: str
    ratio: PublicationRatio
    template: PublicationTemplate
    phase: PublicationPhase = PublicationPhase.new
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    configuration: Optional[dict] = None
    assets: list[str] = Field(default_factory=list)
    readings: list[str] = Field(default_factory=list)

    task_id: Optional[str] = None

    error: Optional[str] = None
    result: Optional[str] = None

    @staticmethod
    def collection_name():
        return "publications"