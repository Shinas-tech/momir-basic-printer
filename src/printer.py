import sys
from pathlib import Path
import os
import sys
import textwrap
from escpos.printer import Network
import logging
logger = logging.getLogger(__name__)

class Printer:
    def __init__(self, printer_config, filesystem_config, logging_config):
        self.paper_width_mm = printer_config.getint('paper_width_mm')
        self.paper_width_chars = printer_config.getint('paper_width_chars')
        self.card_art_enabled = printer_config.getboolean('card_art_enabled')
        self.qr_code_enabled = printer_config.getboolean('qr_code_enabled')
        self.qr_code_size = printer_config.getint('qr_code_size')
        self.dpi = printer_config.getint('dpi')
        self.vendor_id = int(printer_config.get('vendor_id'), 0)
        self.product_id = int(printer_config.get('product_id'), 0)
        self.cards_path = Path(sys.argv[0]).resolve().parent.parent / filesystem_config.get('cards_path')
        self.art_path = Path(sys.argv[0]).resolve().parent.parent / filesystem_config.get('art_path')
        self.default_card_art_path = Path(sys.argv[0]).resolve().parent.parent / filesystem_config.get('default_card_art_path')
        self.access_rights = int(filesystem_config.get('access_rights'), 0)
        logging.basicConfig(level=logging_config.get('log_level').upper(),
                            format=logging_config.get('log_format'))

    def clean_text(self, text):
        return (text.replace('—', '-')
                    .replace('–', '-')
                    .replace('’', "'")
                    .replace('“', '"')
                    .replace('”', '"'))

    def print_card(self, card):
        card_name = self.clean_text(card["name"])
        card_mana_cost = card["mana_cost"]
        card_scryfall_uri = card["scryfall_uri"]
        card_art_path = os.path.join(self.art_path, f"{card['id']}.jpg")
        card_type_line = self.clean_text(card["type_line"])
        card_oracle_text = self.clean_text(card["oracle_text"])
        card_power = card["power"]
        card_toughness = card["toughness"]

        logger.debug(f"Printing card: {card_name}...")
        printer = Network("127.0.0.1", port=9100, profile="simple")
        
        # NAME AND MANA COST
        printer.set(align='left', bold=True)
        title_line_spaces = self.paper_width_chars - (len(card_name) + len(card_mana_cost))
        title_line_padding = " " * max(1, title_line_spaces)
        printer.text(f"{card_name}{title_line_padding}{card_mana_cost}\n")

        # ART
        printer.set(align='center', bold=False)
        if self.card_art_enabled:
            printer.text(f"\n")
            printer.image(card_art_path)
            printer.text(f"\n")

        # TYPE LINE
        printer.text(f"\n{card_type_line}\n\n")

        # ORACLE TEXT
        printer.set(align='left', bold=False)
        for paragraph in card_oracle_text.split('\n'):
            if paragraph.strip():
                wrapped = textwrap.fill(paragraph, width=self.paper_width_chars)
                printer.text(wrapped + "\n\n")
            else:
                printer.text("\n")

        # POWER / TOUGHNESS
        printer.set(align='right', bold=False)
        printer.text(f"{card_power} / {card_toughness}\n")

        # QR CODE
        printer.set(align='center', bold=False)
        if self.qr_code_enabled:
            printer.qr(card_scryfall_uri, size=self.qr_code_size)

        printer.cut()
        logger.debug(f"Printed card: {card_name}.")
