from abc import ABC, abstractmethod

# Abstract base class for Firebase service
class OpenaiServiceInterface(ABC):
    @abstractmethod
    async def translate_script(self, content: str, target_language: str) -> str:
        pass