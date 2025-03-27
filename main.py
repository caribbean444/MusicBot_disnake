# -*- coding: utf-8 -*-
import json
import disnake
import logging
from Youtube_API import name_video
import asyncio
import yt_dlp
from pytube import Playlist
from disnake.ext import commands
from disnake.ui import Button, View
import os
import time as ti
import subprocess
import sys
import colorlog
from dotenv import load_dotenv

load_dotenv()

time_out = 300 # Время отключения после периода бездействия в секундах

# Имя файла для хранения списка игнорируемых каналов
CHANNELS_FILE = "./data/ignored_channels.json"

# Получение уровня логирования из переменной окружения
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

# Отображение уровня логирования в соответствующий уровень для logging
log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
# Получаем уровень логирования, либо INFO, если уровень некорректен
log_level = log_levels.get(log_level_str, logging.INFO)
# Настройка базового логгера для библиотек (например, disnake)
logging.basicConfig(level=log_level)

# Создаем отдельный логгер с именем "MusicBOT"
logger = logging.getLogger("MusicBOT")

# Устанавливаем уровень логирования на INFO
logger.setLevel(log_level)
logger.propagate = False
# Проверяем, есть ли уже обработчики, чтобы не добавлять их повторно

# Создаем обработчик для вывода в консоль
handler = colorlog.StreamHandler()

# Настраиваем цветной форматтер
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s%(reset)s - %(message)s',  # Формат вывода
    log_colors={
        'DEBUG': 'cyan',       # Цвет для DEBUG
        'INFO': 'purple',      # Цвет для INFO (фиолетовый)
        'WARNING': 'yellow',   # Цвет для WARNING
        'ERROR': 'red',        # Цвет для ERROR
        'CRITICAL': 'bold_red' # Цвет для CRITICAL
    }
)

# Устанавливаем форматтер на обработчик
handler.setFormatter(formatter)

# Добавляем обработчик к логгеру "MusicBOT"
logger.addHandler(handler)
token = os.getenv("DISCORD_TOKEN")
owner_ids = set(map(int, os.getenv("BOT_OWNER_IDS", "").split(",")))  # Загружаем и преобразуем ID в множество

subprocess.check_call([sys.executable, '-m', 'pip', 'install', "-U", "--pre", "yt-dlp[default]"])

# Загрузка списка каналов из файла
def load_ignored_channels():
    if not os.path.exists(CHANNELS_FILE):
        return []
    # Проверяем, пуст ли файл
    if os.path.getsize(CHANNELS_FILE) == 0:  # Если файл пуст
        return []
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Сохранение списка каналов в файл
def save_ignored_channels(channels):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(channels, f, indent=4)

list_channal_no = load_ignored_channels()

bot = commands.Bot(command_prefix='.', intents=disnake.Intents.all(), case_insensitive=True)
bot.owner_ids = owner_ids

ydl_opts = {'format': 'bestaudio',
            'ignoreerrors': True,
            'extractor_retries': 3,
            'concurrent_fragment_downloads': 2,
            'noplaylist': True}

