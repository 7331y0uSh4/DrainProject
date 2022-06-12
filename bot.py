import asyncio
import os
from cgitb import text
from timeit import repeat
import discord
from discord import utils
from discord.utils import get
from discord.ext import commands
import config
from config import settings
from discord.ext.tasks import loop
import datetime
from datetime import datetime
import requests
from Cybernator import Paginator
import sqlite3
from tabulate import tabulate #удобный модуль для рисования таблиц
import json
import random

name = "database.db"
api_key = ""
base_url = ""
intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=settings['prefix'],  intents=intents)
date_ban = datetime.now()
bot.remove_command("help")
client = discord.Client()
conn = sqlite3.connect(name) # или :memory:
cursor = conn.cursor()

@bot.event
async def on_ready():
    for guild in bot.guilds:#т.к. бот для одного сервера, то и цикл выводит один сервер#вывод id сервера
        serv=guild#без понятия зачем это
        for member in guild.members:#цикл, обрабатывающий список участников
            cursor.execute(f"SELECT id FROM users where id={member.id}")#проверка, существует ли участник в БД
            if cursor.fetchone()==None:#Если не существует
                cursor.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 0, 'S','[]',0,0)")#вводит все данные об участнике в БД
            else:#если существует
                pass
            conn.commit()

    print('Я запущен!')
    bot.loop.create_task(status_task())

@bot.event
async def on_member_join(member):
    cursor.execute(f"SELECT id FROM users where id={member.id}")#все также, существует ли участник в БД
    if cursor.fetchone()==None:#Если не существует
        cursor.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 0, 'S','[]',0,0)")#вводит все данные об участнике в БД
    else:#Если существует
        pass
    conn.commit()#
    now = datetime.now()
    emb = discord.Embed(title='Добро пожаловать на DrainProject', color=0xff0000)
    emb.add_field(name="Если не знаешь что делать", value='К твоему прочтению обязателен канал <#965359487416418306>. (Галочка в конце)', inline=False)
    emb.add_field(name="Также чтоб не было притензий и разногласий", value='Тебе необходимо прочитать канал <#927297696761528392>', inline=False)
    emb.add_field(name= "Команды бота", value='Чтоб узнать подробнее команды пропиши !help в канале <#972431181624791060>', inline=False)
    emb.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
    emb.set_footer(text=f'Ваш ID: {member.id} Время {now.hour}:{now.minute}')
    await member.send(embed = emb)

@bot.event
async def on_message(message):
    if len(message.content) >= 3:#за каждое сообщение длиной > 10 символов...
        for row in cursor.execute(f"SELECT xp,lvl,cash FROM users where id={message.author.id}"):
            expi=row[0]+random.randint(5, 40)#к опыту добавляется случайное число
            cursor.execute(f'UPDATE users SET xp={expi} where id={message.author.id}')
            if row[1] == 0:
                lvch = expi / (1 * 500)

            else:
                lvch=expi/(row[1]*500)
            lv=int(lvch)
            if row[1] < lv:#если текущий уровень меньше уровня, который был рассчитан формулой выше,...
                emb = discord.Embed(title='✅Поздравляю', description=f"Вы получили новый уровень!!!", colour=discord.Color.green())
                emb.set_footer(text='ответ для ' + message.author.name, icon_url=message.author.avatar_url)
                msg = await message.channel.send(embed=emb)
                await asyncio.sleep(10)
                await msg.delete()#то появляется уведомление...
                bal=2000*lv
                cursor.execute(f'UPDATE users SET lvl={lv},cash={bal} where id={message.author.id}')#и участник получает деньги
    await bot.process_commands(message)#Далее это будет необходимо для ctx команд
    conn.commit() # чтобы команды работали

