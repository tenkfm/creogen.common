from enum import Enum
from typing import Optional
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
    user_id: str = None
    project_id: str = None
    name: str
    path: str
    type: AssetType
    
    @staticmethod
    def collection_name():
        return "assets"
    
    
class Script(FirebaseObject):
    user_id: str
    project_id: str
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
    user_id: str
    project_id: str
    script: Script
    type: ReadingType
    info: Optional[ReadingAvatarInfo] = None
    status: ReadingStatus = ReadingStatus.new
    error: Optional[str] = None
    asset: Optional[Asset] = None
    
    @staticmethod
    def collection_name():
        return "readings"


class GenerationPhase(str, Enum):
    new = "new"
    start_video_generating = "start_video_generating"
    subtitles_generating = "subtitles_generating"
    footages_creating = "footages_creating"
    video_rendering = "video_rendering"
    done = "done"


class GenRatio(str, Enum):
    _9X16 = "9x16"
    _1x1 = "1x1"

    @property
    def width(self) -> int:
        return 720
    
    @property
    def height(self) -> int:
        return 1280 if self == GenRatio._9X16 else 720


class GenTemplate(str, Enum):
    frames_stepper = "frames_stepper"
    chroma_stepper = "chroma_stepper"


class ProjectGen(FirebaseObject):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    title: str
    ratio: GenRatio
    template: GenTemplate
    phase: GenerationPhase = GenerationPhase.new
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    script: Script
    configuration: Optional[dict] = None

    task_id: Optional[str] = None

    error: Optional[str] = None
    result: Optional[str] = None

    @staticmethod
    def collection_name():
        return "gens"