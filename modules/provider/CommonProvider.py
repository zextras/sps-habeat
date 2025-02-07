import logging


class CommonProvider:

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def check(self, hostname):
        pass
