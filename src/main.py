"""Momir Basic Printer - Command-line interface for printing Magic: The Gathering cards.

This module provides an interactive CLI for:
- Viewing card database information
- Refreshing card data from Scryfall
- Printing random cards by converted mana cost (CMC)
"""

import configparser
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Command constants
CMD_INFO = frozenset(['i', 'info'])
CMD_REFRESH = frozenset(['r', 'refresh'])
CMD_PRINT = frozenset(['p', 'print'])
CMD_QUIT = frozenset(['q', 'quit'])

# Prompt strings
PROMPT_MAIN = "~/MBP/MAIN: "
PROMPT_PRINT = "~/MBP/PRINT: "

# Configuration
config = configparser.ConfigParser()
config_file = Path(__file__).resolve().with_name('config.ini')

if not config_file.exists():
    raise FileNotFoundError(f"Configuration file not found: {config_file}")

config.read(config_file)

# Validate required sections exist
required_sections = ['FILESYSTEM', 'LOGGING', 'PRINTER', 'SCRYFALL']
missing_sections = [
    section for section in required_sections if section not in config]
if missing_sections:
    raise ValueError(
        f"Missing required configuration sections: {', '.join(missing_sections)}")

filesystem_config = config['FILESYSTEM']
logging_config = config['LOGGING']
printer_config = config['PRINTER']
scryfall_config = config['SCRYFALL']

# Logging setup
logger = logging.getLogger('momir.main')
logging.basicConfig(
    level=logging_config.get('log_level').upper(),
    format=logging_config.get('log_format'),
    datefmt=logging_config.get('log_date_format'),
    stream=sys.stdout,
    force=True,
)

# Runtime services (initialized lazily with graceful error handling)
printer: Optional[Any] = None
scryfall: Optional[Any] = None


def initialize_services() -> None:
    """Initialize printer and Scryfall services without crashing the app.

    Services that fail to initialize are disabled, allowing unrelated commands
    to continue working.
    """
    global printer, scryfall

    try:
        # Import local modules after logging is configured so import-time logs are visible.
        from printer import Printer
        printer = Printer(printer_config, filesystem_config)
        logger.info("Printer service initialized.")
    except Exception as exc:
        printer = None
        logger.error(f"Printer service unavailable: {exc}")

    try:
        from scryfall import Scryfall
        scryfall = Scryfall(scryfall_config, filesystem_config)
        logger.info("Scryfall service initialized.")
    except Exception as exc:
        scryfall = None
        logger.error(f"Scryfall service unavailable: {exc}")


def print_card_info(metadata: Dict[str, Any]) -> None:
    """Display card database information.

    Args:
        metadata: Metadata dictionary containing database statistics
    """
    logger.info(f"Last updated at: {metadata.get('updated_at')}")
    logger.info(f"Total card count: {metadata.get('total_card_count')} cards")
    logger.info("CMC card counts:")
    for cmc, count in metadata.get('cmc_card_count', {}).items():
        logger.info(f"  CMC {cmc}: {count} cards")


def print_loop() -> None:
    """Interactive loop for printing cards by CMC.

    Prompts user for CMC values and prints random cards with that CMC.
    Loop continues until user exits with Ctrl+C/Ctrl+D.
    """
    logger.info("Entering print mode. Enter CMC values to print random cards.")
    logger.info("Press Ctrl+C or Ctrl+D to return to main menu.")

    if scryfall is None:
        logger.error("Print mode unavailable: Scryfall service is not initialized.")
        return

    if printer is None:
        logger.error("Print mode unavailable: Printer service is not initialized.")
        return

    while True:
        try:
            user_input = input(PROMPT_PRINT).strip()

            # Validate input
            try:
                cmc = int(user_input)
                if cmc < 0:
                    logger.warning("CMC must be non-negative.")
                    continue
            except ValueError:
                logger.warning(
                    f"Invalid input: '{user_input}'. Please enter a valid CMC number.")
                continue

            # Fetch and print card
            logger.debug(f"Fetching card with CMC: {cmc}...")
            card = scryfall.get_random_card_by_cmc(cmc)

            if card is None:
                logger.warning(f"No cards found with CMC {cmc}.")
                continue

            logger.debug(f"Fetched card: {card['name']}. Printing...")
            printer.print_card(card)

        except (KeyboardInterrupt, EOFError):
            logger.debug("Exiting print loop...")
            print()  # New line after interrupt
            break
        except Exception as e:
            logger.error(f"Error during print operation: {e}")


def main() -> None:
    """Main command loop for the Momir Basic Printer application.

    Provides interactive menu for:
    - Viewing database information
    - Refreshing card data
    - Printing cards
    - Quitting the application
    """
    logger.info("Momir Basic Printer started.")
    logger.info("Available commands: (i)nfo, (r)efresh, (p)rint, (q)uit")

    initialize_services()

    while True:
        try:
            command = input(PROMPT_MAIN).strip().lower()

            if command in CMD_INFO:
                logger.debug("Received info command.")
                if scryfall is None:
                    logger.error("Info unavailable: Scryfall service is not initialized.")
                    continue
                metadata = scryfall.get_metadata()
                print_card_info(metadata)

            elif command in CMD_REFRESH:
                logger.debug(
                    "Received refresh command. Refreshing card data...")
                if scryfall is None:
                    logger.error("Refresh unavailable: Scryfall service is not initialized.")
                    continue
                scryfall.refresh_card_data(force_full_refresh=False)
                logger.info("Card data refresh complete.")

            elif command in CMD_PRINT:
                logger.debug("Received print command.")
                print_loop()

            elif command in CMD_QUIT:
                logger.debug("Received quit command. Exiting...")
                break

            elif command:
                logger.warning(
                    f"Unknown command: '{command}'. Available: info, refresh, print, quit")

        except (KeyboardInterrupt, EOFError):
            logger.debug("Received exit signal. Exiting...")
            print()  # New line after interrupt
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")

    logger.info("Momir Basic Printer stopped.")


if __name__ == "__main__":
    main()
