#!/usr/bin/env python3
"""PyPDF Editor - Professional PDF editing tool."""

import sys
import traceback

# Set up logging FIRST before any other imports
from .app.utils.logger import setup_logging, get_logger
logger = setup_logging()
log = get_logger("main")

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt


def exception_hook(exctype, value, tb):
    """Global exception handler."""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    log.critical(f"Unhandled exception: {error_msg}")

    try:
        QMessageBox.critical(
            None,
            "PyPDF Editor Error",
            f"An error occurred:\n\n{value}\n\nCheck logs for details."
        )
    except:
        pass

    sys.exit(1)


def main():
    log.info("Starting PyPDF Editor application...")

    # Install exception hook
    sys.excepthook = exception_hook

    try:
        log.debug("Setting up Qt application...")

        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setApplicationName("PyPDF Editor")
        app.setOrganizationName("PyPDFEditor")

        log.debug("Qt application created successfully")

        log.debug("Importing MainWindow...")
        from .app.main_window import MainWindow

        log.debug("Creating main window...")
        window = MainWindow()

        log.info("Showing main window...")
        window.show()

        # Check if file passed as argument
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            log.info(f"Opening file from argument: {pdf_path}")
            window.open_pdf(pdf_path)

        log.info("Entering Qt event loop...")
        exit_code = app.exec()

        log.info(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        log.critical(f"Startup error: {e}")
        log.critical(traceback.format_exc())
        print(f"\nSTARTUP ERROR: {e}", file=sys.stderr)
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
