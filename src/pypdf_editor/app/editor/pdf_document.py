"""PDF document wrapper using PyMuPDF (fitz)."""

from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

import fitz  # PyMuPDF
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

from ..utils.logger import get_logger

log = get_logger("pdf_document")


@dataclass
class SearchResult:
    """Represents a text search result."""
    page: int
    rect: fitz.Rect
    text: str


@dataclass
class OutlineItem:
    """Represents a bookmark/outline item."""
    title: str
    page: int
    level: int


class PDFDocument(QObject):
    """Wrapper around fitz.Document with Qt signals."""

    # Signals
    document_loaded = pyqtSignal(str)  # path
    document_modified = pyqtSignal()
    document_saved = pyqtSignal(str)  # path
    page_count_changed = pyqtSignal(int)

    def __init__(self, path: Optional[str] = None):
        super().__init__()
        self._doc: Optional[fitz.Document] = None
        self._path: Optional[Path] = None
        self._modified = False
        self._page_cache: dict[tuple[int, float], QPixmap] = {}
        self._cache_max_size = 20

        if path:
            self.open(path)

    @property
    def is_open(self) -> bool:
        """Check if a document is open."""
        return self._doc is not None

    @property
    def path(self) -> Optional[Path]:
        """Get the current document path."""
        return self._path

    @property
    def filename(self) -> str:
        """Get the document filename."""
        return self._path.name if self._path else "Untitled"

    @property
    def page_count(self) -> int:
        """Get the number of pages."""
        return len(self._doc) if self._doc else 0

    @property
    def is_modified(self) -> bool:
        """Check if document has unsaved changes."""
        return self._modified

    @property
    def metadata(self) -> dict:
        """Get document metadata."""
        if not self._doc:
            return {}
        return self._doc.metadata

    def open(self, path: str) -> bool:
        """Open a PDF file."""
        try:
            self.close()
            self._doc = fitz.open(path)
            self._path = Path(path)
            self._modified = False
            self._page_cache.clear()
            log.info(f"Opened PDF: {path} ({self.page_count} pages)")
            self.document_loaded.emit(str(path))
            return True
        except Exception as e:
            log.error(f"Failed to open PDF: {e}")
            return False

    def save(self, path: Optional[str] = None) -> bool:
        """Save the PDF file."""
        if not self._doc:
            return False

        try:
            save_path = Path(path) if path else self._path
            if not save_path:
                return False

            # Save with optimization
            self._doc.save(
                str(save_path),
                garbage=4,
                deflate=True,
                clean=True
            )
            self._path = save_path
            self._modified = False
            log.info(f"Saved PDF: {save_path}")
            self.document_saved.emit(str(save_path))
            return True
        except Exception as e:
            log.error(f"Failed to save PDF: {e}")
            return False

    def save_as(self, path: str) -> bool:
        """Save the PDF to a new location."""
        return self.save(path)

    def close(self):
        """Close the document."""
        if self._doc:
            self._doc.close()
            self._doc = None
            self._path = None
            self._modified = False
            self._page_cache.clear()
            log.info("Closed PDF document")

    def get_page(self, index: int) -> Optional[fitz.Page]:
        """Get a page by index."""
        if self._doc and 0 <= index < len(self._doc):
            return self._doc[index]
        return None

    def get_page_size(self, index: int) -> tuple[float, float]:
        """Get page dimensions (width, height) in points."""
        page = self.get_page(index)
        if page:
            rect = page.rect
            return rect.width, rect.height
        return 0, 0

    def get_page_pixmap(
        self,
        index: int,
        zoom: float = 1.0,
        use_cache: bool = True
    ) -> QPixmap:
        """Render a page to QPixmap."""
        cache_key = (index, round(zoom, 2))

        # Check cache
        if use_cache and cache_key in self._page_cache:
            return self._page_cache[cache_key]

        page = self.get_page(index)
        if not page:
            return QPixmap()

        # Render page
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert to QImage then QPixmap
        img = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(img)

        # Cache with size limit
        if use_cache:
            if len(self._page_cache) >= self._cache_max_size:
                # Remove oldest entry
                oldest_key = next(iter(self._page_cache))
                del self._page_cache[oldest_key]
            self._page_cache[cache_key] = pixmap

        return pixmap

    def get_thumbnail(self, index: int, max_size: int = 150) -> QPixmap:
        """Get a thumbnail of a page."""
        page = self.get_page(index)
        if not page:
            return QPixmap()

        # Calculate zoom to fit max_size
        rect = page.rect
        scale = max_size / max(rect.width, rect.height)

        return self.get_page_pixmap(index, scale, use_cache=False)

    def clear_cache(self):
        """Clear the page render cache."""
        self._page_cache.clear()

    # Text operations
    def get_page_text(self, index: int) -> str:
        """Get text content of a page."""
        page = self.get_page(index)
        if page:
            return page.get_text()
        return ""

    def search_text(
        self,
        query: str,
        page_index: Optional[int] = None,
        case_sensitive: bool = False
    ) -> list[SearchResult]:
        """Search for text in the document."""
        results = []
        if not self._doc or not query:
            return results

        flags = 0 if case_sensitive else fitz.TEXT_PRESERVE_WHITESPACE

        pages = [page_index] if page_index is not None else range(len(self._doc))

        for idx in pages:
            page = self._doc[idx]
            rects = page.search_for(query, flags=flags)
            for rect in rects:
                results.append(SearchResult(
                    page=idx,
                    rect=rect,
                    text=query
                ))

        log.debug(f"Found {len(results)} results for '{query}'")
        return results

    # Outline/Bookmarks
    def get_outline(self) -> list[OutlineItem]:
        """Get document outline (bookmarks/TOC)."""
        if not self._doc:
            return []

        items = []
        toc = self._doc.get_toc()
        for level, title, page in toc:
            items.append(OutlineItem(
                title=title,
                page=page - 1,  # Convert to 0-based
                level=level
            ))
        return items

    # Page operations
    def rotate_page(self, index: int, degrees: int):
        """Rotate a page by degrees (90, 180, 270)."""
        page = self.get_page(index)
        if page:
            current = page.rotation
            page.set_rotation((current + degrees) % 360)
            self._mark_modified()
            # Clear cache for this page
            keys_to_remove = [k for k in self._page_cache if k[0] == index]
            for k in keys_to_remove:
                del self._page_cache[k]
            log.info(f"Rotated page {index} by {degrees} degrees")

    def delete_page(self, index: int):
        """Delete a page."""
        if self._doc and 0 <= index < len(self._doc):
            self._doc.delete_page(index)
            self._mark_modified()
            self._page_cache.clear()
            self.page_count_changed.emit(len(self._doc))
            log.info(f"Deleted page {index}")

    def insert_blank_page(
        self,
        index: int,
        width: float = 612,
        height: float = 792
    ):
        """Insert a blank page at index (default US Letter size)."""
        if self._doc:
            self._doc.insert_page(index, width=width, height=height)
            self._mark_modified()
            self._page_cache.clear()
            self.page_count_changed.emit(len(self._doc))
            log.info(f"Inserted blank page at index {index}")

    def move_page(self, from_index: int, to_index: int):
        """Move a page from one position to another."""
        if not self._doc:
            return
        if 0 <= from_index < len(self._doc) and 0 <= to_index < len(self._doc):
            self._doc.move_page(from_index, to_index)
            self._mark_modified()
            self._page_cache.clear()
            log.info(f"Moved page {from_index} to {to_index}")

    def extract_pages(self, indices: list[int]) -> Optional[bytes]:
        """Extract pages to a new PDF (returns bytes)."""
        if not self._doc:
            return None

        try:
            new_doc = fitz.open()
            for idx in sorted(indices):
                if 0 <= idx < len(self._doc):
                    new_doc.insert_pdf(
                        self._doc,
                        from_page=idx,
                        to_page=idx
                    )

            pdf_bytes = new_doc.tobytes(garbage=4, deflate=True)
            new_doc.close()
            return pdf_bytes
        except Exception as e:
            log.error(f"Failed to extract pages: {e}")
            return None

    # Annotations
    def get_annotations(self, page_index: int) -> list[Any]:
        """Get annotations on a page."""
        page = self.get_page(page_index)
        if not page:
            return []
        return list(page.annots())

    def add_highlight(
        self,
        page_index: int,
        rect: fitz.Rect,
        color: tuple[float, float, float] = (1, 1, 0)
    ):
        """Add a highlight annotation."""
        page = self.get_page(page_index)
        if page:
            annot = page.add_highlight_annot(rect)
            annot.set_colors(stroke=color)
            annot.update()
            self._mark_modified()

    def add_text_annotation(
        self,
        page_index: int,
        rect: fitz.Rect,
        text: str,
        color: tuple[float, float, float] = (1, 1, 0)
    ):
        """Add a sticky note annotation."""
        page = self.get_page(page_index)
        if page:
            annot = page.add_text_annot(rect.tl, text)
            annot.set_colors(stroke=color)
            annot.update()
            self._mark_modified()

    def add_freetext(
        self,
        page_index: int,
        rect: fitz.Rect,
        text: str,
        fontsize: int = 12,
        color: tuple[float, float, float] = (0, 0, 0)
    ):
        """Add a free text annotation."""
        page = self.get_page(page_index)
        if page:
            annot = page.add_freetext_annot(
                rect,
                text,
                fontsize=fontsize,
                text_color=color
            )
            annot.update()
            self._mark_modified()

    def delete_annotation(self, page_index: int, annot):
        """Delete an annotation from a page."""
        page = self.get_page(page_index)
        if page:
            page.delete_annot(annot)
            self._mark_modified()

    # Form fields
    def get_form_fields(self, page_index: int) -> list[dict]:
        """Get form fields on a page."""
        page = self.get_page(page_index)
        if not page:
            return []

        fields = []
        widgets = page.widgets()
        if widgets:
            for widget in widgets:
                fields.append({
                    'name': widget.field_name,
                    'type': widget.field_type,
                    'value': widget.field_value,
                    'rect': widget.rect,
                    'widget': widget
                })
        return fields

    def set_form_field_value(self, widget, value: str):
        """Set a form field value."""
        try:
            widget.field_value = value
            widget.update()
            self._mark_modified()
        except Exception as e:
            log.error(f"Failed to set form field value: {e}")

    # Merge/Split
    @staticmethod
    def merge_pdfs(paths: list[str], output_path: str) -> bool:
        """Merge multiple PDFs into one."""
        try:
            merged = fitz.open()
            for path in paths:
                doc = fitz.open(path)
                merged.insert_pdf(doc)
                doc.close()

            merged.save(output_path, garbage=4, deflate=True)
            merged.close()
            log.info(f"Merged {len(paths)} PDFs to {output_path}")
            return True
        except Exception as e:
            log.error(f"Failed to merge PDFs: {e}")
            return False

    def split_by_pages(
        self,
        output_dir: str,
        pages_per_file: int = 1
    ) -> list[str]:
        """Split PDF into multiple files."""
        if not self._doc:
            return []

        output_paths = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        total = len(self._doc)
        file_num = 1

        for start in range(0, total, pages_per_file):
            end = min(start + pages_per_file, total)

            new_doc = fitz.open()
            new_doc.insert_pdf(self._doc, from_page=start, to_page=end - 1)

            name = self._path.stem if self._path else "split"
            out_file = output_path / f"{name}_part{file_num}.pdf"
            new_doc.save(str(out_file), garbage=4, deflate=True)
            new_doc.close()

            output_paths.append(str(out_file))
            file_num += 1

        log.info(f"Split PDF into {len(output_paths)} files")
        return output_paths

    def _mark_modified(self):
        """Mark document as modified."""
        self._modified = True
        self.document_modified.emit()
