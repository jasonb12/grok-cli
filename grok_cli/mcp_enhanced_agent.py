"""
MCP-Enhanced Grok Agent
Combines Composio tools, custom filesystem tools, and MCP servers
"""

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from composio_langchain import ComposioToolSet, App
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Import custom filesystem tools
from .filesystem_tools import (
    advanced_file_info,
    safe_file_operations,
    directory_tree,
    find_files_advanced,
    monitor_directory_changes
)

# Import MCP integration
from .mcp_integration import MCPServerManager

# Load environment variables from .env file
load_dotenv()

class MCPEnhancedGrokAgent:
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
        
        # Initialize tool managers
        self.composio_toolset = ComposioToolSet()
        self.mcp_manager = MCPServerManager()
        
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
        
        # MCP tools (initially empty)
        self.mcp_tools = []
        
        # Combine all tools
        self._rebuild_tools()
        
        # Initialize agent
        self._initialize_agent()
    
    def _rebuild_tools(self):
        """Rebuild the complete tools list"""
        self.tools = self.composio_tools + self.custom_tools + self.mcp_tools
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with current tools"""
        # Build capability description for system prompt
        capabilities = []
        
        if self.composio_tools:
            capabilities.append("**File & Shell Operations**: Complete filesystem access and shell command execution")
        
        if self.custom_tools:
            capabilities.append("**Enhanced Filesystem**: Advanced file analysis, visual trees, and safe operations")
        
        if self.mcp_tools:
            active_servers = self.mcp_manager.get_server_status()
            active_list = [server for server, active in active_servers.items() if active]
            if active_list:
                capabilities.append(f"**MCP Servers**: {', '.join(active_list)} for specialized operations")
        
        capabilities_text = "\n            - ".join(capabilities) if capabilities else "Basic filesystem operations"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an advanced AI assistant with comprehensive capabilities including:
            - {capabilities_text}
            
            **Tool Categories:**
            
            **Composio Tools** (File & Shell):
            - Complete file operations (read, write, edit, create, delete)
            - Directory navigation and management
            - Shell command execution
            - Git operations and version control
            
            **Custom Filesystem Tools**:
            - advanced_file_info: Detailed file/directory analysis with permissions and metadata
            - safe_file_operations: Safe copy, move, backup with timestamps
            - directory_tree: Visual directory structures with icons
            - find_files_advanced: Advanced search with pattern matching and size filters
            - monitor_directory_changes: Directory monitoring and change tracking
            
            **MCP Server Tools** (when activated):
            - Browser automation and testing (Browser/Playwright servers)
            - Database operations and management (Supabase server)
            - Design-to-code conversion (Figma server)
            - E-commerce development (Shopify server)
            - AI/ML models and datasets (Hugging Face server)
            
            **Usage Guidelines:**
            - Always explain what you're doing before performing operations
            - Use the most appropriate tool for each task
            - Confirm before destructive operations
            - Provide detailed feedback on operations
            - Leverage MCP servers for specialized tasks when available
            
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
            max_iterations=15  # Increased for complex MCP operations
        )
    
    def chat(self, user_message):
        """Chat with the MCP-enhanced agent"""
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
    
    def activate_mcp_server(self, server_name: str) -> bool:
        """Activate an MCP server and integrate its tools"""
        try:
            new_tools = self.mcp_manager.activate_server(server_name)
            if new_tools:
                self.mcp_tools.extend(new_tools)
                self._rebuild_tools()
                self._initialize_agent()  # Reinitialize with new tools
                return True
            return False
        except Exception as e:
            print(f"❌ Error activating MCP server {server_name}: {e}")
            return False
    
    def deactivate_mcp_server(self, server_name: str) -> bool:
        """Deactivate an MCP server and remove its tools"""
        try:
            if self.mcp_manager.deactivate_server(server_name):
                # Rebuild MCP tools list (removing deactivated server's tools)
                self.mcp_tools = self.mcp_manager.get_active_tools()
                self._rebuild_tools()
                self._initialize_agent()  # Reinitialize without deactivated tools
                return True
            return False
        except Exception as e:
            print(f"❌ Error deactivating MCP server {server_name}: {e}")
            return False
    
    def list_available_mcp_servers(self) -> Dict[str, Dict]:
        """List all available MCP servers"""
        return self.mcp_manager.list_available_servers()
    
    def get_mcp_server_status(self) -> Dict[str, bool]:
        """Get status of all MCP servers"""
        return self.mcp_manager.get_server_status()
    
    def list_available_tools(self):
        """List all available tools with categories"""
        print("🛠️  **Available Tools by Category**")
        print("=" * 70)
        
        # Composio Tools
        print(f"\n🔧 **Composio Tools** ({len(self.composio_tools)}):")
        for tool in self.composio_tools[:5]:  # Show first 5
            print(f"  • {tool.name}")
        if len(self.composio_tools) > 5:
            print(f"  • ... and {len(self.composio_tools) - 5} more")
        
        # Custom Filesystem Tools
        print(f"\n✨ **Enhanced Filesystem Tools** ({len(self.custom_tools)}):")
        for tool in self.custom_tools:
            print(f"  • {tool.name}: {tool.description}")
        
        # MCP Tools
        if self.mcp_tools:
            print(f"\n🔌 **MCP Tools** ({len(self.mcp_tools)}):")
            active_servers = self.get_mcp_server_status()
            for server, active in active_servers.items():
                if active:
                    server_info = self.mcp_manager.get_server_info(server)
                    print(f"  📡 {server_info['name']}: {server_info['description']}")
        else:
            print(f"\n🔌 **MCP Tools**: None active")
            print("  💡 Use activate_mcp_server() to add MCP capabilities")
        
        print(f"\n📊 **Total Tools**: {len(self.tools)}")
        return self.tools
    
    def get_config(self):
        """Get current configuration including MCP server status"""
        mcp_status = self.get_mcp_server_status()
        active_servers = [server for server, active in mcp_status.items() if active]
        
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "verbose": self.verbose,
            "api_key_set": bool(self.api_key),
            "total_tools": len(self.tools),
            "composio_tools": len(self.composio_tools),
            "custom_tools": len(self.custom_tools),
            "mcp_tools": len(self.mcp_tools),
            "active_mcp_servers": active_servers,
            "available_mcp_servers": list(self.mcp_manager.available_servers.keys())
        }
    
    def add_composio_tool(self, app_name):
        """Add a new Composio tool/app to the agent"""
        try:
            app = getattr(App, app_name)
            new_tools = self.composio_toolset.get_tools(apps=[app])
            self.composio_tools.extend(new_tools)
            self._rebuild_tools()
            self._initialize_agent()
            print(f"✅ Added Composio {app_name} successfully ({len(new_tools)} tools)")
            return True
        except Exception as e:
            print(f"❌ Error adding Composio {app_name}: {e}")
            return False
    
    def demonstrate_mcp_capabilities(self):
        """Demonstrate MCP server capabilities"""
        print("🚀 **MCP Server Capabilities**")
        print("=" * 60)
        
        servers = self.list_available_mcp_servers()
        for server_name, server_info in servers.items():
            status = "🟢 Active" if server_name in self.mcp_manager.active_servers else "⚪ Available"
            print(f"\n{status} **{server_info['name']}**")
            print(f"   {server_info['description']}")
            print(f"   Tools: {len(server_info['tools'])}")
            
            # Show example usage
            examples = self._get_server_examples(server_name)
            if examples:
                print("   Examples:")
                for example in examples[:2]:  # Show first 2 examples
                    print(f"     • {example}")
        
        print(f"\n💡 **To activate an MCP server:**")
        print(f"   agent.activate_mcp_server('server_name')")
        print(f"   agent.chat('Use the new capabilities!')")
    
    def _get_server_examples(self, server_name: str) -> List[str]:
        """Get example usage for each server"""
        examples = {
            'browser': [
                "Take a screenshot of the current webpage",
                "Run an accessibility audit on the site",
                "Check console errors and network logs"
            ],
            'playwright': [
                "Navigate to a website and click a button",
                "Fill out a form and submit it",
                "Generate a Playwright test script"
            ],
            'supabase': [
                "List my Supabase projects",
                "Execute a SQL query on my database",
                "Deploy an edge function"
            ],
            'figma': [
                "Generate React code from a Figma design",
                "Extract design variables from Figma",
                "Export an image from a Figma node"
            ],
            'shopify': [
                "Search Shopify documentation for API info",
                "Get started with Shopify app development",
                "Find examples for checkout customization"
            ],
            'huggingface': [
                "Search for image generation models",
                "Find datasets for machine learning",
                "Generate an image using Flux model"
            ]
        }
        return examples.get(server_name, []) 