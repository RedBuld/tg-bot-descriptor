import os
import io
import asyncio
import logging
import traceback
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import Router, F, types
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramRetryAfter
from parser import get_caption_and_cover

if not os.environ.get("BOT_TOKEN"):
    raise Exception('provide BOT_TOKEN in env')

####

logging.basicConfig(
    format='%(levelname)s: %(name)s[%(process)d] - %(asctime)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT = Bot(os.environ.get("BOT_TOKEN"))
DP = Dispatcher()


async def generate_private_caption( message: types.Message ) -> None:
    
    if message.forward_origin and message.forward_origin.sender_user.username == 'elibfb2_v3_bot':
        return

    document = await BOT.get_file( message.document.file_id )

    file_path = document.file_path
    file_name = message.document.file_name

    file = await BOT.download_file( file_path )
    caption, cover = await get_caption_and_cover( file_name, file )

    if caption:
        await _send( message.chat.id, file_name, file, caption, cover )

    file.close()


async def generate_channel_caption( channel_post: types.Message ) -> None:

    document = await BOT.get_file( channel_post.document.file_id )

    file_path = document.file_path
    file_name = channel_post.document.file_name

    file = await BOT.download_file( file_path )
    caption, cover = await get_caption_and_cover( file_name, file )

    chat_id = channel_post.chat.id
    file_id = channel_post.document.file_id
    message_id = channel_post.message_id

    if caption:
        if cover:
            await _replace( chat_id, message_id, file_name, file, caption, cover )
        else:
            await _edit( chat_id, file_id, message_id, file_name, file, caption, cover )

    file.close()


async def _send( chat_id: int, file_name: str, file: io.BytesIO, caption: str = '', cover: bytes | None = None ) -> None:
    try:
        file.seek(0)
        document = BufferedInputFile( file.read(), file_name )
        thumb = None
        if cover is not None:
            thumb = BufferedInputFile( cover, 'cover.jpg' )
        await BOT.send_document( chat_id=chat_id, document=document, caption=caption, thumbnail=thumb, parse_mode='HTML', request_timeout=600000 )
    except TelegramRetryAfter as e:
        await asyncio.sleep( e.retry_after )
        await _send( chat_id, file_name, file, caption, cover )
    except:
        traceback.print_exc()
        pass


async def _edit( chat_id: int, file_id: str, message_id: int, file_name: str, file: io.BytesIO, caption: str = '', cover: bytes | None = None ) -> None:
    try:
        await BOT.edit_message_caption( chat_id=chat_id, message_id=message_id, caption=caption, parse_mode='HTML', request_timeout=600000 )
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await _edit( chat_id, file_id, message_id, file_name, file, caption, cover )
    except:
        await _replace( chat_id, message_id, file_name, file, caption, cover )


async def _replace( chat_id: int, message_id: int, file_name: str, file: io.BytesIO, caption: str = '', cover: bytes | None = None ) -> None:
    try:
        file.seek(0)
        document = BufferedInputFile( file.read(), file_name )
        thumb = None
        if cover is not None:
            thumb = BufferedInputFile( cover, 'cover.jpg' )
        await BOT.send_document( chat_id=chat_id, document=document, caption=caption, thumbnail=thumb, parse_mode='HTML', request_timeout=600000 )
        await BOT.delete_message( chat_id=chat_id, message_id=message_id )
    except TelegramRetryAfter as e:
        await asyncio.sleep( e.retry_after )
        await _replace( chat_id, message_id, file_name, file, caption, cover )
    except:
        traceback.print_exc()
        pass


async def main() -> None:
    router = Router()
    router.message.register( generate_private_caption, F.document )
    router.channel_post.register( generate_channel_caption, F.document )
    DP.include_router( router )
    await DP.start_polling(BOT, polling_timeout=5, handle_signals=False)


asyncio.run( main() )