@bot.command(aliases=['ar'])
@commands.has_role(927307674121543750)#РОЛЬ#РОЛЬ#РОЛЬ#РОЛЬ#РОЛЬ#РОЛЬ#РОЛЬ#РОЛЬ#РОЛЬ#РОЛЬ
async def addrole(ctx, role : discord.Role = None, cost: int= None):
        await ctx.message.delete()
        logs=bot.get_channel(972431181624791060) #LOGSLOGSLOGSLOGSLOGSLOGSLOGSLOGS
        if role is None:
                await ctx.send(embed=discord.Embed(
                        timestamp=ctx.message.created_at,
                        colour=discord.Color.dark_red()
                        ).add_field(name=f'<a:noentr:965583104360198205> | Некорректный ввод команды.',
                        value=f'Укажите роль.'
                        ).set_footer(text="{}".format(ctx.author.name),
                        icon_url=ctx.author.avatar_url),
                        delete_after=5
                        )
        else:
                if cost is None:
                        await ctx.send(embed=discord.Embed(
                        timestamp=ctx.message.created_at,
                        colour=discord.Color.dark_red()
                        ).add_field(name=f'<a:noentr:965583104360198205> | Некорректный ввод команды.',
                        value=f'Укажите стоимость роли.'
                        ).set_footer(text="{}".format(ctx.author.name),
                        icon_url=ctx.author.avatar_url),
                        delete_after=5
                        )
                elif cost <1:
                        await ctx.send(embed=discord.Embed(
                        timestamp=ctx.message.created_at,
                        colour=discord.Color.dark_red()
                        ).add_field(name=f'<a:noentr:965583104360198205> | Некорректный ввод команды.',
                        value=f'Сумма не может быть меньше **1** <:servvalute:967795640425930822>.'
                        ).set_footer(text="{}".format(ctx.author.name),
                        icon_url=ctx.author.avatar_url),
                        delete_after=5
                        )
                else:
                        cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
                        conn.commit()

                        await ctx.send(embed=discord.Embed(
                        timestamp=ctx.message.created_at,
                        colour=discord.Color.from_rgb(27, 227, 124)
                        ).add_field(name=f'<a:Yes1:965581422121353216> | Роль успешно добавлена в магазин.',
                        value=f'Стоимость {role.name} = {cost} <:servvalute:967795640425930822>.'
                        ).set_footer(text="{}".format(ctx.author.name),
                        icon_url=ctx.author.avatar_url),
                        delete_after=5)

                        await logs.send(embed=discord.Embed(
                        timestamp=ctx.message.created_at,
                        colour=discord.Color.from_rgb(27, 227, 124)
                        ).add_field(name=f'<a:Yes1:965581422121353216> | Роль успешно добавлена в магазин.',
                        value=f'Стоимость {role.name} = {cost} <:servvalute:967795640425930822>.'
                        ).set_footer(text="{}".format(ctx.author.name),
                        icon_url=ctx.author.avatar_url))

#Вызов магазина
@bot.command()
async def shop(ctx):
        await ctx.message.delete()
        emb=discord.Embed(title="Магазин ролей", timestamp=ctx.message.created_at, colour=discord.Color.from_rgb(255, 255, 255))
        emb.set_footer(text="{}".format(ctx.author.name), icon_url=ctx.author.avatar_url)
        counter=0
        if ctx.channel.id==972431181624791060:
                for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
                        if ctx.guild.get_role(row[0]) != None:
                                counter+=1
                                emb.add_field(
                                        name=f"{counter}. Стоимость - {row[1]} монет",
                                        value=f"Роль {ctx.guild.get_role(row[0]).mention} \n"
                                              f"ID роли вы можете найти в канале <#965359487416418306>",
                                        inline=False
                                )
                        else:
                                pass

                msg = await ctx.send(embed=emb)
                await asyncio.sleep(10)
                await msg.delete()

#Покупка роли
@bot.command()
async def buy(ctx, role: discord.Role = None):
        if ctx.channel.id == 972431181624791060:
                if role is None:
                        msg1 = await ctx.send(embed=discord.Embed(
                                timestamp=ctx.message.created_at,
                                colour=discord.Color.dark_red()
                                ).add_field(name=f'❌ | Некорректный ввод команды.',
                                value=f'Укажите роль, которую хотите приобрести.'
                                ).set_footer(text="{}".format(ctx.author.name),
                                icon_url=ctx.author.avatar_url),
                                mention_author=False)
                        await asyncio.sleep(10)
                        await msg1.delete()
                else:
                        if role in ctx.author.roles:
                                msg2 = await ctx.send(embed=discord.Embed(
                                timestamp=ctx.message.created_at,
                                colour=discord.Color.dark_red()
                                ).add_field(name=f'❌ | У вас уже имеется такая роль.',
                                value=f'Попробуйте выбрать другую.'
                                ).set_footer(text="{}".format(ctx.author.name),
                                icon_url=ctx.author.avatar_url),
                                mention_author=False)
                                await asyncio.sleep(10)
                                await msg2.delete()
                        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
                                msg3 = await ctx.send(embed=discord.Embed(
                                timestamp=ctx.message.created_at,
                                colour=discord.Color.dark_red()
                                ).add_field(name=f'❌ | Недостаточно средств.',
                                value=f'Накопите немного деньжат и возвращайтесь!'
                                ).set_footer(text="{}".format(ctx.author.name),
                                icon_url=ctx.author.avatar_url),
                                mention_author=False)
                                await asyncio.sleep(10)
                                await msg3.delete()
                        else:
                                await ctx.author.add_roles(role)
                                cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
                                conn.commit()
                                msg4 = await ctx.send(embed=discord.Embed(
                                        timestamp=ctx.message.created_at,
                                        colour=discord.Color.from_rgb(27, 227, 124)
                                        ).add_field(name=f'✔️| Роль успешно приобретена.',
                                        value=f'Она уже находится в вашем профиле.'
                                        ).set_footer(text="{}".format(ctx.author.name),
                                        icon_url=ctx.author.avatar_url),
                                        mention_author=False)
                                await asyncio.sleep(10)
                                await msg4.delete()
                                await ctx.message.delete()


