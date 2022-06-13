import logging
import csv
import os
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils import executor
from telegram import WebhookInfo
from yt import getComments, getStatistics
logging.basicConfig(level=logging.INFO)
API_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Yt(StatesGroup):
    commentvideoID = State()
    statsvideoID = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    botInfo = await bot.get_me()
    await bot.send_message(message.chat.id, "Hi {}!, Welcome to {}\n\nGet YouTube Video Comments /comments\nGet YouTube Video Statistics /statistics".format(message.chat.first_name, botInfo.first_name))


@dp.message_handler(commands='comments')
async def comments(message: types.Message, state: FSMContext):
    await Yt.commentvideoID.set()
    await bot.send_message(message.chat.id, "Enter YouTube Video ID.")


@dp.message_handler(state=Yt.commentvideoID)
async def process_comments(message: types.Message, state: FSMContext):
    videoID = message.text
    fileName = "comments_{}_{}.csv".format(videoID, message.chat.id)
    comments = []
    next_token = None
    next_page = True
    await bot.send_message(message.chat.id, "Fetching Comments Please Wait...")
    while next_page:
        data = getComments(next_token, videoID)
        if 'nextPageToken' in data:
            next_token = data['nextPageToken']
            comments.extend(data['items'])
        else:
            if 'items' in data:
                comments.extend(data['items'])
                next_page = False
            else:
                next_page = False
    if len(comments) > 0:
        with open(fileName, 'w', encoding="UTF-8") as file:
            writer = csv.writer(file, delimiter=",", lineterminator="\n")
            writer.writerow(['id', 'name', 'text', 'image', 'channel',
                            'commentlikes', 'publishedAt', 'updatedAt'])
            for item in comments:
                commentData = item['snippet']['topLevelComment']
                writer.writerow([
                    commentData['id'],
                    commentData['snippet']['authorDisplayName'],
                    commentData['snippet']['textDisplay'],
                    commentData['snippet']['authorProfileImageUrl'],
                    commentData['snippet']['authorChannelUrl'],
                    commentData['snippet']['likeCount'],
                    commentData['snippet']['publishedAt'],
                    commentData['snippet']['updatedAt']
                ])
        await bot.send_document(
            message.chat.id,
            document=open(fileName, 'rb'),
            caption="YouTube ID {}\n\nTotal Top Level Comments: {}".format(
                videoID, len(comments))
        )
        await bot.send_message(message.chat.id, 'https://www.youtube.com/watch?v={}'.format(videoID))
        os.remove(fileName)
        await state.finish()
    else:
        await bot.send_message(message.chat.id, "No Comments Found of YouTube ID {}".format(videoID))
        await state.finish()


@dp.message_handler(commands='statistics')
async def comments(message: types.Message, state: FSMContext):
    await Yt.statsvideoID.set()
    await bot.send_message(message.chat.id, "Enter YouTube Video ID.")


@dp.message_handler(state=Yt.statsvideoID)
async def process_comments(message: types.Message, state: FSMContext):
    videoID = message.text
    data = getStatistics(videoID)
    if len(data['items']) > 0:
        text = 'YouTube ID {} Statistics\n\nLikes: {}\nViews: {}\nTop Level Comments & Replies: {}'.format(
            videoID,
            data['items'][0]['statistics']['likeCount'],
            data['items'][0]['statistics']['viewCount'],
            data['items'][0]['statistics']['commentCount']
        )
        await bot.send_message(message.chat.id, text)
        await bot.send_message(message.chat.id, 'https://www.youtube.com/watch?v={}'.format(videoID))
        await state.finish()
    else:
        await bot.send_message(message.chat.id, 'YouTube ID Statistics Is Empty Or Not Found!')
        await state.finish()


@dp.message_handler(commands='web')
async def web(message: types.Message):
    reply_markup = types.InlineKeyboardMarkup()
    reply_markup.add(types.InlineKeyboardButton(text="Google", web_app=types.web_app_info.WebAppInfo(url="https://google.com")))
    await message.answer("test", reply_markup=reply_markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
