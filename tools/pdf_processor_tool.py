from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
import PyPDF2


class PDFProcessorInput(BaseModel):
    """Input schema for PDFProcessorTool."""
    file_path: str = Field(..., description="Path to the PDF file to process")


class PDFProcessorTool(BaseTool):
    name: str = "PDF Processor Tool"
    description: str = (
        "Processes PDF files to extract text content, page information, "
        "image detection, and content statistics. Uses PyMuPDF as primary method "
        "with PyPDF2 as fallback for compatibility."
    )
    args_schema: Type[BaseModel] = PDFProcessorInput

    def _run(self, file_path: str) -> Dict[str, Any]:
        """
        Extract detailed content from PDF files.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing PDF analysis results
        """
        try:
            return self._extract_with_pymupdf(file_path)
        except Exception as e:
            # Fallback to PyPDF2 if PyMuPDF fails
            try:
                return self._extract_with_pypdf2(file_path)
            except Exception as e2:
                return {
                    "error": f"PDF extraction failed. PyMuPDF error: {str(e)}, PyPDF2 error: {str(e2)}",
                    "extraction_method": "failed"
                }

    def _extract_with_pymupdf(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF content using PyMuPDF (primary method)."""
        doc = fitz.open(file_path)

        pdf_analysis = {
            "total_pages": len(doc),
            "has_text": False,
            "has_images": False,
            "text_content": "",
            "page_details": [],
            "extraction_method": "PyMuPDF"
        }

        full_text = ""
        total_images = 0

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text
            page_text = page.get_text()
            full_text += page_text + "\n"

            # Check for images
            image_list = page.get_images()
            page_images = len(image_list)
            total_images += page_images

            pdf_analysis["page_details"].append({
                "page_number": page_num + 1,
                "text_length": len(page_text),
                "has_text": len(page_text.strip()) > 0,
                "image_count": page_images
            })

        # Update analysis
        pdf_analysis["has_text"] = len(full_text.strip()) > 0
        pdf_analysis["has_images"] = total_images > 0
        pdf_analysis["total_images"] = total_images
        pdf_analysis["text_content"] = full_text[:5000] + "..." if len(full_text) > 5000 else full_text
        pdf_analysis["character_count"] = len(full_text)
        pdf_analysis["word_count"] = len(full_text.split())

        doc.close()
        return {"pdf_analysis": pdf_analysis}

    def _extract_with_pypdf2(self, file_path: str) -> Dict[str, Any]:
        """Fallback PDF extraction using PyPDF2."""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            pdf_analysis = {
                "total_pages": len(pdf_reader.pages),
                "extraction_method": "PyPDF2_fallback",
                "text_content": "",
                "has_text": False
            }

            full_text = ""
            for page in pdf_reader.pages:
                try:
                    text = page.extract_text()
                    full_text += text + "\n"
                except:
                    continue

            pdf_analysis["text_content"] = full_text[:5000] + "..." if len(full_text) > 5000 else full_text
            pdf_analysis["has_text"] = len(full_text.strip()) > 0
            pdf_analysis["character_count"] = len(full_text)
            pdf_analysis["word_count"] = len(full_text.split())

            return {"pdf_analysis": pdf_analysis}
