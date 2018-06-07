import yaml
import os
from release_ccharp.exceptions import SnpseqReleaseException


class Config:
    def open_config(self, repo):
        here = os.path.dirname(__file__)
        path = os.path.join(here, 'repo.config.txt')
        with open(path, 'r') as f:
            config = yaml.load(f)
        if not repo in config:
            raise SnpseqReleaseException("This repo name is not present in the config file! '{}'".format(self.repo))
        return config[repo]
