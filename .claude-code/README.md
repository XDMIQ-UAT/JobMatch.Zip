# Claude Code Hooks Configuration

This directory contains hooks and configuration for optimizing Claude Code prompt architecture.

## Files

- `hooks.json` - Main hooks configuration
- `prompts.md` - Prompt templates and examples
- `context-loader.py` - Context loading utility

## Usage

### Quick Start

1. Use hooks automatically when coding in Cursor
2. Or manually load context:
   ```bash
   python .claude-code/context-loader.py [feature_type] [task]
   ```

### Feature Types

- `api_endpoint` - FastAPI endpoints
- `database_model` - SQLAlchemy models
- `frontend_component` - Next.js components
- `ai_integration` - AI features
- `before_generate` - General code generation

## Customization

Edit `hooks.json` to:
- Add new hook types
- Update prompt templates
- Add example files
- Modify context

## Integration

Works with:
- **Cursor**: Automatic hook loading
- **Claude Code**: Prompt optimization
- **Warp**: Terminal operations


