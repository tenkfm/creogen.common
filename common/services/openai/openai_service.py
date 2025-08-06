import asyncio
from openai import OpenAI
from common.services.openai.openai_service_interface import OpenaiServiceInterface

class OpenAIService(OpenaiServiceInterface):

    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    async def _prompt(self, system_prompt: str, user_prompt: str, temperature: float = 1.0):
        # Offload the synchronous call to a separate thread
        chat_completion = await asyncio.to_thread(
            self.client.chat.completions.create,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            model="deepseek-chat",
            response_format="text"
        )
        return chat_completion.choices[0].message.content



    async def translate_script(self, content: str, target_language: str) -> str:
        system = f"""
Translate the following text into {target_language} while preserving the original meaning and context.
Translate it like a native speaker would, ensuring that the translation is natural and fluent.
In the result write only the translated text without any additional comments or explanations.
"""

        result = await self._prompt(system, content)
        return result.strip()