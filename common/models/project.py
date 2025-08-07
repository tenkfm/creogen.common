from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict
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
    
    class Config:
        use_enum_values = True
    
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
    
    class Config:
        use_enum_values = True
    

class Reading(FirebaseObject):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    script_id: Optional[str] = None
    type: ReadingType
    info: ReadingAvatarInfo
    duration: Optional[float] = None
    status: ReadingStatus = ReadingStatus.new
    error: Optional[str] = None
    assets: Optional[List[Asset]] = None
    
    class Config:
        use_enum_values = True

    @staticmethod
    def collection_name():
        return "readings"
    
    
class PublicationPhase(str, Enum):
    new = "new"
    preparing_assets = "preparing_assets"
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


class PublicationCreativeStatus(str, Enum):
    new = "new"
    creating_subtitles = "creating_subtitles"
    generating = "generating"
    error = "error"
    done = "done"


class PublicationCreative(FirebaseObject):
    publication_id: Optional[str] = None
    user_id: Optional[str] = None
    status: PublicationCreativeStatus = PublicationCreativeStatus.new
    error: Optional[str] = None
    file_name: Optional[str]
    
    @staticmethod
    def collection_name():
        return "creatives"
    

class Publication(FirebaseObject):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    script_id: str
    ratio: PublicationRatio
    number_of_creos: int
    template: PublicationTemplate
    phase: PublicationPhase = PublicationPhase.new
    create_time: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    configuration: Optional[dict] = None
    assets: list[str] = Field(default_factory=list)
    readings: list[str] = Field(default_factory=list)

    task_id: Optional[str] = None
    error: Optional[str] = None
    zip_path: Optional[str] = None

    class Config:
        use_enum_values = True
        
    @property
    def width(self) -> int:
        return 720
    
    @property
    def height(self) -> int:
        return 1280 if self.ratio == PublicationRatio._9X16 else 720
    
    @property
    def is_ready_to_run(self) -> bool:
        if self.configuration and len(self.assets) > 0 and len(self.readings) > 0 and self.phase == PublicationPhase.new:
            return True
        return False
    
    def clone(self) -> "Publication":
        """
        Create a new instance of Publication with the same properties but reset phase and timestamps.
        """
        
        return Publication(
            user_id=self.user_id,
            project_id=self.project_id,
            script_id=self.script_id,
            ratio=self.ratio,
            number_of_creos=self.number_of_creos,
            template=self.template,
            phase=PublicationPhase.new,
            create_time=datetime.now().isoformat(),
            configuration=self.configuration,
            assets=self.assets,
            readings=self.readings
        )
        
    @staticmethod
    def collection_name():
        return "publications"
    
    
class PublicationStatus(BaseModel):
    publication_id: str
    publication_status: PublicationPhase
    creatives_ready: int
    creatives_total: int
    creatives_statuses: dict[str, PublicationCreativeStatus] = Field(default_factory=dict)
    progress: float
    
    @property
    def progress(self) -> Dict[str, float]:
        """
        Возвращает словарь вида {creative_id: progress},
        где progress рассчитывается по правилам:
          - new               → 0.0
          - preparing_assets  → 0.1
          - done, error       → 1.0
          - generating        → 0.1 + (ready/total)*0.9
        """
        total = self.creatives_total or 1  # чтобы не делить на ноль
        ready = self.creatives_ready

        progress_map: Dict[str, float] = {}
        for cid, status in self.creatives_statuses.items():
            if self.publication_status == PublicationPhase.new:
                p = 0.0

            elif self.publication_status == PublicationPhase.preparing_assets:
                p = 0.1

            elif self.publication_status in (PublicationPhase.done, PublicationPhase.error):
                p = 1.0

            elif self.publication_status == PublicationPhase.generating:
                # все креативы получают одинаковый прогресс в генерации
                p = 0.1 + (ready / total) * 0.9

            else:
                p = 0.0

            # гарантируем диапазон [0,1]
            progress_map[cid] = max(0.0, min(1.0, p))

        return progress_map