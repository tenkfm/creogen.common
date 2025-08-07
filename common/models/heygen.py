import math
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal

# Domain model for Heygen API responses

class HeygenAvatar(BaseModel):
    avatar_id: str
    avatar_name: str
    gender: str
    preview_image_url: str
    preview_video_url: str
    premium: bool

# API models

# Avatars
class HeygenAvatarsResponseData(BaseModel):
    avatars: List[HeygenAvatar]

class HeygenAvatarsResponse(BaseModel):
    data: HeygenAvatarsResponseData
    
    
# Voice

class HeygenVoice(BaseModel):
    """
    Описывает один голос из ответа HeyGen API /v2/voices.
    """
    voice_id: str
    language: str
    gender: Literal["Female", "Male", "unknown"]
    name: str
    preview_audio: HttpUrl
    support_pause: bool
    emotion_support: bool
    support_locale: bool


class HeygenVoicesResponse(BaseModel):
    """
    Модель ответа HeyGen API для GET https://api.heygen.com/v2/voices.

    Поля:
      - voices: список объектов HeygenVoice
    """
    voices: List[HeygenVoice]


# Video Generation
class HeygenVideoGenerationRequest(BaseModel):
    title: str
    avatar_id: str
    script: str
    background_type: Optional[str] = None # "image", "video", "color"
    background_value: Optional[str] = None # URL for image and video background or color value for color background
    width: int
    height: int

    def __init__(self, title: str, avatar_id: str, script: str, width: int, height: int):
        super().__init__(
            title=title,
            avatar_id=avatar_id,
            script=script,
            background_type=None,
            background_value=None,
            width=width,
            height=height
        )

    def payload(self) -> str:
        json = {
            "title": self.title,
            "caption": False,
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": self.avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": self.script,
                        "voice_id": "2f72ee82b83d4b00af16c4771d611752"
                    },
                    "background": {
                        "type": "color",
                        "value": "#00FF00",
                    }
                }
            ],
            "callback_id": None,
            "dimension": {
                "width": self.__round_up_to_next_even(self.width),
                "height": self.__round_up_to_next_even(self.height)
            }
        }

        return json
    
    def __round_up_to_next_even(self, n):
        return math.ceil(n / 2) * 2

class HeygenVideoGenerationData(BaseModel):
    video_id: str

class HeygenVideoGenerationResponse(BaseModel):
    data: HeygenVideoGenerationData



# Video Status
class HeygenVideoStatusError(BaseModel):
    code: str
    detail: str
    message: str

class HeygenVideoStatusData(BaseModel):
    callback_id: Optional[str] = None
    caption_url: Optional[str] = None
    created_at: int
    duration: Optional[float] = None
    error: Optional[HeygenVideoStatusError] = None
    gif_url: Optional[str] = None
    id: str
    status: str
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    video_url_caption: Optional[str] = None

class HeygenVideoStatusResponse(BaseModel):
    code: int
    data: HeygenVideoStatusData
    message: str
