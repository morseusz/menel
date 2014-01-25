import itertools
from scrappers import *
from menel.scrappers import BaseScrapper


def get_all_scrappers():
    scrappers = []
    globs = globals()
    for g in globs:
        cls = globs[g]
        try:
            if issubclass(cls, BaseScrapper):
                scrappers.append(cls())
        except TypeError:
            pass
    return scrappers


def get_independent(scrappers):
    independent = []
    for scrapper in scrappers:
        if not scrapper.requires:
            independent.append(scrapper)

    for i in independent:
        scrappers.remove(i)

    return independent