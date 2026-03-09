"""Thermal printer interface for printing Magic: The Gathering cards."""

import logging
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional

from escpos.printer import Network
from PIL import Image

logger = logging.getLogger('momir.printer')


class Printer:
    """Thermal printer interface for printing Magic: The Gathering cards.

    This class handles:
    - Formatting card data for thermal printer output
    - Printing card images, text, and QR codes
    - Text cleaning and wrapping for proper display
    """

    # Printer network constants
    DEFAULT_PRINTER_HOST = "127.0.0.1"
    DEFAULT_PRINTER_PORT = 9100
    DEFAULT_PRINTER_PROFILE = "simple"

    # Text formatting constants
    MIN_TITLE_SPACING = 1
    PARAGRAPH_SPACING = "\n\n"

    # Character replacements for printer compatibility
    TEXT_REPLACEMENTS = {
        '\u2014': '-',  # em dash
        '\u2013': '-',  # en dash
        '\u2019': "'",  # right single quotation mark
        '\u201c': '"',  # left double quotation mark
        '\u201d': '"'   # right double quotation mark
    }

    def __init__(self, printer_config, filesystem_config) -> None:
        """Initialize printer with configuration.

        Args:
            printer_config: Configuration section for printer settings
            filesystem_config: Configuration section for filesystem paths
        """
        # Printer configuration
        self.paper_width_mm: int = printer_config.getint('paper_width_mm')
        self.paper_width_chars: int = printer_config.getint(
            'paper_width_chars')
        self.card_art_enabled: bool = printer_config.getboolean(
            'card_art_enabled')
        self.qr_code_enabled: bool = printer_config.getboolean(
            'qr_code_enabled')
        self.qr_code_size: int = printer_config.getint('qr_code_size')
        self.dpi: int = printer_config.getint('dpi')
        self.vendor_id: int = int(printer_config.get('vendor_id'), 0)
        self.product_id: int = int(printer_config.get('product_id'), 0)

        # Network configuration
        self.printer_host: str = printer_config.get(
            'printer_host', fallback=self.DEFAULT_PRINTER_HOST)
        self.printer_port: int = printer_config.getint(
            'printer_port', fallback=self.DEFAULT_PRINTER_PORT)
        self.printer_profile: str = printer_config.get(
            'printer_profile', fallback=self.DEFAULT_PRINTER_PROFILE)
        self.printer_media_width_px: Optional[int] = printer_config.getint(
            'printer_media_width_px', fallback=None)

        # Filesystem paths (use __file__ for reliability)
        base_path = Path(__file__).resolve().parent.parent
        self.cards_path: Path = base_path / filesystem_config.get('cards_path')
        self.art_path: Path = base_path / filesystem_config.get('art_path')
        self.default_card_art_path: Path = base_path / \
            filesystem_config.get('default_card_art_path')
        self.access_rights: int = int(
            filesystem_config.get('access_rights'), 0)

        # Ensure runtime directories exist so app can boot on a fresh install.
        self.cards_path.mkdir(parents=True, exist_ok=True, mode=self.access_rights)
        self.art_path.mkdir(parents=True, exist_ok=True, mode=self.access_rights)

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate critical configuration values on initialization.

        Raises:
            ValueError: If critical configuration is missing or invalid
        """
        if self.paper_width_chars <= 0:
            raise ValueError(
                f"paper_width_chars must be positive, got {self.paper_width_chars}")

        if self.qr_code_size <= 0:
            raise ValueError(
                f"qr_code_size must be positive, got {self.qr_code_size}")

        if self.printer_media_width_px is not None and self.printer_media_width_px <= 0:
            raise ValueError(
                "printer_media_width_px must be positive when provided")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"Printer(host='{self.printer_host}', "
                f"port={self.printer_port}, "
            f"profile='{self.printer_profile}', "
            f"paper_width_chars={self.paper_width_chars})")

    def clean_text(self, text: str) -> str:
        """Clean text for thermal printer compatibility.

        Replaces special Unicode characters with ASCII equivalents
        that the thermal printer can handle.

        Args:
            text: Input text to clean

        Returns:
            Cleaned text with replaced characters
        """
        cleaned = text
        for old_char, new_char in self.TEXT_REPLACEMENTS.items():
            cleaned = cleaned.replace(old_char, new_char)
        return cleaned

    def _get_printer_connection(self) -> Network:
        """Create and return a printer network connection.

        Returns:
            Network printer connection object

        Raises:
            Exception: If connection to printer fails
        """
        try:
            printer = Network(
                self.printer_host,
                port=self.printer_port,
                profile=self.printer_profile,
            )

            # Optional override for profile media width in pixels.
            if self.printer_media_width_px is not None:
                profile_data = printer.profile.profile_data
                media = profile_data.setdefault("media", {})
                width = media.setdefault("width", {})
                width["pixels"] = str(self.printer_media_width_px)

            return printer
        except Exception as e:
            logger.error(
                f"Failed to connect to printer at {self.printer_host}:{self.printer_port}: {e}")
            raise

    def _get_printer_max_width_px(self, printer: Network) -> Optional[int]:
        """Read max printable image width (pixels) from the active printer profile.

        Args:
            printer: Connected network printer instance

        Returns:
            Max width in pixels, or None if unavailable
        """
        try:
            pixels_value = printer.profile.profile_data["media"]["width"]["pixels"]
            return int(pixels_value)
        except (KeyError, TypeError, ValueError):
            return None

    def _print_card_art(self, printer: Network, card_art_path: Path) -> None:
        """Print card art, resizing if needed to fit printer width.

        Args:
            printer: Connected network printer instance
            card_art_path: Path to card art image
        """
        max_width_px = self._get_printer_max_width_px(printer)

        if max_width_px is not None:
            with Image.open(card_art_path) as img:
                if img.width > max_width_px:
                    # Scale down to printer width while preserving aspect ratio.
                    scale = max_width_px / float(img.width)
                    target_height = max(1, int(img.height * scale))
                    img = img.resize((max_width_px, target_height), Image.Resampling.LANCZOS)
                    logger.debug(
                        f"Resized card art for printer width: {card_art_path.name} "
                        f"({img.width}x{img.height})"
                    )
                printer.image(img.copy())
            return

        printer.image(str(card_art_path))

    def print_card(self, card: Dict[str, Any]) -> None:
        """Print a Magic: The Gathering card to the thermal printer.

        Prints formatted card information including:
        - Name and mana cost
        - Card artwork (if enabled)
        - Type line
        - Oracle text (wrapped to paper width)
        - Power/toughness (for creatures)
        - QR code linking to Scryfall page (if enabled)

        Args:
            card: Card data dictionary containing card information

        Raises:
            Exception: If printing fails
        """
        # Extract and clean card data
        card_name = self.clean_text(card.get("name") or "Unknown Card")
        card_mana_cost = card.get("mana_cost") or ""
        card_scryfall_uri = card.get("scryfall_uri") or ""
        card_id = card.get("id")
        card_art_path: Optional[Path] = (
            self.art_path / f"{card_id}.jpg") if card_id else None
        card_type_line = self.clean_text(card.get("type_line") or "")
        card_oracle_text = self.clean_text(card.get("oracle_text") or "")
        card_power = card.get("power")
        card_toughness = card.get("toughness")

        logger.debug(f"Printing card: {card_name}...")

        try:
            printer = self._get_printer_connection()

            # NAME AND MANA COST
            printer.set(align='left', bold=True)
            title_line_spaces = max(
                self.MIN_TITLE_SPACING,
                self.paper_width_chars - (len(card_name) + len(card_mana_cost))
            )
            title_line_padding = " " * title_line_spaces
            printer.text(f"{card_name}{title_line_padding}{card_mana_cost}\n")

            # ART
            printer.set(align='center', bold=False)
            if self.card_art_enabled and card_art_path and card_art_path.exists():
                printer.text("\n")
                self._print_card_art(printer, card_art_path)
                printer.text("\n")

            # TYPE LINE
            if card_type_line:
                printer.text(f"\n{card_type_line}\n\n")

            # ORACLE TEXT
            if card_oracle_text:
                printer.set(align='left', bold=False)
                for paragraph in card_oracle_text.split('\n'):
                    if paragraph.strip():
                        wrapped = textwrap.fill(
                            paragraph, width=self.paper_width_chars)
                        printer.text(wrapped + self.PARAGRAPH_SPACING)
                    else:
                        printer.text("\n")

            # POWER / TOUGHNESS
            if card_power is not None and card_toughness is not None:
                printer.set(align='right', bold=False)
                printer.text(f"{card_power} / {card_toughness}\n")

            # QR CODE
            printer.set(align='center', bold=False)
            if self.qr_code_enabled and card_scryfall_uri:
                printer.qr(card_scryfall_uri, size=self.qr_code_size)

            printer.cut()
            logger.info(f"Successfully printed: {card_name}")

        except Exception as e:
            logger.error(f"Failed to print card {card_name}: {e}")
            raise
