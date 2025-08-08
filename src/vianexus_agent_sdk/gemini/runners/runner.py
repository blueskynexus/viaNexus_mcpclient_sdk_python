import logging
from typing import Any, AsyncGenerator
from google.genai import types as genai_types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from vianexus_agent_sdk.gemini.agents.llm_agent import GeminiLLMAgent


class GeminiRunner(Runner):
    def __init__(self, agent: GeminiLLMAgent, user_id: str, app_name: str, session_id: str):
        self.user_id = user_id
        self.app_name = app_name
        self.agent = agent
        self.session_service = None
        self.runner = None
        self.session_id = session_id
    async def initialize(self):
        self.session_service = InMemorySessionService()
        await self.session_service.create_session(
            user_id=self.user_id,
            app_name=self.app_name,
            session_id=self.session_id,
        )
        super().__init__(
            app_name=self.app_name,
            agent=self.agent,
            session_service=self.session_service,
        )

    async def run_async(self, query: str) -> AsyncGenerator[Any, Any]:
        user_content = genai_types.Content(role='user', parts=[genai_types.Part(text=query)])
        async for event in super().run_async(user_id=self.user_id, session_id=self.session_id, new_message=user_content):
            logging.debug(f"Runner Event: {event}")
            if event.is_final_response() and event.content and event.content.parts and event.content.parts[0].text:
                yield event.content.parts