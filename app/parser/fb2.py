import re
import math
import base64
import traceback
from io import BytesIO
from PIL import Image, ImageFilter
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from .base import *

class FB2Book(Book):

    def __repr__( self ) -> str:
        return str({
            'url': self.url,
            'title': self.title,
            'seria': self.seria,
            'authors': self.authors,
            'chapters': self.chapters,
            'last_chapter': self.last_chapter,
        })

    def __init__( self, book: BytesIO ) -> None:
        super().__init__( book )
        self.convertAuthors()


    def init( self, book: BytesIO ) -> None:
        self._book: Element = ElementTree.parse( book ).getroot()

        for element in self._book.iter():
            element.tag = element.tag.partition('}')[-1]
    
    def parseTitle( self ) -> None:
        _title = self._book.find('./description/title-info/book-title')
        if _title is not None:
            self.title = _title.text

    def parseUrl( self ) -> None:
        _url = self._book.find('./description/document-info/src-url')
        if _url is not None:
            self.url = _url.text

    def parseSeria( self ) -> None:
        _seria = self._book.find('./description/title-info/sequence')
        if _seria is not None:
            self.seria = FB2Seria( _seria )

    def parseAuthors( self ) -> None:
        _authors = self._book.findall('./description/title-info/author')
        for _author in _authors:
            author = FB2Author(_author)
            if author.Name == 'Цокольный этаж':
                continue
            self._authors[ author.Name ] = author

        _authors = self._book.findall('./description/document-info/author')
        for _author in _authors:
            author = FB2Author(_author)
            if author.Name == 'Цокольный этаж':
                continue
            if author.Name in self._authors:
                self._authors[ author.Name ].merge( author )
            else:
                self._authors[ author.Name ] = author

    def parseChapters( self ) -> None:
        _chapters = self._book.findall('./body/section')
        for _chapter in _chapters:
            _title = _chapter.find('./title')
            if _title is not None:
                title_elems = []
                for title_elem in _title.itertext():
                    title_elems.append( title_elem.replace('\n',' ').strip() )
                title = ' '.join( title_elems ).strip()
                if title and title != 'Nota bene' and 'BooksFine' not in title:
                    self.chapters += 1
                    self.last_chapter = title
    
    def parseCover( self ) -> None:
        _cover = self._book.find('./description/title-info/coverpage/image')
        _cover_link = None


        if _cover is not None:
            for attr, value in _cover.attrib.items():
                if attr.endswith('href'):
                    _cover_link = value[1:]


        if _cover_link is not None:
            _cover_file = self._book.find(f'.//*[@id="{_cover_link}"]')
            try:
                _cover_file_bytes = base64.b64decode( _cover_file.text )
                if _cover_file_bytes:
                    self._cover = _cover_file_bytes
            except:
                traceback.print_exc()


        if self._cover is not None:
            try:
                thumb_size = (320, 320)
                with Image.open( BytesIO(self._cover) ) as img_src:
                    img_result = Image.new('RGB', thumb_size)
                    img_src.thumbnail( (320, 320) )
                    img_bg = img_src.copy()

                    left_x = int( ( 320 - img_src.width )/2 )
                    top_y = int( ( 320 - img_src.height )/2 )
                        
                    prop_x = 320/img_src.width
                    prop_y = 320/img_src.height
                    resize_coef = max(prop_x,prop_y)
                    resize_size = math.ceil( 320*resize_coef )
                    
                    img_bg = img_bg.resize( ( resize_size, resize_size ), Image.Resampling.LANCZOS )
                    img_bg = img_bg.filter( ImageFilter.GaussianBlur( 20 ) )
                    
                    img_result.paste( img_bg, ( int(160 - img_bg.width/2), int(160 - img_bg.height/2) ) )
                    img_result.paste( img_src, ( left_x, top_y ) )

                    _data = BytesIO()
                    img_result.save( _data, format="JPEG", optimize=True )
                    _data.seek(0)
                    self._cover = _data.read()
            except:
                traceback.print_exc()
                self._cover = None
        
        if self._cover and len( self._cover ) < 10:
            self._cover = None


    def convertAuthors( self ) -> None:
        for _, author in self._authors.items():

            author_name: str = author.Name
            author_name = author_name.replace( '\n', ' ' )
            author_name = re.sub( r'\s+', ' ', author_name )

            if author.url:
                author_url: str = author.url
                self.authors.append( f'<a href="{author_url}">{author_name}</a>' )
            else:
                self.authors.append( author_name )



class FB2Seria(Seria):
    name: str | None = None
    number: int | None = None

    def __init__( self, data: Element ) -> None:
        super().__init__( data )

    def parse( self, data: Element ) -> None:

        _name = data.attrib.get('name')
        _number = data.attrib.get('number')

        if _name:
            self.name = _name

        if _number:
            self.number = _number


class FB2Author(Author):

    def __init__( self, data: Element ) -> None:
        super().__init__( data )

    def parse( self, data: Element ) -> None:

        last_name = data.find('./last-name')
        first_name = data.find('./first-name')
        middle_name = data.find('./middle-name')
        url = data.find('./home-page')

        if last_name is not None:
            self.last_name = last_name.text

        if first_name is not None:
            self.first_name = first_name.text

        if middle_name is not None:
            self.middle_name = middle_name.text

        if url is not None:
            self.url = url.text