"""Page management operations."""

from typing import Optional
from pathlib import Path

from ..editor.pdf_document import PDFDocument
from ..utils.logger import get_logger

log = get_logger("page_manager")


class PageManager:
    """Manages page-level operations on PDFs."""

    def __init__(self, document: Optional[PDFDocument] = None):
        self._document = document

    def set_document(self, document: PDFDocument):
        """Set the document to manage."""
        self._document = document

    def rotate_page(self, index: int, degrees: int):
        """Rotate a page by specified degrees."""
        if self._document:
            self._document.rotate_page(index, degrees)

    def delete_page(self, index: int):
        """Delete a page."""
        if self._document:
            self._document.delete_page(index)

    def move_page(self, from_index: int, to_index: int):
        """Move a page from one position to another."""
        if self._document:
            self._document.move_page(from_index, to_index)

    def insert_blank_page(self, index: int, width: float = 612, height: float = 792):
        """Insert a blank page."""
        if self._document:
            self._document.insert_blank_page(index, width, height)

    def extract_pages(self, indices: list[int], output_path: str) -> bool:
        """Extract pages to a new PDF file."""
        if not self._document:
            return False

        pdf_bytes = self._document.extract_pages(indices)
        if pdf_bytes:
            Path(output_path).write_bytes(pdf_bytes)
            log.info(f"Extracted {len(indices)} pages to {output_path}")
            return True
        return False

    def merge_pdfs(self, paths: list[str], output_path: str) -> bool:
        """Merge multiple PDFs into one."""
        return PDFDocument.merge_pdfs(paths, output_path)

    def split_document(self, output_dir: str, pages_per_file: int = 1) -> list[str]:
        """Split the document into multiple files."""
        if not self._document:
            return []
        return self._document.split_by_pages(output_dir, pages_per_file)
