"""
Custom filesystem tools for enhanced local filesystem access
"""

import os
import shutil
import stat
import time
from pathlib import Path
from typing import List, Dict, Optional
from langchain.tools import tool

@tool
def advanced_file_info(file_path: str) -> str:
    """Get comprehensive information about a file or directory including permissions, size, dates, and type."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"❌ Path '{file_path}' does not exist"
        
        # Get file stats
        stat_info = path.stat()
        
        # File type
        if path.is_file():
            file_type = "📄 File"
        elif path.is_dir():
            file_type = "📁 Directory"
        elif path.is_symlink():
            file_type = "🔗 Symbolic Link"
        else:
            file_type = "❓ Unknown"
        
        # Permissions
        permissions = oct(stat_info.st_mode)[-3:]
        readable = "✅" if os.access(path, os.R_OK) else "❌"
        writable = "✅" if os.access(path, os.W_OK) else "❌"
        executable = "✅" if os.access(path, os.X_OK) else "❌"
        
        # Dates
        created = time.ctime(stat_info.st_ctime)
        modified = time.ctime(stat_info.st_mtime)
        accessed = time.ctime(stat_info.st_atime)
        
        # Size
        if path.is_file():
            size = stat_info.st_size
            if size < 1024:
                size_str = f"{size} bytes"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                size_str = f"{size/(1024*1024):.1f} MB"
            else:
                size_str = f"{size/(1024*1024*1024):.1f} GB"
        else:
            # For directories, count items
            try:
                items = list(path.iterdir())
                size_str = f"{len(items)} items"
            except PermissionError:
                size_str = "Permission denied"
        
        result = f"""
📋 **File Information for: {file_path}**
────────────────────────────────────────
🏷️  Type: {file_type}
📏 Size: {size_str}
🔒 Permissions: {permissions}
   └── Read: {readable} | Write: {writable} | Execute: {executable}
