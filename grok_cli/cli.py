#!/usr/bin/env python3
"""
Command-line interface for Grok CLI with MCP server support
Enhanced version with filesystem tools and MCP integration
"""

import click
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@click.group()
@click.version_option()
def cli():
    """🚀 Grok CLI - AI Assistant with Enhanced Capabilities
    
    A powerful command-line AI assistant that combines:
    • Composio file and shell tools
    • Enhanced filesystem operations
    • MCP (Model Context Protocol) server integration
    """
    pass

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
def test(enhanced, mcp):
    """Test tools and functionality"""
    click.echo("🧪 Running tool tests...")
    
    if mcp:
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
    """Run interactive MCP demo"""
    click.echo("🎮 Starting MCP Interactive Demo...")
    os.system("python test_mcp_integration.py interactive")

@cli.command()
def tools():
    """List all available tools"""
    try:
        # Try to load the most advanced agent available
        agent = None
        agent_type = "Unknown"
        
        try:
            from .mcp_enhanced_agent import MCPEnhancedGrokAgent
            agent = MCPEnhancedGrokAgent()
            agent_type = "MCP-Enhanced"
        except:
            try:
                from .enhanced_agent import EnhancedGrokAgent
                agent = EnhancedGrokAgent()
                agent_type = "Enhanced"
            except:
                from .agent import GrokAgent
                agent = GrokAgent()
                agent_type = "Standard"
        
        click.echo(f"🛠️  **{agent_type} Agent Tools**")
        click.echo("=" * 50)
        agent.list_available_tools()
        
    except Exception as e:
        click.echo(f"❌ Error listing tools: {e}")

@cli.command()
def config():
    """Show current configuration"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        click.echo("⚙️  **Current Configuration**")
        click.echo("=" * 40)
        
        config_vars = [
            ('GROK_API_KEY', 'API Key'),
            ('GROK_MODEL', 'Model'),
            ('GROK_BASE_URL', 'Base URL'),
            ('GROK_TEMPERATURE', 'Temperature'),
            ('GROK_MAX_TOKENS', 'Max Tokens'),
            ('GROK_VERBOSE', 'Verbose Mode')
        ]
        
        for var, label in config_vars:
            value = os.getenv(var, 'Not set')
            if var == 'GROK_API_KEY' and value != 'Not set':
                value = f"{value[:8]}..." + "*" * 10  # Mask API key
            click.echo(f"{label:15}: {value}")
            
        # Check .env file
        env_exists = os.path.exists('.env')
        click.echo(f"{''.ljust(15)}: {'Found' if env_exists else 'Not found'}")
        
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}")

def main():
    """Main entry point"""
    cli()

if __name__ == '__main__':
    main()