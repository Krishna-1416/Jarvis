"""
File Management & Document Tools for Project Jarvis.
Search, read, write, and inspect local files and folders.
"""

import os
from pathlib import Path
from typing import Optional, List
from tools.registry import tool

@tool(description="Search for files by filename or pattern across a folder or common user locations (Downloads, Desktop, Documents).")
def search_files(pattern: str, search_path: Optional[str] = None, max_results: int = 10) -> str:
    """
    Search for files matching a pattern.
    pattern: Filename or wildcard pattern (e.g. '*.pdf', 'report*', 'resume.docx')
    search_path: Base directory to search (defaults to user home directory)
    max_results: Maximum files to return
    """
    base_dir = Path(search_path) if search_path else Path.home()
    if not base_dir.exists():
        return f"Directory '{search_path}' does not exist."

    matches: List[str] = []
    try:
        # Search using glob (shallow + common directories if home)
        target_dirs = [
            base_dir / "Desktop",
            base_dir / "Documents",
            base_dir / "Downloads",
            base_dir / "Projects",
            base_dir
        ] if not search_path else [base_dir]

        pattern_clean = pattern if "*" in pattern else f"*{pattern}*"
        
        for d in target_dirs:
            if d.exists():
                for p in d.rglob(pattern_clean):
                    if p.is_file():
                        matches.append(str(p))
                        if len(matches) >= max_results:
                            break
            if len(matches) >= max_results:
                break

        if not matches:
            return f"No files matching '{pattern}' found."
        
        return "Found matching files:\n" + "\n".join(f"- {m}" for m in matches)
    except Exception as e:
        return f"Error searching files: {str(e)}"

@tool(description="Read the text content of a file (e.g. txt, md, py, json, yaml, csv).")
def read_file_text(file_path: str, max_chars: int = 3000) -> str:
    """
    Read content of a file.
    file_path: Absolute or relative path to the file
    max_chars: Maximum characters to read
    """
    p = Path(file_path).expanduser().resolve()
    if not p.exists():
        return f"File '{file_path}' does not exist."
    if not p.is_file():
        return f"Path '{file_path}' is a directory, not a file."

    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars + 100)
            
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n... [Truncated: File exceeds {max_chars} characters]"
            
        return f"Contents of {p.name}:\n```\n{content}\n```"
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

@tool(description="Write text content to a new or existing file.")
def write_file_text(file_path: str, content: str) -> str:
    """
    Write text to a file.
    file_path: Path to the destination file
    content: The text content to write
    """
    try:
        p = Path(file_path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{p}'."
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"

@tool(description="List files and directories in a given folder.")
def list_directory(dir_path: Optional[str] = None) -> str:
    """
    List directory contents.
    dir_path: Path to directory (defaults to current working directory)
    """
    p = Path(dir_path).expanduser().resolve() if dir_path else Path.cwd()
    if not p.exists():
        return f"Directory '{dir_path}' does not exist."
    
    try:
        items = list(p.iterdir())
        dirs = [f"📁 {item.name}/" for item in items if item.is_dir()]
        files = [f"📄 {item.name} ({item.stat().st_size} bytes)" for item in items if item.is_file()]
        
        output = [f"Directory contents of '{p}':"]
        output.extend(dirs[:20])
        output.extend(files[:30])
        if len(items) > 50:
            output.append(f"... and {len(items) - 50} more items.")
        return "\n".join(output)
    except Exception as e:
        return f"Error listing directory: {str(e)}"