ydl_opts_url = {
    'extract_flat': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 8', 'options': '-vn'}

inactivity_timers = {}  # Словарь для отслеживания таймеров по ID серверов

@bot.event
async def on_ready():
    logger.info("Bot online")



@bot.event
async def on_message(message):
    if message.channel.id in list_channal_no:
        return
    await bot.process_commands(message)



server, server_id, name_channel = None, None, None

@bot.event
async def on_voice_state_update(member, before, after):
    global server
    if member == bot.user:
        logger.info(f"Состояние бота изменилось: {before.channel} -> {after.channel}")

        # Если бот был кикнут
        if before.channel is not None and after.channel is None:
            logger.info(f"Бот был отключён из канала: {before.channel.name}")

            voice_client = disnake.utils.get(bot.voice_clients, guild=server)
            if voice_client:
                logger.debug(f"Состояние клиента: is_connected={voice_client.is_connected()}")
                try:
                    await voice_client.disconnect(force=True)
                    logger.debug(f"Голосовые клиенты: {bot.voice_clients}")
                    logger.info("Клиент успешно отключён и очищен.")
                except Exception as e:
                    logger.error(f"Ошибка при отключении клиента: {e}")
            else:
                logger.info("Голосовой клиент уже не активен.")

domains = ['https://www.youtube.com/',
           'http://www.youtube.com/',
           'https://music.youtube.com/',
           'http://music.youtube.com/',
           'https://youtu.be/']


async def check_domains(link):
    for x in domains:
        if link.startswith(x):
            return True

    return False

async def check_inactivity(ctx):
    guild_id = ctx.guild.id
    inactivity_timers[guild_id] = asyncio.create_task(inactivity_timeout(ctx))

async def inactivity_timeout(ctx):
    guild_id = ctx.guild.id
    logger.debug(f"Таймер запущен")
    await asyncio.sleep(time_out)
    # Проверяем состояние очереди и воспроизведения
    voice_client = disnake.utils.get(bot.voice_clients, guild=server)
    if len(song_queue) == 0 and (not voice_client or not voice_client.is_playing()):
        voice_client = disnake.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            if guild_id in inactivity_timers:
                del inactivity_timers[guild_id]
            logger.info("Бот отключён из-за отсутствия активности.")
        else:
            logger.warning("Клиент не существует, либо отключен")

class CustomVoiceClient(disnake.VoiceClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def stop(self, *, force: bool = False):
        """Переопределенный stop с контролем колбэка after"""
        if self._player:
            self._player.after = None
        if asyncio.iscoroutinefunction(super().stop):
            await super().stop()  # Для асинхронных версий
        else:
            super().stop()  # Для синхронных версий

    async def disconnect(self, *, force: bool = False):
        """Отключает голосовой клиент и предотвращает автоматическое переподключение."""
        logger.info("Отключение голосового клиента (custom_disconnect)...")
        if not force and not self.is_connected():
            return

        await self.stop()
        self._connected.clear()

        try:
            if self.ws:
                await self.ws.close()

            await self.voice_disconnect()
        finally:
            self.cleanup()
            if self.socket:
                self.socket.close()
         # Убираем внутренние флаги переподключения
        self._listener = None
        self.ws = None
        self.socket = None
        self._handshaking = False

        # Удаляем клиента из состояния
        if self.guild:
            self._state._remove_voice_client(self.guild.id)
    
    async def potential_reconnect(self) -> bool:
        logger.debug("Перехват потенциального переподключения (custom_disconnect)...")
        return False

@bot.command()
async def ignore(ctx,channel: disnake.TextChannel):
    """Канал добавлен в игнорируемые"""
    channel_id = channel.id
    list_channal_no.append(channel_id)
    save_ignored_channels(list_channal_no)
    await ctx.send(f"Канал {channel.mention} теперь недоступен для бота")


@bot.command()
async def noignore(ctx,channel: disnake.TextChannel):
    """Канал исключен из игнорируемых"""
    channel_id = channel.id
    list_channal_no.remove(channel_id)
    save_ignored_channels(list_channal_no)
    await ctx.send(f"Канал {channel.mention} снова доступен для бота")




@bot.command()
async def time(ctx, *, command=None):
    """Изменение времени ожидания бота"""
    global time_out
    if command == None:
        send1 = "Текущее время: " + str(time_out)
        await ctx.channel.send("Укажите время в секундах")
        await ctx.channel.send(send1)
        return
    params1 = command.split(" ")
    if len(params1) == 1:
        time_out = int(params1[0])
        send = "Время ожидания бота изменено: " + str(time_out) + " секунд"
        await ctx.channel.send(send)
    else:
        await ctx.channel.send("Команда некорректна")
        return


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    exit()


@bot.command()
async def clear(ctx):
    """Очистка очереди"""
    song_queue.clear()
    name_song_queue.clear()
    await ctx.channel.send("`Очередь очищена`")


def embed_track(song_info):
    color_standart = 0x00b0f4
    color = 0x6e1d8b
    color1 = 0x9951b3
    artist = song_info["channel"]
    artist_url = song_info["channel_url"]
    image = song_info["thumbnails"][0]["url"]
    title = song_info["title"]
    url = song_info["webpage_url"]
    description = song_info["description"]
    duration= int(song_info['duration'])
    embed = disnake.Embed(title=title,
                      url=url,
                      description=description,
                      colour=color1)
    embed.set_author(name=artist,url=artist_url)
    embed.set_thumbnail(url=image)
    #edit_gif(duration)
    embed.set_image(url="attachment://edited.gif")
    embed.set_footer(text="MusicBOT",
                     icon_url="https://cdn3.emoji.gg/emojis/2068-dancer.gif")
    return embed

song_queue = []
name_song_queue = []

class PlayerView(View):
    ctx= None
    global server, name_channel
    def __init__(self, ctx):
        #View.timeout = 600
        super().__init__(timeout=600)
        self.ctx=ctx

    @disnake.ui.button(style=disnake.ButtonStyle.primary,emoji="▶️")
    async def play_button_callback(self, button, interaction):
        voice = disnake.utils.get(bot.voice_clients, guild=server)
        if voice.is_paused():
            voice.resume()
        await interaction.response.edit_message(view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, emoji="⏸️")
    async def pause_button_callback(self, button, interaction):
        voice = disnake.utils.get(bot.voice_clients, guild=server)
        if voice.is_playing():
            voice.pause()
        await interaction.response.edit_message(view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, emoji="⏹️")
    async def stop_button_callback(self, button, interaction):
        voice = disnake.utils.get(bot.voice_clients, guild=server)
        await clear(self.ctx)
        await voice.stop()
        await interaction.response.edit_message(view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, emoji="⏩")
    async def skip_button_callback(self, button, interaction):
        await interaction.response.defer()
        await skip(self.ctx)
        # button.disabled = True

    @disnake.ui.button(style=disnake.ButtonStyle.primary, emoji="📶")
    async def queue_button_callback(self, button, interaction):
        await queue(self.ctx)
        # button.disabled = True
        await interaction.response.edit_message(view=self)

class QueueView(disnake.ui.View):
    ctx = None

    global server, name_channel, song_queue, name_song_queue

    def __init__(self, ctx):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.options = []

        # Формируем список опций для выбора
        if song_queue:
            for i, name in enumerate(name_song_queue[:25]):
                self.options.append(disnake.SelectOption(label=f"{i + 1}. {name}", value=str(i)))
        else:
            self.options.append(disnake.SelectOption(label="Очередь пуста", value="none"))

        # Создаём Select вручную и добавляем в View
        select_menu = disnake.ui.Select(
            placeholder="Выберите трек",
            options=self.options,
            min_values=0,  # Позволяем выбрать 0 опций
            max_values=1   # Максимум одна опция
        )
        select_menu.callback = self.select_callback  # Устанавливаем обработчик
        self.add_item(select_menu)  # Добавляем Select в View

    async def select_callback(self, interaction: disnake.Interaction):
        await interaction.response.defer()
        for i in range(int(interaction.data["values"][0])):
            song_queue.pop(0)
            name_song_queue.pop(0)

        await skip(self.ctx)
        await interaction.message.delete()

@bot.command()
async def queue(ctx):
    """Очередь треков"""
    if len(song_queue) == 0:
        await ctx.channel.send("`Очерень пуста`")
    else:
        await ctx.channel.send(view=QueueView(ctx))


async def kick(ctx):
    voice = disnake.utils.get(bot.voice_clients, guild=server)
    while voice.is_playing():
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(time_out)
        while voice.is_playing():
            break
        else:
            await voice.disconnect()
            voice.cleanup()


def play_next(ctx):
    global song_queue
    guild_id = ctx.guild.id
    voice = disnake.utils.get(bot.voice_clients, guild=server)
    if voice != None:
        if (not voice.is_connected()):
            # voice.pause()
            song_queue.clear()
            name_song_queue.clear()
    else:
        return
    
    if len(song_queue) == 0:
        # Если очередь пустая, запускаем таймер
        if guild_id in inactivity_timers:
            logger.debug(f"Сброс таймера")
            inactivity_timers[guild_id].cancel()
            del inactivity_timers[guild_id]
        asyncio.run_coroutine_threadsafe(check_inactivity(ctx), bot.loop)
        return

    if len(song_queue) >= 1:
        voice = disnake.utils.get(bot.voice_clients, guild=server)
        sourse = song_queue[0]
        song_queue.pop(0)
        name_track = name_song_queue[0]
        name_song_queue.pop(0)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(sourse, download=False)
        track = disnake.FFmpegPCMAudio(song_info["url"], **FFMPEG_OPTIONS)

        asyncio.run_coroutine_threadsafe(send_info(ctx,song_info), bot.loop)
        try:
            if voice and voice.is_playing():
                voice.stop()
            logger.info(f"Воспроизведение трека")
            voice.play(track, after=lambda e: play_next(ctx))
        except Exception as e:
            logger.error(f"Error playing track: {e}")
            # play_next(ctx)  # Переход к следующему треку
        if guild_id in inactivity_timers:
            logger.debug(f"Сброс таймера")
            inactivity_timers[guild_id].cancel()
            del inactivity_timers[guild_id]

async def send_info(ctx,song_info):
    await ctx.channel.send("`Играет сейчас`", embed=embed_track(song_info)), bot.loop
    await ctx.channel.send(view=PlayerView(ctx=ctx))


@bot.command()
async def leave(ctx):
    """"Отключение бота от голосового чата и очистка очереди"""
    global server, name_channel
    voice = disnake.utils.get(bot.voice_clients, guild=server)
    if voice and voice.is_connected():
        await voice.disconnect()
        voice.cleanup()
        song_queue.clear()
        name_song_queue.clear()
    else:
        await ctx.channel.send("Бот уже отключен")


@bot.command()
async def queue_size(ctx):
    """Размер очереди"""
    await ctx.channel.send(len(song_queue))


@bot.command()
async def skip(ctx):
    """Пропуск текущего трека"""
    global server, name_channel
    voice = disnake.utils.get(bot.voice_clients, guild=server)
    if voice and voice.is_playing():
        await voice.stop()
        play_next(ctx)
    else:
        await ctx.channel.send("Музыка не воспроизводится")


playli = False

async def add_name_songs(ctx, pvideo, start, a):
    global song_queue, name_song_queue
    for i in range(1, len(pvideo)):
        start1 = ti.time()
        name_track = await name_video(pvideo[i])
        end1 = ti.time()
        logger.debug("Время поиска трека: %d ms", (end1 - start1) * 10 ** 3)
        name_song_queue.append(name_track)
        song_queue.append(pvideo[i])
    end = ti.time()
    logger.debug("Время поиска всех треков: %d ms",
          (end - start) * 10 ** 3)
    queue_num = "В очереди: " + str(a + 1) + " -- " + str(len(song_queue))
    await ctx.channel.send(f"`{queue_num}`")
    logger.info("Плейлист загружен")


async def loopp(ctx, pvideo, a):
    global song_queue, name_song_queue
    message_text = "`Загрузка Плейлиста`"

    message_temp = await ctx.channel.send(message_text)

    start = ti.time()

    asyncio.run_coroutine_threadsafe(add_name_songs(ctx, pvideo, start, a), bot.loop)

async def is_playlist(ctx, sourse):
    voice = disnake.utils.get(bot.voice_clients, guild=server)
    p = Playlist(sourse)
    a = len(song_queue)
    global playli
    playli = True

    logger.info(f"URL в Плeйлисте: {p.video_urls}")
    a = len(song_queue)

    if not voice.is_playing():
        sourse = p.video_urls[0]
    else:
        song_queue.append(p.video_urls[0])
        name_track = await name_video(p.video_urls[0])
        name_song_queue.append(name_track)

    asyncio.run_coroutine_threadsafe(loopp(ctx, p.video_urls, a), bot.loop)

    return sourse


@bot.command()
async def play(ctx, *, command=None):
    """Воспроизведение музыки с Youtube"""
    global server, server_id, name_channel, playli, song_queue, name_song_queue
    author = ctx.author
    if command == None:
        server = ctx.guild
        name_channel = author.voice.channel.name
        voice_channel = disnake.utils.get(server.voice_channels, name=name_channel)
        voice = disnake.utils.get(bot.voice_clients, guild=server)
        return

    params = command.split(" ")
    sourse = None
    if len(params) == 1:
        sourse = params[0]
        server = ctx.guild
        name_channel = author.voice.channel.name
        voice_channel = disnake.utils.get(server.voice_channels, name=name_channel)
    else:
        query = ""
        for i in params:
            query += i+ " "
        with yt_dlp.YoutubeDL(ydl_opts_url) as ydl:
            search_results = ydl.extract_info(f"ytsearch:{query}", download=False)

            await play(ctx,command=search_results['entries'][0]['url'])
            return

    voice = disnake.utils.get(bot.voice_clients, guild=server)
    if (disnake.utils.get(bot.voice_clients, guild=server) != None and (not voice.is_connected())):
        logger.info(f"Выполняется отключение")
        await voice.disconnect()
        voice.cleanup()
        song_queue.clear()
        name_song_queue.clear()
        await voice_channel.connect(cls=CustomVoiceClient, reconnect=False)

    voice = disnake.utils.get(bot.voice_clients, guild=server)

    if voice is None:
        await voice_channel.connect(cls=CustomVoiceClient, reconnect=False)
        song_queue.clear()
        name_song_queue.clear()
        voice = disnake.utils.get(bot.voice_clients, guild=server)

    if sourse == None:
        pass
    elif sourse.startswith('http'):

        if (not sourse.startswith('https://www.youtube.com/') and (
        not sourse.startswith('http://www.youtube.com/')) and (
        not sourse.startswith('https://music.youtube.com/')) and (not sourse.startswith('https://youtu.be/')) and (
        not sourse.startswith('https://youtube.com/'))):
            await ctx.channel.send(f'{author.mention} Ссылка не на ютуб')
            return 0

        if sourse.startswith('https://www.youtube.com/playlist') or (
        sourse.startswith('https://music.youtube.com/playlist')) or (sourse.startswith('https://youtube.com/playlist')):
            sourse = await is_playlist(ctx, sourse)
        if not voice.is_playing():

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(sourse, download=False)
            track = disnake.FFmpegPCMAudio(song_info["url"], **FFMPEG_OPTIONS)

            name_track = await name_video(sourse)

            await send_info(ctx, song_info)
            playli = False
            try:
                logger.info(f"Воспроизведение трека")
                voice.play(track, after=lambda e: play_next(ctx))
            except Exception as e:
                logger.error(f"Error playing track: {e}")
                # play_next(ctx)  # Переход к следующему треку
            #asyncio.run_coroutine_threadsafe(kick(ctx), bot.loop)
        else:
            if not playli:
                song_queue.append(sourse)

                name_track = await name_video(sourse)
                name_song_queue.append(name_track)
                queue_num = "В очереди: " + str((len(song_queue)))

                await ctx.channel.send(f"`{queue_num}`")

            playli = False
    else:
        query = ""
        for i in params:
            query += i+ " "
        with yt_dlp.YoutubeDL(ydl_opts_url) as ydl:
            search_results = ydl.extract_info(f"ytsearch:{query}", download=False)

            await play(ctx,command=search_results['entries'][0]['url'])

bot.run(token)
