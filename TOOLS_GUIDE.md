# Grok CLI Tools Guide

## Overview
Your Grok CLI uses Composio to provide powerful tool integration with LangChain. This guide shows you how to add and use different types of tools.

## Configuration with .env Files

### Setting Up Your Environment
1. **Copy the example file**: `cp .env.example .env`
2. **Edit the .env file** with your actual values:
   ```bash
   # Required
   GROK_API_KEY=your_actual_api_key_here
   
   # Optional - customize as needed
   GROK_MODEL=grok-4-0709
   GROK_BASE_URL=https://api.x.ai/v1
   GROK_TEMPERATURE=0.7
   GROK_MAX_TOKENS=1000
   GROK_VERBOSE=False
   ```

### Configuration Options
- **GROK_API_KEY**: Your API key from x.ai (required)
- **GROK_MODEL**: Model to use (default: grok-4-0709)
- **GROK_BASE_URL**: API base URL (default: https://api.x.ai/v1)
- **GROK_TEMPERATURE**: Response creativity (0.0-1.0, default: 0.7)
- **GROK_MAX_TOKENS**: Maximum response length (default: 1000)
- **GROK_VERBOSE**: Enable detailed logging (default: False)

## Currently Available Tools

### 1. FILETOOL
- **Purpose**: File and directory operations
- **Capabilities**:
  - Read files
  - Write files
  - Create directories
  - Delete files/directories
  - List directory contents
  - Move/copy files

### 2. SHELLTOOL
- **Purpose**: Execute shell/terminal commands
- **Capabilities**:
  - Run any terminal command
  - Execute scripts
  - Install packages
  - Git operations
  - System management
  - **System Information**: Get OS info, processes, memory, disk usage

### System Information via Shell Commands
Since SYSTEMTOOL has compatibility issues, use SHELLTOOL for system information:
- **System Info**: `uname -a`
- **Process Info**: `ps aux`
- **Disk Usage**: `df -h`
- **Memory Usage**: `free -h` (Linux) or `vm_stat` (macOS)
- **CPU Info**: `cat /proc/cpuinfo` (Linux) or `sysctl -n machdep.cpu.brand_string` (macOS)

## Adding More Tools

### Available Composio Apps
```python
# In your agent.py, you can add these apps:
self.tools = self.composio_toolset.get_tools(apps=[
    App.FILETOOL,      # File operations
    App.SHELLTOOL,     # Shell commands  
    # System operations available via SHELLTOOL
    App.WEBTOOL,       # Web scraping and HTTP requests
    App.SEARCHTOOL,    # Search capabilities
    App.GITHUBTOOL,    # GitHub operations
    App.SLACKTOOL,     # Slack integration
    App.EMAILTOOL,     # Email operations
    App.CALENDARTOOL,  # Calendar management
    App.DATABASETOOL,  # Database operations
])
```

### Adding Tools Dynamically
You can now add tools at runtime:
```python
agent = GrokAgent()
agent.add_tool("WEBTOOL")      # Add web scraping capabilities
agent.add_tool("GITHUBTOOL")   # Add GitHub integration
```

### Adding Custom Tools
You can also create custom tools:

```python
from langchain.tools import tool
from typing import Optional

@tool
def custom_file_analyzer(file_path: str) -> str:
    """Analyze a file and return detailed information about it."""
    import os
    from pathlib import Path
    
    path = Path(file_path)
    if not path.exists():
        return f"File {file_path} does not exist"
    
    stat = path.stat()
    return f"""
    File Analysis for {file_path}:
    - Size: {stat.st_size} bytes
    - Modified: {stat.st_mtime}
    - Type: {path.suffix}
    - Permissions: {oct(stat.st_mode)}
    """

# Add to your agent
self.tools.extend([custom_file_analyzer])
```

## Enhanced Filesystem Access

### Current File Operations
With FILETOOL, you can already:
- Read any file: "Read the contents of config.json"
- Write files: "Create a new Python file with a hello world function"
- Navigate directories: "List all files in the current directory"
- Delete files: "Delete the temporary files in /tmp"

### Enhanced Operations with SHELLTOOL
Combine with shell commands for advanced operations:
- "Find all Python files larger than 1MB"
- "Create a backup of the entire project"
- "Run a recursive search for TODO comments"
- "Set up a new virtual environment"
- "Show me system information like OS and memory usage"
- "Check what processes are running"

## Usage Examples

### Basic Setup
```bash
# Copy and configure .env file
cp .env.example .env
# Edit .env with your GROK_API_KEY

# Test configuration
python test_tools.py config

# Run basic tests
python test_tools.py basic
```

### Using the CLI
```bash
# Start the CLI (uses .env automatically)
grok-cli

# Show configuration
grok-cli --config

# Use custom settings
grok-cli --temperature 0.9 --max-tokens 1500 --verbose
```

### Basic File Operations
```python
from grok_cli.agent import GrokAgent

# Initialize with .env file
agent = GrokAgent()

# Read a file
agent.chat("Read the contents of readme.md")

# Create a new file
agent.chat("Create a new Python file called utils.py with basic logging setup")

# List directory contents
agent.chat("Show me all files in the current directory")
```

### System Operations
```python
# System analysis
agent.chat("Show me system information and current memory usage")

# Process monitoring
agent.chat("Show me running processes")

# Disk usage
agent.chat("Check disk usage")

# Environment info
agent.chat("Show environment variables")
```

### Advanced Operations
```python
# Code analysis
agent.chat("Find all Python files and analyze their complexity")

# Project setup
agent.chat("Create a new Django project structure")

# Git operations
agent.chat("Check git status and show recent commits")
```

### Adding Tools at Runtime
```python
# Add web capabilities
agent.add_tool("WEBTOOL")
agent.chat("Scrape the latest news from a tech website")

# Add GitHub integration
agent.add_tool("GITHUBTOOL")
agent.chat("Check my GitHub repositories")
```

## Best Practices

1. **Use .env Files**: Keep sensitive data out of code
2. **Start Small**: Begin with FILETOOL and SHELLTOOL
3. **Test New Tools**: Use `agent.add_tool()` to test before adding permanently
4. **System Info via Shell**: Use shell commands for system information
5. **Security**: Be careful with SHELLTOOL - it can execute any command
6. **Error Handling**: The agent includes built-in error handling
7. **Permissions**: Ensure proper file permissions for operations

## Troubleshooting

### Common Issues
1. **Missing API Key**: Check .env file and GROK_API_KEY
2. **Tool Compatibility**: Some tools may not be available in all Composio versions
3. **Permission Denied**: Check file/directory permissions
4. **Rate Limiting**: Built-in handling for API rate limits

### Testing Tools
```bash
# Test basic functionality
python test_tools.py basic

# Test specific tool addition
python -c "
from grok_cli.agent import GrokAgent
agent = GrokAgent()
agent.add_tool('WEBTOOL')
print('WEBTOOL added successfully')
"
```

### Testing Configuration
```bash
# Test your .env setup
python test_tools.py config

# Test basic functionality
python test_tools.py basic

# Interactive testing
python test_tools.py interactive
```

### CLI Testing
```bash
# Show current configuration
grok-cli --config

# Test with development mode
grok-cli --dev  # Uses OpenAI instead (cheaper for testing)
```

## Next Steps

1. **Set Up .env**: Copy .env.example and add your API key
2. **Test Current Setup**: Try the enhanced agent with basic tools
3. **Add More Tools**: Use `agent.add_tool()` to test new capabilities
4. **Create Custom Tools**: For project-specific operations
5. **Integrate with CI/CD**: Use for automated development tasks

## Security Considerations

- **Never commit .env files**: They contain sensitive API keys
- **Use .env.example**: For sharing configuration templates
- **SHELLTOOL**: Can execute any command - use carefully
- **FILETOOL**: Has full file system access
- **System Commands**: Be cautious with shell commands that modify system state
- Always review commands before execution in production 