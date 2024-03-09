import asyncio
import os
import subprocess

from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.enums import ContentType

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
VMAX = 600


@dp.message()
async def video(msg: Message) -> None:
    if msg.content_type == ContentType.VIDEO:
        received = False
        downloaded = False
        v = msg.video

        if v.file_size < 20971520:
            file = await bot.get_file(v.file_id)

            if file is not None:
                received = True

            await bot.download_file(file.file_path, "in.mp4")

            while received and not downloaded:
                if os.path.exists("in.mp4"):
                    received = False
                    downloaded = True

            if downloaded:
                await msg.answer('Downloaded')

            if v.width != v.height or v.width > VMAX or v.height > VMAX:
                await msg.answer('Video has big resolution or more than 60 seconds long.'
                                 ' It will be resized and/or reduced.')

            w, h = v.width, v.height

            if w != h:
                if w > VMAX and h > VMAX:
                    crop = f'crop={VMAX}:{VMAX}:{int((w - VMAX) / 2)}:{int((h - VMAX) / 2)}'

                elif w <= VMAX < h:
                    crop = f'crop={w}:{w}:{0}:{int((h - w) / 2)}'

                elif w > VMAX >= h:
                    crop = f'crop={h}:{h}:{int((w - h) / 2)}:{0}'

                elif w <= VMAX and h <= VMAX:
                    if w > h:
                        crop = f'crop={h}:{h}:{int((w - h) / 2)}:{0}'
                    elif w < h:
                        crop = f'crop={w}:{w}:{0}:{int((h - w) / 2)}'

            else:
                if w >= VMAX:
                    crop = f'crop={VMAX}:{VMAX}:{int((w - VMAX) / 2)}:{int((h - VMAX) / 2)}'
                elif w < VMAX:
                    crop = f'crop={w}:{h}:{0}:{0}'

            process = subprocess.Popen(['ffmpeg', '-y', '-i', 'in.mp4', '-filter:v', crop, 'out.mp4'])

            if process.wait() == 0 and os.path.exists("out.mp4"):
                await bot.send_video_note(chat_id=msg.from_user.id, video_note=FSInputFile("out.mp4"))
            else:
                await msg.answer(f'Process failed: {process.wait()}')

            await msg.answer("Job's done")

        else:
            await msg.answer(f'Video is bigger than 20Mb, bot cannot process it.')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