@bot.command()
async def balance(ctx, member: discord.Member = None):
    await ctx.message.delete()
    if member is None:
        msg1 = await ctx.send(embed=discord.Embed(
            description=f"""Баланс пользователя **{ctx.author}** составляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} монет.**"""
        ))
        await asyncio.sleep(10)
        await msg1.delete()
    else:
        msg2 = await ctx.send(embed=discord.Embed(
            description=f"""Баланс пользователя **{member}** составляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} монет.**"""
        ))
        await asyncio.sleep(10)
        await msg2.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def give_cash(ctx, mention, cash):
    await ctx.message.delete()
    try:
        mention = str(mention).replace('!', '')
        for row in cursor.execute(f'SELECT cash FROM users where mention=?', (mention,)):
            cursor.execute(f'UPDATE users SET cash={int(cash) + row[0]} where mention=?', (mention,))
        conn.commit()
        for row in cursor.execute(f'SELECT nickname FROM users where mention=?', (mention,)):
            embed = discord.Embed(title='Пополнение баланса', color=0x42f566)
            embed.set_author(name='Community Bot')
            embed.add_field(name='Оповещение', value=f'Баланс пользователя {row[0]} пополнен на {cash} монет')
            msg1=await ctx.send(embed=embed)
            await asyncio.sleep(10)
            await msg1.delete()
    except Exception as E:
        print(f'give_cash command error: {E}')
        embed = discord.Embed(title='Оповещение', color=0xFF0000)
        embed.add_field(name='Оповещение', value='Ошибка при выполнение программы.')
        msg2=await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await msg2.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def stats(ctx):
    count = 0  # put these at the beginning of your command so it will reset every time, otherwise, your starting number would be the sum of all earlier commands
    for member in ctx.guild.members:  # you forgot to get members
        if member.status != discord.Status.offline:
            count += 1  # you can't use "= +1" - "+= 1" is correct

    all_users = ctx.guild.member_count
    embed = discord.Embed(title=f'**{ctx.guild.name}** "Статистика"', color=0x000)
    embed.add_field(name="Всего участников", value=all_users)
    embed.add_field(name="Онлайн", value=f'{count} :green_circle:', inline=True)  # your "f" was in wrong place
    embed.add_field(name="Оффлайн", value=f'{all_users - count} :red_circle:', inline=True)
    msg = await ctx.send(embed=embed)
    await ctx.message.delete()
    await asyncio.sleep(30)
    await msg.delete()

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel != None:
        if after.channel.id == 965643277074309210:
            for guild in bot.guilds:
                maincategory = discord.utils.get(guild.categories, id=965643275807649792) #категория создания канала
                channel1 = await guild.create_voice_channel(
                    f'𝕯𝖗𝖆𝖎𝖓𝖊𝖗 {member.display_name}', #название канала
                     #позиция созданного канала (для теста просто уберите этот пункт)
                    category=maincategory, #категория  в которой создастся канал
                    bitrate=96000 # установить битрейт 96
                )
                await channel1.set_permissions(member, connect=True, mute_members=True, move_members=True, manage_channels=True) # установить права на канал его создателю
                await member.move_to(channel1) # переместить пользователя в этот канал
                def check(x, y, z):
                    return len(channel1.members) == 0

                await bot.wait_for('voice_state_update', check=check)
                await channel1.delete()

@bot.command()
async def name(ctx, *, new_name):
    await ctx.message.delete()
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.edit(name="🔊" +new_name)
        emb = discord.Embed( title = '✅Получилось', description="Название голосового канала успешно изменено!", colour = discord.Color.green())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        emb = discord.Embed( title = '❌error', description="ERROR!", colour = discord.Color.green())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg2 = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg2.delete()
        return

