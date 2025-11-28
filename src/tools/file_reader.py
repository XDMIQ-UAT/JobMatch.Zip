"""
File Reader Tool

Tool for reading job descriptions and candidate profiles from files.
"""

from typing import Any, Dict
from pathlib import Path
from src.tools.base_tool import BaseTool


class FileReaderTool(BaseTool):
    """Tool for reading content from files."""
    
    name = "file_reader"
    description = "Reads text content from files (supports .txt, .md, .pdf, .docx)"
    
    def execute(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            source: File path
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with 'content' (text) and 'metadata'
        """
        file_path = Path(source)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        
        # Determine file type
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == ".txt" or suffix == ".md":
                content = file_path.read_text(encoding="utf-8")
            elif suffix == ".pdf":
                # Requires PyPDF2 or pdfplumber
                try:
                    import PyPDF2
                    with open(file_path, "rb") as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        content = "\n".join(page.extract_text() for page in pdf_reader.pages)
                except ImportError:
                    raise ImportError("PyPDF2 is required for PDF files. Install with: pip install PyPDF2")
            elif suffix in [".doc", ".docx"]:
                # Requires python-docx
                try:
                    from docx import Document
                    doc = Document(file_path)
                    content = "\n".join(paragraph.text for paragraph in doc.paragraphs)
                except ImportError:
                    raise ImportError("python-docx is required for DOCX files. Install with: pip install python-docx")
            else:
                # Try to read as text
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            metadata = {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "file_type": suffix,
                "content_length": len(content)
            }
            
            return {
                "content": content,
                "metadata": metadata
            }
        
        except Exception as e:
            raise Exception(f"Failed to read file {source}: {str(e)}")

