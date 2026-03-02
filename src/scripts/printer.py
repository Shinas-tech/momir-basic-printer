class Printer:
    def __init__(self, config):
        self.print_speed = config.get('print_speed', fallback=5)
        self.paper_width_mm = config.getint('paper_width_mm', fallback=58)
        self.dpi = config.getint('dpi', fallback=300)