@bot.command()
async def limit(ctx, user_limit: int):
    await ctx.message.delete()
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.edit(user_limit=user_limit)
        emb = discord.Embed( title = '✅Получилось', description="Лимит голосового канала успешно изменён!", colour = discord.Color.green())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        emb = discord.Embed( title = '❌error', description="ERROR!", color = discord.Color.red())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg2 = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg2.delete()
        return

@bot.command()
async def rkick(ctx: commands.Context, user: discord.Member):
    await ctx.message.delete()
    if ctx.author.voice and ctx.author.voice.channel:
        emb = discord.Embed( title = '✅Получилось', description=f"Пользователь {user.mention} выгнан из  {user.voice.channel.mention}!", colour = discord.Color.green())

        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg = await ctx.send( embed = emb)
        await user.move_to(None)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        emb = discord.Embed( title = '❌error', description="ERROR!", color = discord.Color.red())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg2 = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg2.delete()
        return

@bot.command()
async def lock(ctx):
    await ctx.message.delete()
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.set_permissions(discord.utils.get(ctx.guild.roles, id=927307019092893716), connect = False)
        emb = discord.Embed( title = '✅Получилось', description=f"Голосовой канал закрыт!", colour = discord.Color.green())

        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        emb = discord.Embed( title = '❌error', description="ERROR!" ,color = discord.Color.red())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg2 = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg2.delete()
        return

@bot.command()
async def hide(ctx):
    await ctx.message.delete()
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.set_permissions(discord.utils.get(ctx.guild.roles, id=927307019092893716), view_channel=False)
        emb = discord.Embed( title = '✅Получилось', description=f"Голосовой канал скрыт!", colour = discord.Color.green())

        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        emb = discord.Embed( title = '❌error', description="ERROR!", color = discord.Color.red())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg2 = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg2.delete()
        return

@bot.command()
async def unhide(ctx):
    await ctx.message.delete()
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.set_permissions(discord.utils.get(ctx.guild.roles, id=927307019092893716), view_channel=True)
        emb = discord.Embed( title = '✅Получилось', description=f"Голосовой канал виден всем!", colour = discord.Color.green())

        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        emb = discord.Embed( title = '❌error', description="ERROR!", color = discord.Color.red())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg2 = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg2.delete()
        return

@bot.command()
async def unlock(ctx):
    await ctx.message.delete()
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.set_permissions(discord.utils.get(ctx.guild.roles, id=927307019092893716), connect = True)
        emb = discord.Embed( title = '✅Получилось', description=f"Голосовой канал открыт!", colour = discord.Color.green())

        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        emb = discord.Embed( title = '❌error', description="ERROR!", color = discord.Color.red())
        emb.set_footer(text = 'ответ для ' + ctx.author.name, icon_url = ctx.author.avatar_url)
        msg2 = await ctx.send( embed = emb)
        await asyncio.sleep(10)
        await msg2.delete()
        return

@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def role(ctx): # Создаём функцию и передаём аргумент ctx. # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.message.delete()
    emb = discord.Embed(title='Где получить роль?', color=0xff0000)
    emb.add_field(name=f'Привет друг.', value='Для того чтоб получить роль прочти <#965359487416418306>! (В самом конце есть галочка)', inline=False)
    emb.set_thumbnail(url="https://disk.yandex.ru/d/_e2Lyb0FFxV7Bw")
    sent_message = await ctx.send(embed=emb)
    await asyncio.sleep(10)
    await sent_message.delete()

@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def rules(ctx): # Создаём функцию и передаём аргумент ctx. # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.message.delete()
    emb = discord.Embed(title='!!!ПРАВИЛА!!!', color=0xff0000)
    emb.add_field(name=f'Привет друг.', value='Все правила находятся тут <#927297696761528392>! (НЕ ЗНАНИЕ ПРАВИЛ НЕ ОСВОБОЖДАЕТ ОТ ОТВЕТСТВЕННОСТИ)', inline=False)
    emb.set_thumbnail(url="https://disk.yandex.ru/d/_e2Lyb0FFxV7Bw")
    sent_message = await ctx.send(embed=emb)
    await asyncio.sleep(10)
    await sent_message.delete()

