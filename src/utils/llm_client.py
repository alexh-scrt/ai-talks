"""Simple LLM client wrapper for progression control components"""

import os
from typing import Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


class LLMClient:
    """Simple LLM client for generating consequence tests and synthesis"""
    
    def __init__(self, model: Optional[str] = None, temperature: float = 0.7):
        """Initialize LLM client"""
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:32b")
        self.llm = ChatOllama(
            model=self.model,
            temperature=temperature
        )
    
    async def complete(self, prompt: str) -> str:
        """Complete a prompt and return the response text"""
        try:
            message = HumanMessage(content=prompt)
            response = await self.llm.ainvoke([message])
            return response.content
        except Exception as e:
            raise Exception(f"LLM completion failed: {e}")
    
    def complete_sync(self, prompt: str) -> str:
        """Synchronous completion for non-async contexts"""
        try:
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            raise Exception(f"LLM completion failed: {e}")