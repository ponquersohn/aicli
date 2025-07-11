"""Core AI agent implementation using LangChain."""

from typing import Optional, Dict, Any, List
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

from ..llm.factory import LLMFactory
from ..utils.config import Config
from ..tools.registry import ToolRegistry


class AIAgent:
    """Main AI agent for conversational code assistance."""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMFactory.create_llm(config.llm)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        self.tools = ToolRegistry.get_tools(config)
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent executor."""
        # Create system prompt
        system_prompt = self._create_system_prompt()
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create structured chat agent
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.config.logging.level == "DEBUG",
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=10,
            max_execution_time=60,
        )
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the AI agent."""
        return """You are AICLI, a helpful AI assistant for code development and analysis.

You are designed to help developers with:
- Code review and analysis
- Refactoring and optimization
- Bug fixes and debugging
- Writing new features
- Explaining complex code
- Project architecture advice
- Testing and documentation

Guidelines:
1. Always provide clear, actionable advice
2. Include code examples when helpful
3. Explain your reasoning
4. Ask clarifying questions when needed
5. Use available tools to examine files and run code
6. Be concise but thorough
7. Focus on best practices and clean code

Available tools allow you to:
- Read and analyze project files
- Execute Python code safely
- Run git commands
- Search through codebases
- Preview file changes

Always consider the project context and existing code patterns when making suggestions.
Prioritize security and maintainability in your recommendations."""
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a query with the AI agent."""
        try:
            # Prepare input with context if available
            input_data = {"input": query}
            if context:
                input_data.update(context)
            
            # Execute with agent
            result = self.agent_executor.invoke(input_data)
            
            # Extract the final answer
            if isinstance(result, dict) and "output" in result:
                return result["output"]
            else:
                return str(result)
                
        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    def add_context(self, context: str, context_type: str = "file"):
        """Add context information to the conversation memory."""
        context_message = f"[{context_type.upper()}] {context}"
        self.memory.chat_memory.add_user_message(context_message)
    
    def clear_memory(self):
        """Clear the conversation memory."""
        self.memory.clear()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        messages = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                messages.append({"role": "assistant", "content": message.content})
        return messages
    
    def save_session(self, session_name: str, session_dir: str):
        """Save the current session."""
        # TODO: Implement session saving
        pass
    
    def load_session(self, session_name: str, session_dir: str):
        """Load a previous session."""
        # TODO: Implement session loading
        pass