class Scryfall:
    def __init__(self, config):
        self.base_url = config.get('base_url', fallback='https://api.scryfall.com')
        self.request_delay = config.getfloat('request_delay', fallback=0.1)
