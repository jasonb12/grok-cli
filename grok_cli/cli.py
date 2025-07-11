#!/usr/bin/env python3
"""
Command-line interface for Grok CLI with comprehensive development support
Combines MCP server integration with project-aware development features
"""

import click
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

@click.group()
@click.version_option()
def cli():
    """🚀 Grok CLI - AI Assistant for Development & MCP Integration
    
    A powerful command-line AI assistant that combines:
    • Project-aware development (like Claude Code)
    • MCP (Model Context Protocol) server integration
    • Enhanced filesystem operations
    • Git integration and merge conflict resolution
    """
    pass

@cli.command()
@click.option('--project-path', type=click.Path(exists=True), help='Path to project directory (defaults to current)')
@click.option('--config', type=click.Path(), help='Path to .env configuration file')
@click.option('--temperature', type=float, help='Model temperature (0.0-2.0)')
@click.option('--max-tokens', type=int, help='Maximum tokens in response')
@click.option('--verbose', is_flag=True, help='Enable verbose mode')
def dev(project_path, config, temperature, max_tokens, verbose):
    """Start project-aware development mode (like Claude Code)"""
    
    # Load custom config if provided
    if config:
        from dotenv import load_dotenv
        load_dotenv(config)
        click.echo(f"📄 Loaded configuration from: {config}")
    
    # Set project path
    if project_path:
        project_path = Path(project_path).resolve()
    else:
        project_path = Path.cwd()
    
    click.echo("🚀 " + "="*60)
    click.echo("   GROK CLI - PROJECT-AWARE DEVELOPMENT MODE")
    click.echo("="*60)
    click.echo(f"📁 Project: {project_path.name}")
    click.echo(f"📍 Path: {project_path}")
    
    # Initialize project-aware agent
    try:
        from .project_agent import ProjectAwareGrokAgent
        
        agent = ProjectAwareGrokAgent(
            project_path=project_path,
            temperature=temperature,
            max_tokens=max_tokens,
            verbose=verbose
        )
        
        # Show project analysis
        project_info = agent.get_project_info()
        click.echo(f"🔍 Languages: {', '.join(project_info['languages']) if project_info['languages'] else 'Unknown'}")
        click.echo(f"🛠️  Frameworks: {', '.join(project_info['frameworks']) if project_info['frameworks'] else 'None detected'}")
        click.echo(f"📊 Files: {project_info['file_count']} files found")
        click.echo(f"📋 Git: {'Yes' if project_info['is_git_repo'] else 'No'}")
        
        click.echo("="*60)
        click.echo("💬 Ready for development! Ask me to:")
        click.echo("   • Analyze your codebase")
        click.echo("   • Fix merge conflicts")
        click.echo("   • Debug issues")
        click.echo("   • Refactor code")
        click.echo("   • Run tests or builds")
        click.echo("💡 Type 'quit', 'exit', or press Ctrl+C to stop.")
        click.echo("="*60)
        
        # Interactive development loop
        while True:
            try:
                user_input = input(f"\n🎯 {project_path.name}> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    click.echo("👋 Happy coding!")
                    break
                
                if user_input.lower() == 'status':
                    project_info = agent.get_project_info()
                    click.echo(f"\n📊 **Project Status:**")
                    click.echo(f"   Current directory: {project_info['current_dir']}")
                    click.echo(f"   Languages: {', '.join(project_info['languages'])}")
                    click.echo(f"   Frameworks: {', '.join(project_info['frameworks'])}")
                    continue
                
                if user_input.lower() == 'tools':
                    agent.list_available_tools()
                    continue
                
                if user_input:
                    click.echo("\n🤖 Assistant:")
                    agent.chat(user_input)
                    
            except KeyboardInterrupt:
                click.echo("\n👋 Happy coding!")
                break
            except Exception as e:
                click.echo(f"❌ Error: {e}")
                
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
        click.echo("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        click.echo(f"❌ Initialization error: {e}")
        click.echo("💡 Check your .env file and API key configuration")

@cli.command()
@click.option('--config', type=click.Path(), help='Path to .env configuration file')
@click.option('--temperature', type=float, help='Model temperature (0.0-2.0)')
@click.option('--max-tokens', type=int, help='Maximum tokens in response')
@click.option('--verbose', is_flag=True, help='Enable verbose mode')
@click.option('--enhanced', is_flag=True, default=True, help='Use enhanced agent with filesystem tools')
@click.option('--mcp', is_flag=True, help='Use MCP-enhanced agent')
def chat(config, temperature, max_tokens, verbose, enhanced, mcp):
    """Start interactive chat with the AI assistant"""
    
    # Load custom config if provided
    if config:
        from dotenv import load_dotenv
        load_dotenv(config)
        click.echo(f"📄 Loaded configuration from: {config}")
    
    # Display startup banner
    click.echo("🚀 " + "="*60)
    click.echo("   GROK CLI - AI Assistant with Enhanced Capabilities")
    click.echo("="*60)
    
    # Initialize the appropriate agent
    try:
        if mcp:
            from .mcp_enhanced_agent import MCPEnhancedGrokAgent
            agent = MCPEnhancedGrokAgent(
                temperature=temperature,
                max_tokens=max_tokens,
                verbose=verbose
            )
            click.echo("🔌 MCP-Enhanced agent initialized with specialized server support")
        elif enhanced:
            from .enhanced_agent import EnhancedGrokAgent
            agent = EnhancedGrokAgent(
                temperature=temperature,
                max_tokens=max_tokens,
                verbose=verbose
            )
            click.echo("✨ Enhanced agent initialized with filesystem tools")
        else:
            from .agent import GrokAgent
            agent = GrokAgent(
                temperature=temperature,
                max_tokens=max_tokens,
                verbose=verbose
            )
            click.echo("🤖 Standard agent initialized")
        
        # Show configuration
        config_info = agent.get_config()
        click.echo(f"📊 Model: {config_info['model']} | Tools: {config_info.get('total_tools', 'N/A')}")
        
        if mcp:
            available_servers = config_info.get('available_mcp_servers', [])
            active_servers = config_info.get('active_mcp_servers', [])
            click.echo(f"🔌 MCP Servers: {len(active_servers)}/{len(available_servers)} active")
            if available_servers:
                click.echo(f"   Available: {', '.join(available_servers)}")
            
        click.echo("="*60)
        click.echo("💬 Start chatting! Type 'quit', 'exit', or press Ctrl+C to stop.")
        
        if mcp:
            click.echo("💡 MCP Commands: 'activate server_name', 'deactivate server_name', 'mcp status'")
        
        click.echo("="*60)
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("\n🗣️  You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    click.echo("👋 Goodbye!")
                    break
                
                # Handle MCP commands if using MCP agent
                if mcp and hasattr(agent, 'activate_mcp_server'):
                    if user_input.startswith('activate '):
                        server_name = user_input[9:].strip()
                        click.echo(f"🔌 Activating {server_name} MCP server...")
                        success = agent.activate_mcp_server(server_name)
                        if success:
                            click.echo(f"✅ {server_name} server activated!")
                        else:
                            click.echo(f"❌ Failed to activate {server_name}")
                        continue
                    
                    elif user_input.startswith('deactivate '):
                        server_name = user_input[11:].strip()
                        click.echo(f"🔌 Deactivating {server_name} MCP server...")
                        success = agent.deactivate_mcp_server(server_name)
                        if success:
                            click.echo(f"✅ {server_name} server deactivated!")
                        else:
                            click.echo(f"❌ Failed to deactivate {server_name}")
                        continue
                    
                    elif user_input.lower() == 'mcp status':
                        config_info = agent.get_config()
                        click.echo(f"\n📊 **MCP Status:**")
                        click.echo(f"   Total tools: {config_info['total_tools']}")
                        click.echo(f"   Active servers: {config_info['active_mcp_servers']}")
                        click.echo(f"   Available servers: {config_info['available_mcp_servers']}")
                        continue
                    
                    elif user_input.lower() == 'mcp servers':
                        agent.demonstrate_mcp_capabilities()
                        continue
                
                if user_input:
                    click.echo("\n🤖 Assistant:")
                    agent.chat(user_input)
                    
            except KeyboardInterrupt:
                click.echo("\n👋 Goodbye!")
                break
            except Exception as e:
                click.echo(f"❌ Error: {e}")
                
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
        click.echo("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        click.echo(f"❌ Initialization error: {e}")
        click.echo("💡 Check your .env file and API key configuration")

@cli.command()
def setup():
    """Set up environment configuration"""
    try:
        from .setup_env import setup_environment
        setup_environment()
    except ImportError:
        click.echo("❌ Setup module not found")
    except Exception as e:
        click.echo(f"❌ Setup error: {e}")

@cli.command()
@click.option('--enhanced', is_flag=True, default=True, help='Test enhanced filesystem tools')
@click.option('--mcp', is_flag=True, help='Test MCP integration')
@click.option('--project', is_flag=True, help='Test project-aware mode')
def test(enhanced, mcp, project):
    """Test tools and functionality"""
    click.echo("🧪 Running tool tests...")
    
    if project:
        click.echo("🎯 Testing project-aware mode...")
        try:
            from .project_agent import ProjectAwareGrokAgent
            agent = ProjectAwareGrokAgent()
            click.echo("✅ Project agent initialized successfully")
            project_info = agent.get_project_info()
            click.echo(f"📁 Project: {project_info['project_name']}")
            click.echo(f"🔍 Languages: {', '.join(project_info['languages'])}")
            click.echo(f"📊 Files: {project_info['file_count']} files")
        except Exception as e:
            click.echo(f"❌ Project test error: {e}")
    elif mcp:
        click.echo("🔌 Testing MCP integration...")
        os.system("python test_mcp_integration.py")
    elif enhanced:
        click.echo("✨ Testing enhanced filesystem tools...")
        os.system("python test_enhanced_filesystem.py")
    else:
        click.echo("🔧 Testing basic tools...")
        try:
            from .agent import GrokAgent
            agent = GrokAgent()
            agent.list_available_tools()
        except Exception as e:
            click.echo(f"❌ Test error: {e}")

@cli.group()
def mcp():
    """MCP (Model Context Protocol) server management"""
    pass

@mcp.command()
def servers():
    """List all available MCP servers"""
    try:
        from .mcp_integration import MCPServerManager
        manager = MCPServerManager()
        
        click.echo("🔌 **Available MCP Servers**")
        click.echo("=" * 50)
        
        servers = manager.list_available_servers()
        for server_name, server_info in servers.items():
            click.echo(f"\n📡 **{server_info['name']}**")
            click.echo(f"   {server_info['description']}")
            click.echo(f"   Tools: {len(server_info['tools'])}")
            
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@mcp.command()
@click.argument('server_name')
def info(server_name):
    """Get detailed information about a specific MCP server"""
    try:
        from .mcp_integration import MCPServerManager
        manager = MCPServerManager()
        
        server_info = manager.get_server_info(server_name)
        if server_info:
            click.echo(f"📡 **{server_info['name']}**")
            click.echo(f"Description: {server_info['description']}")
            click.echo(f"Tools ({len(server_info['tools'])}):")
            for tool in server_info['tools']:
                click.echo(f"  • {tool}")
        else:
            click.echo(f"❌ Server '{server_name}' not found")
            
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@mcp.command()
def demo():
    """Run MCP integration demonstration"""
    try:
        os.system("python test_mcp_integration.py")
    except Exception as e:
        click.echo(f"❌ Demo error: {e}")

@cli.command()
def tools():
    """List all available tools across all agents"""
    click.echo("🛠️  **Available Tools by Agent Type**")
    click.echo("=" * 60)
    
    # Standard agent tools
    try:
        from .agent import GrokAgent
        agent = GrokAgent()
        tools = agent.get_config().get('tools', [])
        click.echo(f"\n🤖 **Standard Agent** ({len(tools)} tools)")
        for tool in tools[:5]:  # Show first 5
            click.echo(f"   • {tool}")
        if len(tools) > 5:
            click.echo(f"   ... and {len(tools) - 5} more")
    except Exception as e:
        click.echo(f"❌ Standard agent error: {e}")
    
    # Enhanced agent tools
    try:
        from .enhanced_agent import EnhancedGrokAgent
        agent = EnhancedGrokAgent()
        config = agent.get_config()
        click.echo(f"\n✨ **Enhanced Agent** ({config.get('total_tools', 'N/A')} tools)")
        click.echo(f"   • Composio tools: {config.get('composio_tools', 'N/A')}")
        click.echo(f"   • Custom tools: {config.get('custom_tools', 'N/A')}")
    except Exception as e:
        click.echo(f"❌ Enhanced agent error: {e}")
    
    # MCP agent tools
    try:
        from .mcp_enhanced_agent import MCPEnhancedGrokAgent
        agent = MCPEnhancedGrokAgent()
        config = agent.get_config()
        click.echo(f"\n🔌 **MCP Agent** ({config.get('total_tools', 'N/A')} tools)")
        click.echo(f"   • Available servers: {len(config.get('available_mcp_servers', []))}")
        click.echo(f"   • Active servers: {len(config.get('active_mcp_servers', []))}")
    except Exception as e:
        click.echo(f"❌ MCP agent error: {e}")
    
    # Project agent tools
    try:
        from .project_agent import ProjectAwareGrokAgent
        agent = ProjectAwareGrokAgent()
        config = agent.get_config()
        click.echo(f"\n🎯 **Project Agent** ({config.get('total_tools', 'N/A')} tools)")
        click.echo(f"   • Project-aware development tools")
        click.echo(f"   • Git integration tools")
        click.echo(f"   • Language detection tools")
    except Exception as e:
        click.echo(f"❌ Project agent error: {e}")

if __name__ == "__main__":
    cli()