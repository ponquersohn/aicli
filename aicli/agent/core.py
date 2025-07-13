"""Core AI agent implementation using LangChain."""

from typing import Optional, Dict, Any, List
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.tools import Tool
from langchain import hub

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
        # Use a simpler ReAct agent with proper prompt format
        try:
            # Try to get ReAct prompt from hub
            prompt = hub.pull("hwchase17/react")
        except:
            # Fallback to manual prompt creation
            prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor without memory for now (to avoid conflicts)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.config.logging.level == "DEBUG",
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=5,
            max_execution_time=30,
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

You have access to the following tools:
{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (Thought/Action/Observation can repeat N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```

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