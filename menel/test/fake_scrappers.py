import menel.scrappers


class ScrapperToList:
    lst = []
    ident = None

    def __eq__(self, other):
        if self.ident != other.ident:
            return False
        if type(self) != type(other):
            return False
        return True

    def scrape_all(self):
        self.lst.append(self.ident)


class ScrapperA(ScrapperToList, menel.scrappers.BaseScrapper):
    ident = 'A'


class ScrapperB(ScrapperToList, menel.scrappers.BaseScrapper):
    ident = 'B'
    requires = [ScrapperA]


class ScrapperC(ScrapperToList, menel.scrappers.BaseScrapper):
    ident = 'C'
    requires = [ScrapperA]


class ScrapperD(ScrapperToList, menel.scrappers.BaseScrapper):
    ident = 'D'
    requires = [ScrapperB, ScrapperC]


class NotAScrapper:
    pass