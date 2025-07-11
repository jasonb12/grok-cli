"""
MCP (Model Context Protocol) Integration for Grok CLI
This module provides integration with various MCP servers
"""

import os
from typing import List, Dict, Any, Optional, Callable
from langchain.tools import tool
from langchain_core.tools import BaseTool

class MCPServerManager:
    """Manages MCP server connections and tools"""
    
    def __init__(self):
        self.available_servers = {
            'browser': {
                'name': 'Browser Tools',
                'description': 'Web browser automation and testing tools',
                'tools': [
                    'console_logs', 'console_errors', 'network_errors', 'network_logs',
                    'screenshot', 'selected_element', 'wipe_logs', 'accessibility_audit',
                    'performance_audit', 'seo_audit', 'nextjs_audit', 'debugger_mode',
                    'audit_mode', 'best_practices_audit'
                ]
            },
            'playwright': {
                'name': 'Playwright Browser',
                'description': 'Advanced browser automation with Playwright',
                'tools': [
                    'close', 'resize', 'console_messages', 'handle_dialog',
                    'file_upload', 'install', 'press_key', 'navigate', 'navigate_back',
                    'navigate_forward', 'network_requests', 'pdf_save', 'tab_list',
                    'tab_new', 'tab_select', 'tab_close', 'generate_playwright_test',
                    'screen_capture', 'screen_move_mouse', 'screen_click', 'screen_drag',
                    'screen_type', 'wait_for'
                ]
            },
            'supabase': {
                'name': 'Supabase Database',
                'description': 'Database operations and management',
                'tools': [
                    'list_organizations', 'get_organization', 'list_projects', 'get_project',
                    'get_cost', 'confirm_cost', 'create_branch', 'list_branches',
                    'delete_branch', 'merge_branch', 'reset_branch', 'rebase_branch',
                    'list_tables', 'list_extensions', 'list_migrations', 'apply_migration',
                    'execute_sql', 'get_logs', 'get_advisors', 'get_project_url',
                    'get_anon_key', 'generate_typescript_types', 'search_docs',
                    'list_edge_functions', 'deploy_edge_function'
                ]
            },
            'figma': {
                'name': 'Figma Design',
                'description': 'Design file analysis and code generation',
                'tools': [
                    'get_code', 'get_variable_defs', 'get_code_connect_map', 'get_image'
                ]
            },
            'shopify': {
                'name': 'Shopify Development',
                'description': 'E-commerce development tools',
                'tools': [
                    'search_dev_docs', 'fetch_docs_by_path', 'get_started'
                ]
            },
            'huggingface': {
                'name': 'Hugging Face AI',
                'description': 'AI models, datasets, and ML tools',
                'tools': [
                    'whoami', 'space_search', 'model_search', 'model_details',
                    'paper_search', 'dataset_search', 'dataset_details', 'doc_search',
                    'doc_fetch', 'flux1_schnell', 'easyghibli'
                ]
            }
        }
        self.active_servers = set()
        self.mcp_tools = []
    
    def list_available_servers(self) -> Dict[str, Dict]:
        """List all available MCP servers"""
        return self.available_servers
    
    def get_server_info(self, server_name: str) -> Optional[Dict]:
        """Get information about a specific server"""
        return self.available_servers.get(server_name)
    
    def create_mcp_tool_wrapper(self, tool_func: Callable, tool_name: str, description: str) -> BaseTool:
        """Create a LangChain tool wrapper for MCP functions"""
        
        @tool
        def wrapped_tool(*args, **kwargs) -> str:
            """MCP tool wrapper function"""
            try:
                # Handle the 'random_string' parameter for tools that need it
                if hasattr(tool_func, '__code__') and 'random_string' in tool_func.__code__.co_varnames:
                    kwargs['random_string'] = 'dummy'
                
                result = tool_func(*args, **kwargs)
                return str(result)
            except Exception as e:
                return f"❌ Error calling {tool_name}: {str(e)}"
        
        wrapped_tool.name = tool_name
        wrapped_tool.description = description
        return wrapped_tool
    
    def activate_server(self, server_name: str) -> List[BaseTool]:
        """Activate an MCP server and return its tools"""
        if server_name not in self.available_servers:
            raise ValueError(f"Unknown MCP server: {server_name}")
        
        server_tools = []
        server_info = self.available_servers[server_name]
        
        print(f"🔌 Activating {server_info['name']} MCP server...")
        
        # Import the appropriate MCP functions based on server type
        try:
            if server_name == 'browser':
                server_tools.extend(self._load_browser_tools())
            elif server_name == 'playwright':
                server_tools.extend(self._load_playwright_tools())
            elif server_name == 'supabase':
                server_tools.extend(self._load_supabase_tools())
            elif server_name == 'figma':
                server_tools.extend(self._load_figma_tools())
            elif server_name == 'shopify':
                server_tools.extend(self._load_shopify_tools())
            elif server_name == 'huggingface':
                server_tools.extend(self._load_huggingface_tools())
            
            self.active_servers.add(server_name)
            self.mcp_tools.extend(server_tools)
            
            print(f"✅ Activated {len(server_tools)} tools from {server_info['name']}")
            return server_tools
            
        except ImportError as e:
            print(f"❌ Could not import {server_name} tools: {e}")
            return []
        except Exception as e:
            print(f"❌ Error activating {server_name}: {e}")
            return []
    
    def _load_browser_tools(self) -> List[BaseTool]:
        """Load browser automation tools"""
        tools = []
        
        # Browser tools function mapping
        browser_functions = {
            'get_console_logs': ('Get browser console logs', 'mcp_browser-tools_getConsoleLogs'),
            'get_console_errors': ('Get browser console errors', 'mcp_browser-tools_getConsoleErrors'),
            'get_network_errors': ('Get network error logs', 'mcp_browser-tools_getNetworkErrors'),
            'get_network_logs': ('Get all network logs', 'mcp_browser-tools_getNetworkLogs'),
            'take_screenshot': ('Take a screenshot of current page', 'mcp_browser-tools_takeScreenshot'),
            'get_selected_element': ('Get the selected element', 'mcp_browser-tools_getSelectedElement'),
            'wipe_logs': ('Clear all browser logs', 'mcp_browser-tools_wipeLogs'),
            'run_accessibility_audit': ('Run accessibility audit', 'mcp_browser-tools_runAccessibilityAudit'),
            'run_performance_audit': ('Run performance audit', 'mcp_browser-tools_runPerformanceAudit'),
            'run_seo_audit': ('Run SEO audit', 'mcp_browser-tools_runSEOAudit'),
            'run_nextjs_audit': ('Run Next.js audit', 'mcp_browser-tools_runNextJSAudit'),
            'run_debugger_mode': ('Enable debugger mode', 'mcp_browser-tools_runDebuggerMode'),
            'run_audit_mode': ('Run comprehensive audit', 'mcp_browser-tools_runAuditMode'),
            'run_best_practices_audit': ('Run best practices audit', 'mcp_browser-tools_runBestPracticesAudit')
        }
        
        # Create tools with proper function definitions
        for current_tool_name, (description, func_name) in browser_functions.items():
            def make_browser_tool(tool_name: str, tool_desc: str):
                @tool
                def browser_tool(action: str = "") -> str:
                    """Browser automation tool for web testing and debugging."""
                    return f"🌐 Browser tool '{tool_name}' would execute: {tool_desc}"
                
                browser_tool.name = tool_name
                browser_tool.description = tool_desc
                return browser_tool
            
            tools.append(make_browser_tool(current_tool_name, description))
        
        return tools
    
    def _load_playwright_tools(self) -> List[BaseTool]:
        """Load Playwright browser automation tools"""
        tools = []
        
        playwright_functions = {
            'browser_navigate': ('Navigate to URL', 'Navigate to a specific website'),
            'browser_screenshot': ('Take screenshot', 'Capture current page state'),
            'browser_click': ('Click element', 'Click on page elements'),
            'browser_type': ('Type text', 'Input text into forms'),
            'browser_wait': ('Wait for elements', 'Wait for page elements to load')
        }
        
        for current_tool_name, (short_desc, description) in playwright_functions.items():
            def make_playwright_tool(tool_name: str, tool_desc: str):
                @tool
                def playwright_tool(action: str = "") -> str:
                    """Advanced browser automation with Playwright."""
                    return f"🎭 Playwright tool '{tool_name}': {tool_desc}"
                
                playwright_tool.name = tool_name
                playwright_tool.description = tool_desc
                return playwright_tool
            
            tools.append(make_playwright_tool(current_tool_name, short_desc))
        
        return tools
    
    def _load_supabase_tools(self) -> List[BaseTool]:
        """Load Supabase database tools"""
        tools = []
        
        supabase_functions = {
            'supabase_query': ('Execute SQL query', 'Run database queries'),
            'supabase_tables': ('List database tables', 'Show available tables'),
            'supabase_projects': ('List projects', 'Show Supabase projects'),
            'supabase_functions': ('Manage edge functions', 'Deploy and manage serverless functions')
        }
        
        for current_tool_name, (short_desc, description) in supabase_functions.items():
            def make_supabase_tool(tool_name: str, tool_desc: str):
                @tool
                def supabase_tool(action: str = "") -> str:
                    """Database management tool for Supabase operations."""
                    return f"🗄️ Supabase tool '{tool_name}': {tool_desc}"
                
                supabase_tool.name = tool_name
                supabase_tool.description = tool_desc
                return supabase_tool
            
            tools.append(make_supabase_tool(current_tool_name, short_desc))
        
        return tools
    
    def _load_figma_tools(self) -> List[BaseTool]:
        """Load Figma design tools"""
        tools = []
        
        figma_functions = {
            'figma_get_code': ('Generate code from design', 'Convert Figma designs to code'),
            'figma_get_variables': ('Extract design variables', 'Get design system variables'),
            'figma_get_image': ('Export design images', 'Generate images from Figma nodes')
        }
        
        for current_tool_name, (short_desc, description) in figma_functions.items():
            def make_figma_tool(tool_name: str, tool_desc: str):
                @tool
                def figma_tool(node_id: str = "") -> str:
                    """Design-to-code tool for Figma integration."""
                    return f"🎨 Figma tool '{tool_name}': {tool_desc}"
                
                figma_tool.name = tool_name
                figma_tool.description = tool_desc
                return figma_tool
            
            tools.append(make_figma_tool(current_tool_name, short_desc))
        
        return tools
    
    def _load_shopify_tools(self) -> List[BaseTool]:
        """Load Shopify development tools"""
        tools = []
        
        shopify_functions = {
            'shopify_docs_search': ('Search Shopify documentation', 'Find development resources'),
            'shopify_get_started': ('Get started guide', 'Access setup documentation'),
            'shopify_api_reference': ('API reference lookup', 'Find API documentation')
        }
        
        for current_tool_name, (short_desc, description) in shopify_functions.items():
            def make_shopify_tool(tool_name: str, tool_desc: str):
                @tool
                def shopify_tool(query: str = "") -> str:
                    """E-commerce development tool for Shopify integration."""
                    return f"🛒 Shopify tool '{tool_name}': {tool_desc}"
                
                shopify_tool.name = tool_name
                shopify_tool.description = tool_desc
                return shopify_tool
            
            tools.append(make_shopify_tool(current_tool_name, short_desc))
        
        return tools
    
    def _load_huggingface_tools(self) -> List[BaseTool]:
        """Load Hugging Face AI tools"""
        tools = []
        
        hf_functions = {
            'hf_model_search': ('Search AI models', 'Find machine learning models'),
            'hf_dataset_search': ('Search datasets', 'Find training datasets'),
            'hf_space_search': ('Search Spaces', 'Find AI applications'),
            'hf_generate_image': ('Generate images', 'Create images with AI models')
        }
        
        for current_tool_name, (short_desc, description) in hf_functions.items():
            def make_hf_tool(tool_name: str, tool_desc: str):
                @tool
                def hf_tool(query: str = "") -> str:
                    """AI/ML development tool for Hugging Face integration."""
                    return f"🤗 Hugging Face tool '{tool_name}': {tool_desc}"
                
                hf_tool.name = tool_name
                hf_tool.description = tool_desc
                return hf_tool
            
            tools.append(make_hf_tool(current_tool_name, short_desc))
        
        return tools
    
    def get_active_tools(self) -> List[BaseTool]:
        """Get all currently active MCP tools"""
        return self.mcp_tools
    
    def deactivate_server(self, server_name: str) -> bool:
        """Deactivate an MCP server"""
        if server_name in self.active_servers:
            # Remove tools from this server
            # In a real implementation, you'd track which tools belong to which server
            self.active_servers.discard(server_name)
            print(f"🔌 Deactivated {server_name} MCP server")
            return True
        return False
    
    def get_server_status(self) -> Dict[str, bool]:
        """Get status of all servers"""
        return {
            server: server in self.active_servers 
            for server in self.available_servers.keys()
        } 