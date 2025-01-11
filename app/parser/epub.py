import math
import traceback
from io import BytesIO
from PIL import Image, ImageFilter
from . import ebooklib
from .ebooklib import epub
from .base import *

class EPUBBook(Book):

    def __init__( self, book: BytesIO ) -> None:
        super().__init__( book )

    def init( self, book: BytesIO ) -> None:
        self._book: epub.EpubBook = epub.read_epub( book, { 'ignore_ncx': True } )

    def parseTitle( self ) -> None:
        _title = self._book.get_metadata('DC', 'title')
        if _title and _title[0]:
            self.title = _title[0][0]

    def parseUrl( self ) -> None:
        _url = self._book.get_metadata('OPF','FB2.document-info.src-url')
        if _url:
            self.url = _url[0][0]
        pass

    def parseSeria( self ) -> None:
        # _collection1 = self._book.get_item_with_id('collection')
        # _collection2 = self._book.get_metadata('OPF','collection')
        pass

    def parseAuthors( self ) -> None:
        _authors = self._book.get_metadata('DC', 'creator')
        for _author in _authors:
            author = EPUBAuthor(_author)
            if author.Name == 'Цокольный этаж':
                continue
            self._authors[ author.Name ] = author
        pass

    def parseChapters( self ) -> None:
        _chapters = self._book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        self.chapters = len( list( _chapters ) )
        self.last_chapter = f'Глава {self.chapters}'
    
    def parseCover( self ) -> None:
        _covers = self._book.get_items_of_type(ebooklib.ITEM_COVER)
        for _cover in _covers:
            image_bytes: bytes = _cover.get_content()
            if image_bytes:
                self._cover = image_bytes
                break
        
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


class EPUBSeria(Seria):
    name: str | None = None
    number: int | None = None

    def __init__( self, data: tuple ) -> None:
        super().__init__( data )

    def parse( self, data: tuple ) -> None:
        pass

class EPUBAuthor(Author):

    def __init__( self, data: tuple ) -> None:
        super().__init__( data )

    def parse( self, data: tuple ) -> None:

        first_name = data[0]

        if first_name:
            self.first_name = first_name