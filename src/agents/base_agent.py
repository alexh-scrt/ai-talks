from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import os
from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from ..utils.text_processing import strip_reasoning

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents with tool calling capabilities"""
    
    def __init__(
        self, 
        agent_id: str, 
        web_search: bool = True, 
        model: Optional[str] = None, 
        session_id: Optional[str] = None, 
        llm_params: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.model = model or os.getenv(f'{self.agent_id.upper()}_MODEL') or os.getenv("OLLAMA_MODEL", "qwen3:32b")
        if not self.model:
            raise ValueError(f"Model not specified for agent {self.agent_id}")
        
        self.conversation_history = []
        self.session_id = session_id
        
        # Track tool usage
        self._last_tool_calls = []  # Store tool call history
        self._tools_used_this_turn = False  # Flag for current turn
        
        # Setup LLM parameters
        default_params = {
            "model": self.model,
            "temperature": 0.7
        }
        if llm_params:
            default_params.update(llm_params)
        
        self.llm = ChatOllama(**default_params)
        
        # Setup tools if needed
        self.tools = [] if not web_search else self._setup_tools()
        
        # Bind tools to LLM if available
        if self.tools:
            self.llm = self.llm.bind_tools(self.tools)

    def _setup_tools(self) -> List[BaseTool]:
        """Setup tools for the agent"""
        tools = []
        
        # Add web search tool for research
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if tavily_api_key:
            try:
                tavily_tool = TavilySearchResults(
                    api_key=tavily_api_key,
                    max_results=5,
                    include_answer=True,
                    include_raw_content=False,
                    include_images=False,
                    search_depth="basic",
                    include_domains=[],
                    exclude_domains=[],
                )
                tools.append(tavily_tool)
                logger.info(f"✅ Tavily search tool added for {self.agent_id}")
            except Exception as e:
                logger.error(f"❌ Failed to setup Tavily for {self.agent_id}: {e}")
        else:
            logger.warning(f"⚠️ TAVILY_API_KEY not set - web search disabled for {self.agent_id}")
                
        return tools
        
    @abstractmethod
    async def process(self, prompt: str, context: Optional[str] = None) -> str:
        """Process input and generate response - to be implemented by subclasses"""
        pass

    async def add_to_history(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add message to conversation history"""
        entry = {
            "role": role,
            "content": content
        }
        if metadata:
            entry["metadata"] = metadata
            
        self.conversation_history.append(entry)
    
    def get_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history
    
    async def get_recent_context(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation turns"""
        return self.conversation_history[-n:]
    
    async def generate_with_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using the LLM"""
        
        # Reset tool usage tracking for this turn
        self._last_tool_calls = []
        self._tools_used_this_turn = False
        
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = await self.llm.ainvoke(messages)
        
        # Handle tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            self._last_tool_calls = response.tool_calls  # Track calls
            self._tools_used_this_turn = True  # Set flag
            
            # Process tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                # Find and execute the tool
                for tool in self.tools:
                    if tool.name == tool_name:
                        try:
                            result = await tool.ainvoke(tool_args)
                            tool_results.append(result)
                            logger.info(f"🔍 {self.agent_id} used {tool_name}")
                        except Exception as e:
                            logger.error(f"Tool execution failed: {e}")
                            tool_results.append(f"Tool error: {str(e)}")
            
            # If we have tool results, generate a final response incorporating them
            if tool_results:
                messages.append(response)
                tool_message = f"Tool results: {tool_results}"
                messages.append(HumanMessage(content=tool_message))
                final_response = await self.llm.ainvoke(messages)
                # Apply basic cleaning to remove reasoning blocks
                return strip_reasoning(final_response.content)
        
        # Apply basic cleaning to remove reasoning blocks
        return strip_reasoning(response.content)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def __str__(self):
        return f"{self.__class__.__name__}(id={self.agent_id}, model={self.model})"