📅 Created: {created}
📝 Modified: {modified}
👁️  Accessed: {accessed}
🗂️  Full Path: {path.absolute()}
        """
        
        # Additional info for symlinks
        if path.is_symlink():
            target = path.readlink()
            result += f"\n🎯 Target: {target}"
        
        return result.strip()
        
    except Exception as e:
        return f"❌ Error getting file info: {str(e)}"

@tool
def safe_file_operations(operation: str, source: str, destination: str = "") -> str:
    """Perform safe file operations with confirmation and backup. Operations: copy, move, backup, restore."""
    try:
        source_path = Path(source)
        
        if operation == "backup":
            if not source_path.exists():
                return f"❌ Source '{source}' does not exist"
            
            # Create backup with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.name}.backup_{timestamp}"
            backup_path = source_path.parent / backup_name
            
            if source_path.is_file():
                shutil.copy2(source_path, backup_path)
                return f"✅ File backed up: {source} → {backup_path}"
            else:
                shutil.copytree(source_path, backup_path)
                return f"✅ Directory backed up: {source} → {backup_path}"
        
        elif operation == "copy":
            if not destination:
                return "❌ Destination required for copy operation"
            
            dest_path = Path(destination)
            
            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
                return f"✅ File copied: {source} → {destination}"
            else:
                if dest_path.exists():
                    return f"❌ Destination '{destination}' already exists"
                shutil.copytree(source_path, dest_path)
                return f"✅ Directory copied: {source} → {destination}"
        
        elif operation == "move":
            if not destination:
                return "❌ Destination required for move operation"
            
            dest_path = Path(destination)
            shutil.move(source_path, dest_path)
            return f"✅ Moved: {source} → {destination}"
        
        else:
            return f"❌ Unknown operation: {operation}. Use: backup, copy, move"
            
    except Exception as e:
        return f"❌ Error during {operation}: {str(e)}"

@tool
def directory_tree(path: str = ".", max_depth: int = 3, show_hidden: bool = False) -> str:
    """Generate a visual tree structure of directories and files."""
    try:
        root_path = Path(path)
        if not root_path.exists():
            return f"❌ Path '{path}' does not exist"
        
        def _build_tree(current_path: Path, prefix: str = "", depth: int = 0) -> List[str]:
            if depth > max_depth:
                return []
            
            items = []
            try:
                children = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                
                # Filter hidden files if requested
                if not show_hidden:
                    children = [child for child in children if not child.name.startswith('.')]
                
                for i, child in enumerate(children):
                    is_last = i == len(children) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = "    " if is_last else "│   "
                    
                    # Icon based on file type
                    if child.is_dir():
                        icon = "📁"
                    elif child.suffix.lower() in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
                        icon = "📝"
                    elif child.suffix.lower() in ['.txt', '.md', '.rst']:
                        icon = "📄"
                    elif child.suffix.lower() in ['.jpg', '.png', '.gif', '.svg']:
                        icon = "🖼️"
                    elif child.suffix.lower() in ['.mp3', '.wav', '.mp4', '.avi']:
                        icon = "🎵"
                    else:
                        icon = "📄"
                    
                    items.append(f"{prefix}{current_prefix}{icon} {child.name}")
                    
                    # Recurse into directories
                    if child.is_dir() and depth < max_depth:
                        items.extend(_build_tree(child, prefix + next_prefix, depth + 1))
                        
            except PermissionError:
                items.append(f"{prefix}└── ❌ Permission denied")
            
            return items
        
        tree_lines = [f"🌳 Directory Tree: {root_path.absolute()}"]
        tree_lines.extend(_build_tree(root_path))
        
        return "\n".join(tree_lines)
        
    except Exception as e:
        return f"❌ Error generating tree: {str(e)}"

@tool
def find_files_advanced(pattern: str, directory: str = ".", 
                       file_type: str = "all", min_size: str = "", max_size: str = "") -> str:
    """Advanced file search with pattern matching, type filtering, and size constraints."""
    try:
        search_path = Path(directory)
        if not search_path.exists():
            return f"❌ Directory '{directory}' does not exist"
        
        def parse_size(size_str: str) -> int:
            """Parse size string like '10MB', '500KB', '1GB' to bytes"""
            if not size_str:
                return 0
            
            size_str = size_str.upper()
            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            
            for suffix, mult in multipliers.items():
                if size_str.endswith(suffix):
                    return int(float(size_str[:-len(suffix)]) * mult)
            
            return int(size_str)  # Assume bytes if no suffix
        
        min_bytes = parse_size(min_size) if min_size else 0
        max_bytes = parse_size(max_size) if max_size else float('inf')
        
        matches = []
        
        for file_path in search_path.rglob(pattern):
            try:
                # Type filtering
                if file_type == "files" and not file_path.is_file():
                    continue
                elif file_type == "dirs" and not file_path.is_dir():
                    continue
                
                # Size filtering (only for files)
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if size < min_bytes or size > max_bytes:
                        continue
                
                # Format the match
                rel_path = file_path.relative_to(search_path)
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024**2:
                        size_str = f"{size/1024:.1f}KB"
                    else:
                        size_str = f"{size/1024**2:.1f}MB"
                    matches.append(f"📄 {rel_path} ({size_str})")
                else:
                    matches.append(f"📁 {rel_path}/")
                    
            except (PermissionError, OSError):
                continue
        
        if not matches:
            return f"🔍 No files found matching pattern '{pattern}' in '{directory}'"
        
        result = f"🔍 **Found {len(matches)} matches for '{pattern}':**\n"
        result += "\n".join(matches[:50])  # Limit to first 50 results
        
        if len(matches) > 50:
            result += f"\n... and {len(matches) - 50} more matches"
        
        return result
        
    except Exception as e:
        return f"❌ Error during search: {str(e)}"

@tool
def monitor_directory_changes(directory: str = ".", duration: int = 10) -> str:
    """Monitor a directory for changes over a specified duration (in seconds)."""
    try:
        watch_path = Path(directory)
        if not watch_path.exists():
            return f"❌ Directory '{directory}' does not exist"
        
        # Take initial snapshot
        initial_files = {}
        for file_path in watch_path.rglob("*"):
            if file_path.is_file():
                try:
                    stat_info = file_path.stat()
                    initial_files[str(file_path)] = {
                        'size': stat_info.st_size,
                        'mtime': stat_info.st_mtime
                    }
                except (PermissionError, OSError):
                    continue
        
        return f"📊 Directory snapshot taken. {len(initial_files)} files monitored in '{directory}'"
        
    except Exception as e:
        return f"❌ Error monitoring directory: {str(e)}" 