"""
Enhanced Grok Agent with advanced filesystem capabilities
"""

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from composio_langchain import ComposioToolSet, App
import os
from dotenv import load_dotenv

# Import custom filesystem tools
from .filesystem_tools import (
    advanced_file_info,
    safe_file_operations,
    directory_tree,
    find_files_advanced,
    monitor_directory_changes
)

# Load environment variables from .env file
load_dotenv()

class EnhancedGrokAgent:
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
        
        # Get Composio tools
        self.composio_tools = self.composio_toolset.get_tools(apps=[
            App.FILETOOL,      # File operations
            App.SHELLTOOL,     # Shell commands
        ])
        
        # Add custom filesystem tools
        self.custom_tools = [
            advanced_file_info,
            safe_file_operations,
            directory_tree,
            find_files_advanced,
            monitor_directory_changes
        ]
        
        # Combine all tools
        self.tools = self.composio_tools + self.custom_tools
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced AI assistant with comprehensive filesystem access including:
            
            **Standard Tools:**
            - File operations (read, write, create, delete, edit, rename)
            - Shell commands (execute terminal commands)
            - Git operations (clone, patch, custom commands)
            
            **Enhanced Filesystem Tools:**
            - advanced_file_info: Get detailed file/directory information with permissions, dates, sizes
            - safe_file_operations: Perform safe copy, move, backup operations with timestamps
            - directory_tree: Generate visual tree structures of directories
            - find_files_advanced: Advanced file search with size filtering and pattern matching
            - monitor_directory_changes: Monitor directory changes over time
            
            **Usage Guidelines:**
            - Always explain what you're doing before performing operations
            - Use safe operations when possible (backup before destructive changes)
            - Provide detailed information when requested
            - Ask for confirmation before destructive operations
            - Use appropriate tools for the task (enhanced tools for advanced operations)
            
            **For system information, use shell commands like:**
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
        """Chat with the enhanced agent"""
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
        """List all available tools with categories"""
        print("Available Tools:")
        print("=" * 60)
        
        print("\n🔧 **Composio Tools:**")
        for tool in self.composio_tools:
            print(f"  • {tool.name}")
        
        print(f"\n✨ **Enhanced Filesystem Tools:**")
        for tool in self.custom_tools:
            print(f"  • {tool.name}: {tool.description}")
        
        print(f"\n📊 **Total Tools:** {len(self.tools)}")
        return self.tools
    
    def get_config(self):
        """Get current configuration"""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "verbose": self.verbose,
            "api_key_set": bool(self.api_key),
            "total_tools": len(self.tools),
            "custom_tools": len(self.custom_tools),
            "composio_tools": len(self.composio_tools)
        }
    
    def add_tool(self, app_name):
        """Add a new Composio tool/app to the agent"""
        try:
            app = getattr(App, app_name)
            new_tools = self.composio_toolset.get_tools(apps=[app])
            self.composio_tools.extend(new_tools)
            self.tools = self.composio_tools + self.custom_tools
            print(f"✅ Added {app_name} successfully ({len(new_tools)} tools)")
            return True
        except Exception as e:
            print(f"❌ Error adding {app_name}: {e}")
            return False
    
    def demonstrate_filesystem_features(self):
        """Demonstrate the enhanced filesystem capabilities"""
        demo_commands = [
            "Show me detailed information about this directory using advanced_file_info",
            "Create a visual tree of this project directory",
            "Find all Python files larger than 1KB in this directory",
            "Backup the .env file safely"
        ]
        
        print("🚀 **Enhanced Filesystem Demo**")
        print("=" * 60)
        print("Try these commands:")
        for i, cmd in enumerate(demo_commands, 1):
            print(f"{i}. {cmd}")
        print("\nOr ask me to help with any filesystem operation!")
        
        return demo_commands 