from typing import Callable

# parce qu'il gere une pagination presque comme une patator
class Paginatator():
    def __init__(self):
        self.minPage=1
        self.maxPage=10
        self.currentPage=1
        self.width=10
        self.calc()

    def setMinPage(self, _minPage:int):
        self.minPage=_minPage
        self.currentPage=min(self.maxPage, max(self.minPage,self.currentPage))
        self.calc()

    def setMaxPage(self, _maxPage:int):
        self.maxPage=_maxPage
        self.currentPage=min(self.maxPage, max(self.minPage,self.currentPage))
        self.calc()

    def setWidth(self, _width:int):
        self.width=_width
        self.calc()

    def setCurrentPage(self, _currentPage:int):
        self.currentPage=min(self.maxPage, max(self.minPage,_currentPage))
        self.calc()

    def calc(self):
        self.begin = max(min(int(self.currentPage-self.width/2), self.maxPage-self.width+1),self.minPage)
        self.end = min(self.begin + self.width, self.maxPage+1)

    def generateFirst(self, generator:Callable[[int, int], any]):
        return generator(self.minPage, self.currentPage)
    
    def generatePrevious(self, generator:Callable[[int, int], any]):
        return generator(max(self.minPage, self.currentPage-1),self.currentPage)
    
    def generateNext(self, generator:Callable[[int, int], any]):
        return generator(min(self.maxPage, self.currentPage+1),self.currentPage)
    
    def generateLast(self, generator:Callable[[int, int], any]):
        return generator(self.maxPage,self.currentPage)
    
    def generateRange(self, generator:Callable[[int, int], any]):
        return list(map(lambda i:generator(i,self.currentPage), range(self.begin, self.end)))
    