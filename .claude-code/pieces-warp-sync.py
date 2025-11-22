"""
Pieces MCP Integration for Warp Terminal Sync
Keeps Pieces in sync with Warp terminal activities
"""
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class PiecesWarpSync:
    """Syncs Pieces MCP with Warp terminal activities."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.warp_config = self.project_root / "warp.config.yaml"
    
    def capture_warp_context(self) -> Dict[str, Any]:
        """Capture current Warp terminal context."""
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "project_root": str(self.project_root),
            "warp_config_exists": self.warp_config.exists(),
            "current_directory": os.getcwd(),
            "environment": dict(os.environ)
        }
        
        # Capture Warp-specific context if available
        if "WARP_SESSION_ID" in os.environ:
            context["warp_session_id"] = os.environ["WARP_SESSION_ID"]
        
        if "WARP_WORKFLOW" in os.environ:
            context["warp_workflow"] = os.environ["WARP_WORKFLOW"]
        
        return context
    
    def sync_to_pieces(self, context: Dict[str, Any], activity_type: str = "warp_activity"):
        """Sync context to Pieces via MCP."""
        # This would use Pieces MCP to store context
        # For now, log the sync operation
        print(f"Syncing {activity_type} to Pieces MCP...")
        print(f"Context: {json.dumps(context, indent=2)}")
        
        # In production, would call Pieces MCP API
        # mcp_Pieces_create_pieces_memory(...)
    
    def capture_command_context(self, command: str, output: Optional[str] = None):
        """Capture command execution context for Pieces."""
        context = self.capture_warp_context()
        context.update({
            "activity_type": "command_execution",
            "command": command,
            "output": output,
            "tool": "warp"
        })
        
        self.sync_to_pieces(context, "warp_command")
    
    def capture_file_context(self, file_path: str, operation: str = "accessed"):
        """Capture file access context for Pieces."""
        context = self.capture_warp_context()
        context.update({
            "activity_type": "file_access",
            "file_path": file_path,
            "operation": operation,
            "tool": "warp"
        })
        
        self.sync_to_pieces(context, "warp_file_access")


def main():
    """CLI interface for Pieces-Warp sync."""
    import sys
    
    sync = PiecesWarpSync()
    
    if len(sys.argv) < 2:
        print("Usage: python pieces-warp-sync.py <command|file> [args...]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "command" and len(sys.argv) > 2:
        command = " ".join(sys.argv[2:])
        sync.capture_command_context(command)
    
    elif action == "file" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        operation = sys.argv[3] if len(sys.argv) > 3 else "accessed"
        sync.capture_file_context(file_path, operation)
    
    elif action == "context":
        context = sync.capture_warp_context()
        print(json.dumps(context, indent=2))
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()