@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def privat(ctx): # Создаём функцию и передаём аргумент ctx.
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.message.delete()
    emb = discord.Embed(title='Приват-Комнаты.', color=0xff0000)
    emb.add_field(name=f'Привет друг.', value='Для того чтоб создать приват комнату присоеденись к каналу <#965643277074309210>!', inline=False)
    emb.set_thumbnail(url="https://disk.yandex.ru/d/_e2Lyb0FFxV7Bw")
    sent_message = await ctx.send(embed=emb)
    await asyncio.sleep(10)
    await sent_message.delete()

@bot.command()
async def clear(ctx, user: discord.Member):
    await ctx.message.delete()
    await ctx.channel.purge(limit=5, check=lambda m: m.author==user)

@bot.command()
@commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
async def mute(ctx, user: discord.Member, time: int, reason):
    await ctx.message.delete()
    role = user.guild.get_role(927338319543697438) # айди роли которую будет получать юзер
    role2 = user.guild.get_role (927307019092893716)
    sent_message = await ctx.send(f'{user} получил мут на {time} минут по причине: {reason}')
    await user.add_roles(role)
    await user.move_to(None)
    await user.remove_roles(role2)
    await asyncio.sleep(time * 60)
    await user.remove_roles(role)
    await user.add_roles(role2)
    await asyncio.sleep(10)
    await sent_message.delete()

@bot.command()
async def status_task():
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="DrainProject"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="за сервером 👀"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="ваши вопросы"))
        await asyncio.sleep(10)

@bot.command()
@commands.has_permissions(administrator=True)
async def mutevip(ctx, user: discord.Member, time: int, reason):
    await ctx.message.delete()
    role = user.guild.get_role(927338319543697438) # айди роли которую будет получать юзер
    rol = user.guild.get_role (927307019092893716)
    role2 = user.guild.get_role (927299470041968700)
    role4 = user.guild.get_role (927309846221553696)
    sent_message = await ctx.send(f'{user} получил мут на {time} минут по причине: {reason}')
    await user.add_roles(role)
    await user.move_to(None)
    await user.remove_roles(role2)
    await asyncio.sleep(time * 60)
    await user.remove_roles(role)
    await user.add_roles(role2)
    await asyncio.sleep(10)
    await sent_message.delete()

@bot.event
async def on_raw_reaction_add(ctx):
    if ctx.message_id == config.POST_ID:
        channel = bot.get_channel(ctx.channel_id)  # получаем объект канала
        message = await channel.fetch_message(ctx.message_id)  # получаем объект сообщения
        member = ctx.member  # получаем объект пользователя который поставил реакцию
        print(member)

        try:
            emoji = str(ctx.emoji)  # эмоджик который выбрал юзер
            role = discord.utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)

            if (len([i for i in member.roles if i and i.id not in config.EXCROLES]) <= config.MAX_ROLES_PER_USER):
                await member.add_roles(role)
                print('[SUCCESS] Пользователь {0.display_name} получил роль {1.name}'.format(member, role))
            else:
                await message.remove_reaction(ctx.emoji, member)
                print('[ERROR] Too many roles for user {0.display_name}'.format(member))

        except KeyError as e:
            print('[ERROR] KeyError, no role found for ' + emoji)
        except Exception as e:
            print(repr(e))

@bot.event
async def on_raw_reaction_remove(ctx):
    channel = bot.get_channel(ctx.channel_id)  # получаем id канала
    message = await channel.fetch_message(ctx.message_id)  # получаем id сообщения
    user_id = ctx.user_id  # по сути эта херня не нужна, но на всякий случай не трож
    member = await (await bot.fetch_guild(ctx.guild_id)).fetch_member(ctx.user_id)
    print(member, user_id)

    try:
        emoji = str(ctx.emoji)  # эмоджик который выбрал юзер
        role = discord.utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)

        await member.remove_roles(role)
        print('[SUCCESS] Роль {1.name} была убрана у пользователя {0.display_name}'.format(member, role))

    except KeyError as e:
        print('[ERROR] KeyError, no role found for ' + emoji)
    except Exception as e:
        print(repr(e))

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason):
    await ctx.message.delete()
    await ctx.channel.purge(limit=1)

    embed = discord.Embed(title='Пользователь кикнут!', color=discord.Color.red())
    embed.add_field(name='Модератор / админ:', value=ctx.message.author.mention, inline=False)
    embed.add_field(name='Нарушитель:', value=member.mention, inline=False)
    embed.add_field(name='Причина:', value=reason, inline=False)
    embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)
    await member.send(f'Вы кикнуты по причине "{reason}"!')
    await member.kick(reason=reason)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason):
    await ctx.message.delete()
    await ctx.channel.purge(limit=1)

    embed = discord.Embed(title='Пользователь забанен!', color=discord.Color.red())
    embed.add_field(name='Модератор / админ:', value=ctx.message.author.mention, inline=False)
    embed.add_field(name='Нарушитель:', value=member.mention, inline=False)
    embed.add_field(name='Причина:', value=reason, inline=False)
    embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)
    await member.send(f'Вы забанены по причине "{reason}"!')
    await member.ban(reason=reason)

