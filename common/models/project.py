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


class Asset(FirebaseObject):
    user_id: str = None
    project_id: str = None
    name: str
    type: AssetType
    
    @staticmethod
    def collection_name():
        return "assets"
    

class GenerationPhase(str, Enum):
    new = "new"
    generating_avatar = "generating_avatar"
    start_video_generating = "start_video_generating"
    subtitles_generating = "subtitles_generating"
    footages_creating = "footages_creating"
    video_rendering = "video_rendering"
    done = "done"


class GenAvatarPlatform(str, Enum):
    heygen = "heygen"


class GenAvatarInfo(BaseModel):
    platform: GenAvatarPlatform = GenAvatarPlatform.heygen
    avatar_id: str
    avatar_name: Optional[str] = None
    preview_image_url: Optional[str] = None
    avatar_video_id: Optional[str] = None


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
    title: str
    ratio: GenRatio
    template: GenTemplate
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    phase: GenerationPhase = GenerationPhase.new
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    avatar: Optional[GenAvatarInfo] = None
    script: Optional[str] = None
    configuration: Optional[dict] = None

    task_id: Optional[str] = None

    error: Optional[str] = None
    result: Optional[str] = None

    @staticmethod
    def collection_name():
        return "project_generations"