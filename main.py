"""
=============================================================================
SmartFM - Smart Fleet Management System
=============================================================================
Subject:        SWE30003 - Software Architectures and Design
Assignment:     3 - Object Design Implementation and Reflection
Prepared for:   ABC-Trans Vietnam
Prepared by:    Swinsoft Consulting
Semester:       May, 2026

Description:
    Main entry point for the SmartFM application.
    This module initialises the SmartFMSystem (bootstrap controller)
    and launches the main menu user interface.

    Coding Standard: PEP 8 - Style Guide for Python Code
    Reference: G. van Rossum, B. Warsaw, and N. Coghlan, "PEP 8 - Style
    Guide for Python Code," Python Software Foundation, 2001.
    Available: https://peps.python.org/pep-0008/

Business Areas Implemented:
    1. Customer Account Registration and Login
    2. Browse and Place a Shipment Order
    3. Vehicle and Driver Management (Fleet)
    4. Assign Vehicle and Driver to Order

Platform:
    - Language : Python 3.10+
    - UI       : Text-based (terminal)
    - Storage  : JSON files (data/ folder)
=============================================================================
"""

import sys
import os

# ---------------------------------------------------------------------------
# Make sure all subfolders are importable regardless of working directory
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for subfolder in ("system", "managers", "services", "models", "storage", "ui"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

# ---------------------------------------------------------------------------
# Local imports
# ---------------------------------------------------------------------------
from system.smartfm_system import SmartFMSystem
from ui.main_menu import MainMenu


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_NAME    = "SmartFM - Smart Fleet Management System"
APP_VERSION = "1.0.0"
DIVIDER     = "=" * 60


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def print_banner() -> None:
    """Print the application startup banner to the terminal."""
    print()
    print(DIVIDER)
    print(f"  {APP_NAME}")
    print(f"  Version : {APP_VERSION}")
    print(f"  Client  : ABC-Trans Vietnam")
    print(f"  Vendor  : Swinsoft Consulting")
    print(DIVIDER)
    print()


def print_shutdown() -> None:
    """Print a shutdown message when the application exits."""
    print()
    print(DIVIDER)
    print("  SmartFM has shut down. Goodbye!")
    print(DIVIDER)
    print()


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
def bootstrap() -> SmartFMSystem:
    """
    Initialise the SmartFMSystem and all its subsystems.

    Returns:
        SmartFMSystem: The fully initialised top-level system controller.

    Following the Creator heuristic (Larman, 2004), SmartFMSystem is
    responsible for creating and wiring all manager and service instances.
    """
    print("  Initialising SmartFM subsystems...")
    system = SmartFMSystem()
    system.initialise()
    print("  All subsystems ready.")
    print()
    return system


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """
    Application entry point.

    Execution flow:
        1. Print startup banner
        2. Bootstrap SmartFMSystem (creates all managers and services)
        3. Launch the MainMenu UI loop
        4. Print shutdown message on exit
    """
    print_banner()

    try:
        # Step 1 - Bootstrap all subsystems via SmartFMSystem
        system = bootstrap()

        # Step 2 - Hand control to the MainMenu UI
        menu = MainMenu(system)
        menu.run()

    except KeyboardInterrupt:
        # Allow Ctrl+C to exit cleanly without a traceback
        pass

    finally:
        print_shutdown()


# ---------------------------------------------------------------------------
# Entry point guard
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()