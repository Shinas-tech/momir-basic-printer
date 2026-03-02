import configparser
from printer import Printer
from scryfall import Scryfall

config = configparser.ConfigParser()
config.read('config.ini')

printer = Printer(config['PRINTER'])
scryfall = Scryfall(config['SCRYFALL'])
