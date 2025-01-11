
import zipfile
from io import BytesIO       

from .base import Book
from .epub import EPUBBook
from .fb2 import FB2Book

async def get_caption_and_cover( file_name: str, file: BytesIO ) -> tuple[ str, bytes | None ]:

    _book = None

    caption = ''
    cover = None

    if file_name.endswith( '.zip' ):
        archive = zipfile.ZipFile( file, 'r' )
        for _file in archive.infolist():

            if _file.filename.endswith( '.fb2' ):
                _book = FB2Book( BytesIO( archive.read( _file ) ) )
                break
            elif _file.filename.endswith( '.epub' ):
                _book = EPUBBook( BytesIO( archive.read( _file ) ) )
                break

    elif file_name.endswith( '.fb2' ):
        _book = FB2Book( file )

    elif file_name.endswith( '.epub' ):
        _book = EPUBBook( file )

    if _book:
        caption = await process_caption( _book )
        cover = await process_cover( _book )

    return caption, cover

async def process_cover( book: Book ) -> bytes | None:
    return book._cover


async def process_caption( book: Book ) -> str:
    
    caption = ''
    
    if book.title and book.url:
        caption += f'<b><a href="{book.url}">{book.title}</a></b>'
    elif book.title:
        caption += f'<b>{book.title}</b>'
    
    if len( book.authors ) > 0:
        authors: str = ', '.join( list( filter( None, book.authors ) ) )
        if authors:
            if len( book.authors ) > 1:
                caption += f'\nАвторы: {authors}'
            else:
                caption += f'\nАвтор: {authors}'
    
    if book.seria:
        seria = book.seria.name
        if book.seria.number:
            caption += f'\nСерия: {seria} #{book.seria.number}'

    if book.chapters > 0:
        if book.chapters > 1:
            caption += f'\n\nПо: "{book.last_chapter}"'
        elif book.last_chapter != book.title:
            caption += f'\n\n{book.last_chapter}'

    return caption