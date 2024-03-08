import asyncio
import os
import subprocess

from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.enums import ContentType

TOKEN = "TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher()


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

            if v.width != v.height or v.duration > 60:
                await msg.answer('Video has big resolution or more than 60 seconds long.'
                                 ' It will be resized and/or reduced.')

            w, h = v.width, v.height
            vmax = 600

            if w != h:
                if w > vmax and h > vmax:
                    crop = f'crop={vmax}:{vmax}:{int((w - vmax) / 2)}:{int((h - vmax) / 2)}'

                elif w <= vmax < h:
                    crop = f'crop={w}:{w}:{0}:{int((h - w) / 2)}'

                elif w > vmax >= h:
                    crop = f'crop={h}:{h}:{int((w - h) / 2)}:{0}'

                elif w <= vmax and h <= vmax:
                    if w > h:
                        crop = f'crop={h}:{h}:{int((w - h) / 2)}:{0}'
                    elif w < h:
                        crop = f'crop={w}:{w}:{0}:{int((h - w) / 2)}'

            else:
                if w >= vmax:
                    crop = f'crop={vmax}:{vmax}:{int((w - vmax) / 2)}:{int((h - vmax) / 2)}'
                elif w < vmax:
                    crop = f'crop={w}:{h}:{0}:{0}'

            if v.duration < 60:
                process = subprocess.Popen(['ffmpeg', '-y', '-i', 'in.mp4', '-filter:v', crop, 'out.mp4'])
            else:
                process = subprocess.Popen(['ffmpeg', '-y', '-ss', '00:00:00', '-to', '00:01:00',
                                            '-i', 'in.mp4', '-filter:v', crop, 'out.mp4'])

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
