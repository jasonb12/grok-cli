"""
Project-Aware Grok Agent for Local Development
Works directly on host filesystem like Claude Code
"""

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from composio_langchain import ComposioToolSet, App, WorkspaceType
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class ProjectAwareGrokAgent:
    def __init__(self, project_path=None, api_key=None, model=None, base_url=None, temperature=None, max_tokens=None, verbose=None):
        # Load from .env file if parameters not provided
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        self.model = model or os.getenv("GROK_MODEL", "grok-4-0709")
        self.base_url = base_url or os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
        self.temperature = float(temperature or os.getenv("GROK_TEMPERATURE", "0.7"))
        self.max_tokens = int(max_tokens or os.getenv("GROK_MAX_TOKENS", "1000"))
        self.verbose = verbose if verbose is not None else os.getenv("GROK_VERBOSE", "False").lower() == "true"
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY must be provided either as parameter or in .env file")
        
        # Set project path (current directory if not specified)
        self.project_path = Path(project_path or os.getcwd()).resolve()
        print(f"🎯 Project path: {self.project_path}")
        
        # Change to project directory
        os.chdir(self.project_path)
        
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Configure ComposioToolSet with explicit Host workspace for direct filesystem access
        self.composio_toolset = ComposioToolSet(
            workspace_config=WorkspaceType.Host()
        )
        
        # Get comprehensive tools for project development
        self.tools = self.composio_toolset.get_tools(apps=[
            App.FILETOOL,      # File operations (read, write, create, delete)
            App.SHELLTOOL,     # Shell/terminal commands
            App.GITHUBTOOL,    # Git operations for version control
        ])
        
        # Analyze project structure for context
        self.project_context = self._analyze_project_structure()
        
        # Create project-aware system prompt
        system_prompt = self._create_system_prompt()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
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
            max_iterations=15  # Increased for complex project operations
        )
    
    def _analyze_project_structure(self):
        """Analyze the project structure to understand the codebase"""
        context = {
            "project_path": str(self.project_path),
            "project_name": self.project_path.name,
            "is_git_repo": (self.project_path / ".git").exists(),
            "files": [],
            "languages": set(),
            "frameworks": set(),
        }
        
        # Common file extensions and their languages
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', 
            '.jsx': 'React', '.tsx': 'React TypeScript', '.vue': 'Vue.js',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
            '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby',
            '.html': 'HTML', '.css': 'CSS', '.scss': 'SASS', '.less': 'LESS',
            '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML', '.xml': 'XML',
            '.md': 'Markdown', '.txt': 'Text', '.sh': 'Shell Script'
        }
        
        # Framework detection patterns
        framework_patterns = {
            'package.json': ['Node.js/npm'],
            'requirements.txt': ['Python'],
            'Pipfile': ['Python/Pipenv'],
            'poetry.lock': ['Python/Poetry'],
            'Cargo.toml': ['Rust'],
            'go.mod': ['Go'],
            'pom.xml': ['Java/Maven'],
            'build.gradle': ['Java/Gradle'],
            'composer.json': ['PHP/Composer'],
            'Gemfile': ['Ruby/Bundler'],
            'yarn.lock': ['Node.js/Yarn'],
            'next.config.js': ['Next.js'],
            'nuxt.config.js': ['Nuxt.js'],
            'vue.config.js': ['Vue.js'],
            'angular.json': ['Angular'],
            'svelte.config.js': ['Svelte'],
            'tailwind.config.js': ['Tailwind CSS'],
            'webpack.config.js': ['Webpack'],
            'vite.config.js': ['Vite'],
            'tsconfig.json': ['TypeScript'],
            'dockerfile': ['Docker'],
            'docker-compose.yml': ['Docker Compose'],
            '.gitignore': ['Git'],
            'README.md': ['Documentation']
        }
        
        try:
            # Scan project files (limit to reasonable depth)
            for item in self.project_path.rglob("*"):
                if item.is_file() and not any(part.startswith('.') for part in item.parts):
                    relative_path = item.relative_to(self.project_path)
                    context["files"].append(str(relative_path))
                    
                    # Detect language
                    suffix = item.suffix.lower()
                    if suffix in language_map:
                        context["languages"].add(language_map[suffix])
                    
                    # Detect frameworks
                    filename = item.name.lower()
                    for pattern, frameworks in framework_patterns.items():
                        if pattern in filename:
                            context["frameworks"].update(frameworks)
                    
                    # Limit file scanning to prevent overload
                    if len(context["files"]) > 100:
                        break
            
        except Exception as e:
            print(f"Warning: Could not fully analyze project structure: {e}")
        
        return context
    
    def _create_system_prompt(self):
        """Create a project-aware system prompt"""
        context = self.project_context
        
        prompt = f"""You are an expert software development assistant working directly on the user's local filesystem, similar to Claude Code or GitHub Copilot. 

**CURRENT PROJECT CONTEXT:**
- Project: {context['project_name']}
- Path: {context['project_path']}
- Git Repository: {'Yes' if context['is_git_repo'] else 'No'}
- Languages: {', '.join(sorted(context['languages'])) if context['languages'] else 'Unknown'}
- Frameworks: {', '.join(sorted(context['frameworks'])) if context['frameworks'] else 'None detected'}
- Files Found: {len(context['files'])} files

**YOUR CAPABILITIES:**
You have direct access to the host filesystem through these tools:
- **File Operations**: Read, write, edit, create, delete files and directories
- **Shell Commands**: Execute terminal commands (npm install, git commands, build scripts, etc.)
- **Git Operations**: Full version control capabilities (status, commit, push, pull, merge, etc.)

**DEVELOPMENT WORKFLOW ASSISTANCE:**
- **Code Analysis**: Read and understand existing codebase structure
- **Merge Conflict Resolution**: Detect conflicts via git status, read conflicted files, resolve conflicts by editing files
- **Project Setup**: Install dependencies, run build scripts, start dev servers
- **Testing**: Run test suites, lint code, format code
- **Debugging**: Analyze logs, check file contents, run diagnostic commands
- **Refactoring**: Modify multiple files safely with proper backup practices

**WORKING PRINCIPLES:**
1. **Project Awareness**: Always consider the project context and existing patterns
2. **Safety First**: Use git status before major changes, create branches for risky operations
3. **Explain Actions**: Describe what you're doing before executing commands
4. **Iterative Development**: Break complex tasks into smaller, verifiable steps
5. **Follow Conventions**: Respect existing code style, naming patterns, and project structure

**MERGE CONFLICT RESOLUTION WORKFLOW:**
1. Run `git status` to identify conflicted files
2. Read conflicted files to understand the conflicts
3. Analyze both sides of conflicts (HEAD vs incoming changes)
4. Edit files to resolve conflicts (remove conflict markers, choose appropriate code)
5. Test the resolution if possible
6. Add resolved files with `git add`
7. Complete the merge with `git commit`

**COMMON COMMANDS FOR PROJECT WORK:**
- `git status` - Check repository state
- `git log --oneline -10` - Recent commits
- `npm install` / `pip install -r requirements.txt` - Install dependencies
- `npm test` / `pytest` / `cargo test` - Run tests
- `npm run build` / `python setup.py build` - Build project
- `npm start` / `python app.py` - Start development server

Always work within the current project directory: {context['project_path']}
"""
        return prompt
    
    def chat(self, user_message):
        """Chat with the project-aware agent"""
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
        print("🛠️  **Project Development Tools**")
        print("=" * 50)
        for tool in self.tools:
            print(f"  • {tool.name}: {tool.description}")
        return self.tools
    
    def get_project_info(self):
        """Get current project information"""
        return {
            "project_path": self.project_context["project_path"],
            "project_name": self.project_context["project_name"],
            "is_git_repo": self.project_context["is_git_repo"],
            "languages": list(self.project_context["languages"]),
            "frameworks": list(self.project_context["frameworks"]),
            "file_count": len(self.project_context["files"]),
            "current_dir": os.getcwd()
        }
    
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
            "project_info": self.get_project_info()
        } 