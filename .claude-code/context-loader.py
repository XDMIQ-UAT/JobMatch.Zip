"""
Claude Code Context Loader
Loads project context for optimized prompt generation
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any


class ContextLoader:
    """Loads and provides project context for Claude Code."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.hooks_file = self.project_root / ".claude-code" / "hooks.json"
        self.context_cache = {}
    
    def load_hooks(self) -> Dict[str, Any]:
        """Load hooks configuration."""
        if self.hooks_file.exists():
            with open(self.hooks_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_project_context(self) -> Dict[str, Any]:
        """Get comprehensive project context."""
        hooks = self.load_hooks()
        
        return {
            "project_name": "AI-Enabled LLC Matching Platform",
            "tech_stack": hooks.get("context", {}).get("tech_stack", {}),
            "key_features": hooks.get("context", {}).get("key_features", []),
            "principles": hooks.get("context", {}).get("principles", []),
            "development_tools": ["Warp", "Claude Code", "Cursor"],
            "workflow": "Interactive business-side coding"
        }
    
    def get_relevant_files(self, feature_type: str) -> List[str]:
        """Get relevant example files for a feature type."""
        hooks = self.load_hooks()
        hook_config = hooks.get("hooks", {}).get(feature_type, {})
        return hook_config.get("example_files", [])
    
    def build_prompt_context(self, task: str, feature_type: str = None) -> str:
        """Build optimized prompt context for a task."""
        context = self.get_project_context()
        hooks = self.load_hooks()
        
        # Handle tech_stack string properly
        backend_stack = context['tech_stack'].get('backend', '')
        if isinstance(backend_stack, str):
            backend_tech = backend_stack
        else:
            backend_tech = ', '.join(backend_stack) if backend_stack else ''
        
        prompt_parts = [
            f"Project: {context['project_name']}",
            f"Tech Stack: {backend_tech}",
            "",
            "Key Principles:",
        ]
        
        for principle in context['principles']:
            prompt_parts.append(f"- {principle}")
        
        if feature_type and feature_type in hooks.get("hooks", {}):
            hook_config = hooks["hooks"][feature_type]
            
            # Load prompt file if specified
            if "prompt_file" in hook_config:
                prompt_file_path = self.project_root / hook_config["prompt_file"]
                if prompt_file_path.exists():
                    with open(prompt_file_path, 'r') as f:
                        prompt_content = f.read()
                        prompt_parts.append("")
                        prompt_parts.append("=" * 60)
                        prompt_parts.append("PROMPT TEMPLATE:")
                        prompt_parts.append("=" * 60)
                        prompt_parts.append(prompt_content)
                        prompt_parts.append("=" * 60)
            
            if "template" in hook_config:
                prompt_parts.append("")
                prompt_parts.append("Template:")
                prompt_parts.append(hook_config["template"])
            
            if "example_files" in hook_config:
                prompt_parts.append("")
                prompt_parts.append("Reference Examples:")
                for file in hook_config["example_files"]:
                    prompt_parts.append(f"- {file}")
        
        prompt_parts.append("")
        prompt_parts.append(f"Task: {task}")
        
        return "\n".join(prompt_parts)


def main():
    """CLI interface for context loading."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Load project context for Claude Code")
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode without side effects')
    parser.add_argument('--print', action='store_true', dest='print_context', help='Print the context')
    parser.add_argument('--limit', type=int, default=None, help='Limit output lines')
    parser.add_argument('--hook', type=str, help='Hook type (e.g., api_endpoint, database_model)')
    parser.add_argument('--topic', type=str, help='Topic/feature type')
    parser.add_argument('--example', type=str, help='Show examples for a hook type')
    parser.add_argument('task', nargs='*', help='Task description')
    
    args = parser.parse_args()
    
    loader = ContextLoader()
    
    # Handle --example flag
    if args.example:
        hooks = loader.load_hooks()
        hook_config = hooks.get('hooks', {}).get(args.example, {})
        if hook_config:
            print(f"Hook: {args.example}")
            print(f"\nTemplate:\n{hook_config.get('template', 'N/A')}")
            print(f"\nExample Files:")
            for file in hook_config.get('example_files', []):
                print(f"  - {file}")
        else:
            print(f"Hook '{args.example}' not found")
            print(f"Available hooks: {', '.join(hooks.get('hooks', {}).keys())}")
        return
    
    # Handle --hook or task
    if args.hook or args.task:
        feature_type = args.hook or args.topic
        task = ' '.join(args.task) if args.task else 'General task'
        context = loader.build_prompt_context(task, feature_type)
        
        # Apply limit if specified
        if args.limit:
            lines = context.split('\n')[:args.limit]
            context = '\n'.join(lines)
        
        if args.dry_run:
            print("[DRY RUN MODE]")
        if args.print_context or not args.task:
            print(context)
    else:
        # Default: show project context as JSON
        context = loader.get_project_context()
        output = json.dumps(context, indent=2)
        
        if args.limit:
            lines = output.split('\n')[:args.limit]
            output = '\n'.join(lines)
        
        print(output)


if __name__ == "__main__":
    main()