@bot.command(pass_context=True)
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    await ctx.message.delete()
    channel = bot.get_channel(930952434291965992)
    banned_users = await ctx.guild.bans()
    await ctx.channel.purge(limit=0)

    for ban_entry in banned_users:
        user = ban_entry.user
        await ctx.guild.unban(user)
        emb = discord.Embed(color=0xff0000)
        emb.add_field(name='✅ UnBan пользователя', value='Пользователь {} был разбанен.'.format(member))
        await channel.send(embed = emb)
        return

@bot.command()
@commands.has_permissions(administrator=True)
async def adclear(ctx, amount=15):
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)

@bot.command()
async def info(ctx,member:discord.Member):
        await ctx.message.delete()
        emb = discord.Embed(title='✅ Информация о пользователе', color=344462)
        await ctx.channel.purge(limit=0)
        emb.add_field(name="Дата инвайта на сервер:", value=member.joined_at, inline=False)
        emb.add_field(name="Никнейм:", value=member.display_name, inline=False)
        emb.add_field(name= "Айди:", value=member.id, inline=False)
        emb.add_field(name= "Аккаунт создан:", value=member.created_at.strftime("%a,%#d %B %Y, %I:%M %p UTC"), inline=False)
        table = [["nickname", "cash", "lvl", "xp"]]
        for row in cursor.execute(f"SELECT nickname,cash,lvl,xp FROM users where id={ctx.author.id}"):
            table.append([row[0], row[1], row[2], row[3]])
            emb.add_field(name=f"\n{tabulate(table)}", value=f"Ваша статистика.", inline=False)
        emb.set_thumbnail(url=member.avatar_url)
        emb.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        await ctx.author.send(embed = emb)
        msg = await ctx.send('***Подробная информация о пользоваетеле была отправлена в личные сообщения.***')
        await asyncio.sleep(30)
        await msg.delete()

@bot.command()
async def feed(ctx):
    await ctx.message.delete()
    embed1 = discord.Embed(
        title="Мы Вконтакте",
        description="Ссылка для перехода на vk",
        url='https://vk.com/drainproject',
    )
    embed2 = discord.Embed(
        title="Аднминистратор",
        description="Ссылка для перехода на vk",
        url='https://vk.com/kakoitoebanat',
    )
    embed3 = discord.Embed(
        title="Наш Steam",
        description="Ссылка для перехода на Steam",
        url='https://steamcommunity.com/groups/DrainProject',
    )
    embed4 = discord.Embed(
        title="Steam Администрации",
        description="Ссылка для перехода на Steam",
        url='https://steamcommunity.com/id/1337y0uSh4/',
    )
    msg1 = await ctx.send(embed=embed1)
    msg2 = await ctx.send(embed=embed2)
    msg3 = await ctx.send(embed=embed3)
    msg4 = await ctx.send(embed=embed4)
    await asyncio.sleep(30)
    await msg1.delete()
    await msg2.delete()
    await msg3.delete()
    await msg4.delete()

@bot.command()
async def ping(ctx): # Объявление асинхронной функции __ping с возможностью публикации сообщения
    await ctx.message.delete()
    ping = bot.ws.latency # Получаем пинг клиента

    ping_emoji = '🟩🟩🟩🟩🟩' # Эмоция пинга, если он меньше 100ms

    if ping > 0.10000000000000000:
        ping_emoji = '🟩🟩🟩🟨🟨' # Эмоция пинга, если он больше 100ms

    if ping > 0.15000000000000000:
        ping_emoji = '🟩🟩🟨🟨🟨' # Эмоция пинга, если он больше 150ms

    if ping > 0.20000000000000000:
        ping_emoji = '🟨🟨🟨🟨🟨' # Эмоция пинга, если он больше 200ms

    if ping > 0.25000000000000000:
        ping_emoji = '🟨🟨🟨🟥🟥' # Эмоция пинга, если он больше 250ms

    if ping > 0.30000000000000000:
        ping_emoji = '🟨🟨🟥🟥🟥' # Эмоция пинга, если он больше 300ms

    if ping > 0.35000000000000000:
        ping_emoji = '🟥🟥🟥🟥🟥' # Эмоция пинга, если он больше 350ms

    message = await ctx.send('Пожалуйста, подождите. . .') # Переменная message с первоначальным сообщением
    await message.edit(content = f'Пинг: {ping_emoji} `{ping * 1000:.0f}ms`') # Редактирование первого сообщения на итоговое (на сам пинг)
    await asyncio.sleep(20)
    await message.delete()

