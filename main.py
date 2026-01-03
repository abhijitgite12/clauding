#!/usr/bin/env python3
"""PySnagit - Full-featured screen capture and editing tool."""

import sys
import traceback

# Set up logging FIRST before any other imports
from app.utils.logger import setup_logging, get_logger
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
            "PySnagit Error",
            f"An error occurred:\n\n{value}\n\nCheck logs for details."
        )
    except:
        pass

    sys.exit(1)


def main():
    log.info("Starting PySnagit application...")

    # Install exception hook
    sys.excepthook = exception_hook

    try:
        log.debug("Setting up Qt application...")

        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setApplicationName("PySnagit")
        app.setOrganizationName("PySnagit")
        app.setQuitOnLastWindowClosed(False)

        log.debug("Qt application created successfully")

        log.debug("Importing MainWindow...")
        from app.main_window import MainWindow

        log.debug("Creating main window...")
        window = MainWindow()

        log.info("Showing main window...")
        window.show()

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
