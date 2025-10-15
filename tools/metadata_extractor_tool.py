from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import os
from datetime import datetime
from PIL import Image


class MetadataExtractorInput(BaseModel):
    """Input schema for MetadataExtractorTool."""
    file_path: str = Field(..., description="Path to the file to extract metadata from")


class MetadataExtractorTool(BaseTool):
    name: str = "Metadata Extractor Tool"
    description: str = (
        "Extracts comprehensive metadata from files including file statistics, "
        "creation/modification dates, file type information, and file size. "
        "For image files, also extracts dimensions, format, and color mode."
    )
    args_schema: Type[BaseModel] = MetadataExtractorInput

    def _run(self, file_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from a file.

        Args:
            file_path: Path to the file to extract metadata from

        Returns:
            Dictionary containing file metadata
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}

            file_stats = os.stat(file_path)
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1]

            metadata = {
                "file_name": file_name,
                "file_path": file_path,
                "file_size": file_stats.st_size,
                "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "file_extension": file_extension,
                "created_date": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified_date": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "file_type": self._determine_file_type(file_extension)
            }

            # Add image-specific metadata
            if self._is_image(file_extension):
                image_metadata = self._extract_image_metadata(file_path)
                metadata.update({"image_metadata": image_metadata})

            return metadata

        except Exception as e:
            return {"error": f"Failed to extract metadata: {str(e)}"}

    def _determine_file_type(self, extension: str) -> str:
        """Determine file category based on extension."""
        doc_types = {
            '.pdf': 'PDF Document',
            '.doc': 'Word Document',
            '.docx': 'Word Document',
            '.txt': 'Text File',
            '.xlsx': 'Excel Spreadsheet',
            '.xls': 'Excel Spreadsheet',
            '.pptx': 'PowerPoint Presentation',
            '.jpg': 'Image',
            '.jpeg': 'Image',
            '.png': 'Image',
            '.gif': 'Image',
            '.bmp': 'Image',
            '.tiff': 'Image'
        }
        return doc_types.get(extension.lower(), 'Unknown')

    def _is_image(self, extension: str) -> bool:
        """Check if the file is an image based on extension."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        return extension.lower() in image_extensions

    def _extract_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract detailed metadata from image files."""
        try:
            with Image.open(image_path) as img:
                return {
                    "dimensions": f"{img.size[0]}x{img.size[1]}",
                    "width": img.size[0],
                    "height": img.size[1],
                    "format": img.format,
                    "mode": img.mode,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            return {"error": f"Could not read image metadata: {str(e)}"}


def categorize_files_by_type(file_paths: list) -> Dict[str, list]:
    """
    Categorize files into different types for processing.

    Args:
        file_paths: List of file paths to categorize

    Returns:
        Dictionary with categorized file lists
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx']

    categorized = {
        'images': [],
        'documents': [],
        'other': []
    }

    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in image_extensions:
            categorized['images'].append(file_path)
        elif ext in document_extensions:
            categorized['documents'].append(file_path)
        else:
            categorized['other'].append(file_path)

    return categorized