@bot.command()
async def weather(ctx, *, city: str):
    await ctx.message.delete()
    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    channel = ctx.message.channel
    if x["cod"] != "404":
        async with channel.typing():
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsiuis = str(round(current_temperature - 273.15))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Погода {city_name}", color=ctx.guild.me.top_role.color, timestamp=ctx.message.created_at, )
            embed.add_field(name="Темпиратура(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
            embed.add_field(name="Влажность(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Давление(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://e7.pngegg.com/pngimages/377/815/png-clipart-computer-icons-weather-weather-heart-weather-forecasting.png")
            embed.set_footer(text=f"Выведено для {ctx.author.name}")
        msg = await channel.send(embed=embed)
        await asyncio.sleep(10)
        await msg.delete()
    else:
        msg2 = await channel.send("Город не найден.")
        await asyncio.sleep(10)
        await msg2.delete()

@bot.command()
async def help(ctx):
    await ctx.message.delete()
    embed1 = discord.Embed(title="Основные команды", color=0xff0000)
    embed1.add_field(name='{}role'.format(settings['prefix']), value='Информация о том где можно получить роль.', inline=False)
    embed1.add_field(name='{}feed'.format(settings['prefix']), value='Информация о том где можно нас найти.', inline=False)
    embed1.add_field(name='{}ping'.format(settings['prefix']), value='Информация о вашем пинге на сервере.', inline=False)
    embed1.add_field(name='{}info @пользователь'.format(settings['prefix']), value='Информация о вас отправляется вам в личные сообщения (Опыт, уровень, монеты).', inline=False)
    embed1.add_field(name='{}weather (Город)'.format(settings['prefix']), value='Информация о погоде в написанном городе (Занимаюсь доработкой команды)', inline=False)
    embed1.add_field(name='{}stats'.format(settings['prefix']), value='Статистика активности сервера.', inline=False)
    embed1.add_field(name='{}rules'.format(settings['prefix']), value='Правила сервера. Обязательны к прочтению для воизбежания конфликтов.', inline=False)
    embed1.add_field(name='{}privat'.format(settings['prefix']), value='Приват комнаты. Не узнаешь что это пока не попробуешь.', inline=False)
    embed1.set_thumbnail(url="https://psv4.userapi.com/c240331/u494765878/docs/d9/c9dc55248065/vETcSBfEms4.jpg?extra=CI4Nlb36pUEorsuslEnMGTK6EyKHfpP29NiMHSzDonKAiRZM_6XSA0OsEPICgZsPPxt-B3vDVIu-HMlVo7aVkWJgcCs46mprqXJapB4qIGI0cGtxighoKuYbWREYPhpSyHTqR5slvybMwGADTTz1yw")
    embed2 = discord.Embed(title="Команды администрации", color=0xff0000)
    embed2.add_field(name='{}clear @(ваш ник)'.format(settings['prefix']), value='Очистка чата от ваших сообщений.', inline=False)
    embed2.add_field(name='{}adclear'.format(settings['prefix']), value='Очистка чата (Для администраторов от <@&927308500420411423> и выше).', inline=False)
    embed2.add_field(name='{}ban @пользователь (*) (Причина)'.format(settings['prefix']), value='Бан пользователя (Для администраторов от <@&927308500420411423> и выше).', inline=False)
    embed2.add_field(name='{}unban @пользователь'.format(settings['prefix']), value='Разбан пользователя (Для администраторов от <@&927308500420411423> и выше).', inline=False)
    embed2.add_field(name='{}mute @пользователь (Время) (Причина)'.format(settings['prefix']), value='Для администраторов по типу <@&927309846221553696>, <@&927299202457940059> и выше.', inline=False)
    embed2.add_field(name='{}mutevip @(vip)пользователь (Время) (Причина)'.format(settings['prefix']), value='Для администраторов от <@&927308500420411423> и выше.', inline=False)
    embed2.set_thumbnail(url="https://psv4.userapi.com/c240331/u494765878/docs/d9/c9dc55248065/vETcSBfEms4.jpg?extra=CI4Nlb36pUEorsuslEnMGTK6EyKHfpP29NiMHSzDonKAiRZM_6XSA0OsEPICgZsPPxt-B3vDVIu-HMlVo7aVkWJgcCs46mprqXJapB4qIGI0cGtxighoKuYbWREYPhpSyHTqR5slvybMwGADTTz1yw")
    embed3 = discord.Embed(title="Команды приват комнат", color=0xff0000)
    embed3.add_field(name='{}hide'.format(settings['prefix']), value='Прячет вашу приват комнату от посторонних лиц.', inline=False)
    embed3.add_field(name='{}unhide'.format(settings['prefix']), value='Делает вашу приват комнату снова видимой.', inline=False)
    embed3.add_field(name='{}lock'.format(settings['prefix']), value='Блокирует вашу приват комнату от посторонних лиц.', inline=False)
    embed3.add_field(name='{}unlock'.format(settings['prefix']), value='Разблокирует вашу приват комнату.', inline=False)
    embed3.add_field(name='{}name'.format(settings['prefix']), value='Задает имя вашей приват комнате.', inline=False)
    embed3.add_field(name='{}rkick'.format(settings['prefix']), value='Кикает нежелательного гостя с вашей приват комнаты.', inline=False)
    embed3.add_field(name='{}limit'.format(settings['prefix']), value='Задает лимит количества участников в вашей приват комнате.', inline=False)
    embed3.set_thumbnail(url="https://psv4.userapi.com/c240331/u494765878/docs/d9/c9dc55248065/vETcSBfEms4.jpg?extra=CI4Nlb36pUEorsuslEnMGTK6EyKHfpP29NiMHSzDonKAiRZM_6XSA0OsEPICgZsPPxt-B3vDVIu-HMlVo7aVkWJgcCs46mprqXJapB4qIGI0cGtxighoKuYbWREYPhpSyHTqR5slvybMwGADTTz1yw")
    embed4 = discord.Embed(title="Команды Магазина", color=0xff0000)
    embed4.add_field(name='{}balance @(Пользователь)'.format(settings['prefix']), value='Баланс пользователя.', inline=False)
    embed4.add_field(name='{}shop'.format(settings['prefix']), value='Магазин. Товар и цены.', inline=False)
    embed4.add_field(name='{}buy (id роли)'.format(settings['prefix']), value='Команда покупки роли. (ID роли написанны тут <#965359487416418306>, в самом низу во вкладке ROLES)', inline=False)
    embed4.add_field(name='{}give_cash @(Пользователь)'.format(settings['prefix']), value='Выдать деньги пользователю.(Для администраторов от <@&927308500420411423> и выше)', inline=False)
    embed4.add_field(name='Вы также можете купить себе роль.', value='Пропишите команду !feed и напишите Администратору.', inline=False)
    embed4.add_field(name='Что добавить?', value='Вы можете написать свое предложение сюда <#927342232099504138>.', inline=False)
    embed4.set_thumbnail(url="https://psv4.userapi.com/c240331/u494765878/docs/d9/c9dc55248065/vETcSBfEms4.jpg?extra=CI4Nlb36pUEorsuslEnMGTK6EyKHfpP29NiMHSzDonKAiRZM_6XSA0OsEPICgZsPPxt-B3vDVIu-HMlVo7aVkWJgcCs46mprqXJapB4qIGI0cGtxighoKuYbWREYPhpSyHTqR5slvybMwGADTTz1yw")
    embeds = [embed1, embed2, embed3, embed4]
    message = await ctx.send(embed=embed1)
    page = Paginator(bot, message, only=ctx.author, use_more=False, embeds=embeds, footer=False)
    await page.start()
    await asyncio.sleep(30)
    await message.delete()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        now = datetime.now()
        await ctx.message.delete()
        embed1 = discord.Embed(title=f"Такой команды не существует, воспользуйтесь справкой, введя {config.PREFIX}help.'", color=0xff0000)
        embed1.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        message = await ctx.send(embed=embed1)
        await asyncio.sleep(10)
        await message.delete()
    else:
        print(error)

@kick.error
@ban.error
@unban.error
@mute.error
@mutevip.error
@give_cash.error
async def moderation_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f'{ctx.author.mention}, вы неверно ввели аргументы, воспользуйтесь командой {config.PREFIX}help для справки.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас недостаточно прав для выполнения данной команды.')

bot.run(settings['token'])
