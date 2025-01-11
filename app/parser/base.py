from io import BytesIO
from typing import List, Dict, Any, Self

class Seria:
    name: str | None = None
    number: int | None = None

    def __repr__( self ) -> str:
        number = f' #{self.number}' if self.number else ''
        return f'{self.name}{number}'

    def __init__( self, data: Any ) -> None:
        self.name = None
        self.number = None

        self.parse( data )
    
    def parse( self, data: Any ) -> None:
        pass


class Author:
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    url: str | None = None

    @property
    def Name( self ) -> str:
        if self.middle_name:
            return ' '.join( list( filter( None, [ self.last_name, self.first_name, self.middle_name ] ) ) )
        else:
            return ' '.join( list( filter( None, [ self.first_name, self.last_name ] ) ) )

    def __repr__( self ) -> str:
        fio = ' '.join( list( filter( None, [ self.last_name, self.first_name, self.middle_name ] ) ) )
        url = f' [{self.url}]' if self.url else ''
        return f'{fio}{url}'

    def __init__( self, data: Any ) -> None:
        self.last_name = None
        self.first_name = None
        self.middle_name = None
        self.url = None

        self.parse( data )
    
    def parse( self, data: Any ) -> None:
        pass
    
    def merge( self, new: Self ) -> None:
        if not self.last_name:
            self.last_name = new.last_name
        if not self.first_name:
            self.first_name = new.first_name
        if not self.middle_name:
            self.middle_name = new.middle_name
        if not self.url:
            self.url = new.url


class Book:
    _book: Any
    _cover: bytes = None
    title: str = ''
    url: str | None = None
    chapters: int = 0
    last_chapter: str = ''
    seria: Seria | None = None
    authors: List[ str ] = []
    _authors: Dict[ str, Author ] = {}

    def __init__( self, book: BytesIO ) -> None:
        self.title = ''
        self.url = None
        self.chapters = 0
        self.last_chapter = ''
        self.seria = None
        self.authors = []
        self._authors = {}

        self.init( book )
        self.parse()

    def init( self, book: BytesIO ) -> None:
        pass

    def parse( self ) -> None:
        self.parseUrl()
        self.parseTitle()
        self.parseSeria()
        self.parseAuthors()
        self.parseChapters()
        self.parseCover()

    def parseTitle( self ) -> None:
        pass

    def parseUrl( self ) -> None:
        pass

    def parseSeria( self ) -> None:
        pass

    def parseAuthors( self ) -> None:
        pass

    def parseChapters( self ) -> None:
        pass

    def parseCover( self ) -> None:
        pass