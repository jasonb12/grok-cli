from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from composio_langchain import ComposioToolSet, App
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GrokAgent:
    def __init__(self, api_key=None, model=None, base_url=None, temperature=None, max_tokens=None, verbose=None):
        # Load from .env file if parameters not provided
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        self.model = model or os.getenv("GROK_MODEL", "grok-4-0709")
        self.base_url = base_url or os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
        self.temperature = float(temperature or os.getenv("GROK_TEMPERATURE", "0.7"))
        self.max_tokens = int(max_tokens or os.getenv("GROK_MAX_TOKENS", "1000"))
        self.verbose = verbose if verbose is not None else os.getenv("GROK_VERBOSE", "False").lower() == "true"
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY must be provided either as parameter or in .env file")
        
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        self.composio_toolset = ComposioToolSet()
        
        # Start with basic tools that are known to work
        self.tools = self.composio_toolset.get_tools(apps=[
            App.FILETOOL,      # File operations (read, write, create, delete)
            App.SHELLTOOL,     # Shell/terminal commands
            # Note: SYSTEMTOOL removed due to compatibility issues
            # Add more apps as needed and tested:
            # App.WEBTOOL,     # Web scraping and HTTP requests
            # App.SEARCHTOOL,  # Search capabilities
            # App.GITHUBTOOL,  # GitHub operations
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with access to powerful tools including:
            - File operations (read, write, create, delete files and directories)
            - Shell commands (execute terminal commands)
            
            Use these tools appropriately to help the user with their requests. 
            Always explain what you're doing and ask for confirmation before making destructive changes.
            
            For system information, you can use shell commands like:
            - 'uname -a' for system info
            - 'ps aux' for process information
            - 'df -h' for disk usage
            - 'free -h' for memory usage (Linux) or 'vm_stat' (macOS)
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.verbose,  
            max_iterations=10
        )
    
    def chat(self, user_message):
        """Chat with the agent using LangChain's built-in tool calling"""
        try:
            response = self.agent_executor.invoke({"input": user_message})
            output = response.get("output", "Sorry, I couldn't generate a response.")
            print(output)  
            return output
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                error_msg = "Rate limit exceeded. Please try again later."
                print(error_msg)
                return error_msg
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            return error_msg
    
    def list_available_tools(self):
        """List all available tools"""
        print("Available tools:")
        for tool in self.tools:
            print(f"- {tool.name}: {tool.description}")
        return self.tools
    
    def get_config(self):
        """Get current configuration"""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "verbose": self.verbose,
            "api_key_set": bool(self.api_key)
        }
    
    def add_tool(self, app_name):
        """Add a new tool/app to the agent"""
        try:
            app = getattr(App, app_name)
            new_tools = self.composio_toolset.get_tools(apps=[app])
            self.tools.extend(new_tools)
            print(f"✅ Added {app_name} successfully")
            return True
        except Exception as e:
            print(f"❌ Error adding {app_name}: {e}")
            return False