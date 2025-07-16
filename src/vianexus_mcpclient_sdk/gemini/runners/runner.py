import logging
from typing import Any
from google.genai import types as genai_types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from vianexus_mcpclient_sdk.gemini.agents.llm_agent import GeminiLLMAgent


class GeminiRunner(Runner):
    def __init__(self, agent: GeminiLLMAgent, name: str, session_id: str):
        self.name = name
        self.agent = agent
        self.session_service = None
        self.runner = None
        self.session_id = session_id
    async def initialize(self):
        self.session_service = InMemorySessionService()
        await self.session_service.create_session(
            user_id=self.name,
            app_name=self.name,
            session_id=self.session_id,
        )
        super().__init__(
            app_name=self.name,
            agent=self.agent,
            session_service=self.session_service,
        )

    async def run_async(self, query: str):
        user_content = genai_types.Content(role='user', parts=[genai_types.Part(text=query)])
        final_response_content = "No final response received."
        async for event in super().run_async(user_id=self.name, session_id=self.session_id, new_message=user_content):
            logging.debug(f"Event: {event}")
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text
        return final_response_content