import aiohttp
import disnake
from disnake.ext import commands
import random
import config  # Импортируем конфигурационные параметры из файла config.py

# Создаем объект бота
bot = commands.Bot(command_prefix=config.PREFIX)

# Словарь для хранения баланса пользователей
balances = {}

# Словарь для хранения опыта пользователей
experience = {}

# Словарь для хранения уровней пользователей
levels = {}

# Функция для проверки баланса пользователя
def check_balance(user_id):
    if user_id not in balances:
        balances[user_id] = 100  # Начальный баланс 100
    return balances[user_id]

# Функция для проверки опыта пользователя
def check_experience(user_id):
    if user_id not in experience:
        experience[user_id] = 0  # Начальный опыт 0
    return experience[user_id]

# Функция для проверки уровня пользователя
def check_level(user_id):
    if user_id not in levels:
        levels[user_id] = 1  # Начальный уровень 1
    return levels[user_id]

# Команда для проверки баланса
@bot.command()
async def баланс(ctx):
    balance = check_balance(ctx.author.id)
    await ctx.send(f'Ваш текущий баланс: {balance} денег.')

# Команда для рулетки
@bot.command()
async def рулетка(ctx, ставка: int):
    if ставка <= 0:
        await ctx.send("Ставка должна быть положительным числом.")
        return
    
    balance = check_balance(ctx.author.id)
    if balance < ставка:
        await ctx.send("У вас недостаточно денег для этой ставки.")
        return
    
    результат = random.choice(['выигрыш', 'проигрыш'])
    if результат == 'выигрыш':
        выигрыш = ставка * 2
        balances[ctx.author.id] += выигрыш
        await ctx.send(f'Поздравляем! Вы выиграли {выигрыш} денег.')
    else:
        balances[ctx.author.id] -= ставка
        await ctx.send('Увы, вы проиграли.')

# Команда для получения лидерборда богачей
@bot.command()
async def лидерборд(ctx):
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
    leaderboard = '\n'.join([f'{idx+1}. <@{user_id}>: {balance} денег' for idx, (user_id, balance) in enumerate(sorted_balances)])
    await ctx.send(f'Лидерборд:\n{leaderboard}')

# Команда для заработка денег
@bot.command()
async def заработать(ctx):
    balance = check_balance(ctx.author.id)
    заработок = random.randint(1, 50)
    balances[ctx.author.id] += заработок
    await ctx.send(f'Вы заработали {заработок} денег.')

# Команда для получения опыта
@bot.event
async def on_message(message):
    if not message.author.bot:
        опыт = random.randint(1, 10)
        experience[message.author.id] += опыт
        await bot.process_commands(message)

# Команда для просмотра опыта и уровня
@bot.command()
async def ранг(ctx, участник: disnake.Member = None):
    участник = участник or ctx.author
    опыт = check_experience(участник.id)
    уровень = check_level(участник.id)
    await ctx.send(f'У {участник} {опыт} опыта и {уровень} уровень.')

# Административные команды

# Команда для сброса ранга
@bot.command()
@commands.has_permissions(administrator=True)
async def сброс_ранга(ctx, участник: disnake.Member):
    experience[участник.id] = 0
    levels[участник.id] = 1
    await ctx.send(f'Ранг {участник} был сброшен.')

# Команда для установки ранга
@bot.command()
@commands.has_permissions(administrator=True)
async def установить_ранг(ctx, участник: disnake.Member, опыт: int, уровень: int):
    experience[участник.id] = опыт
    levels[участник.id] = уровень
    await ctx.send(f'Ранг {участник} был установлен на {опыт} опыта и {уровень} уровень.')

# Приветственное сообщение при входе нового пользователя
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f'Добро пожаловать, {member.mention} на сервер! Не забудь ознакомиться с правилами.')

# Прощальное сообщение при выходе пользователя
@bot.event
async def on_member_remove(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f'{member.name} покинул сервер. Мы будем скучать по нему.')

# Команда для вывода информации о сервере
@bot.command()
async def сервер(ctx):
    server = ctx.guild
    total_members = server.member_count
    online_members = sum(member.status != disnake.Status.offline for member in server.members)
    text_channels = len(server.text_channels)
    voice_channels = len(server.voice_channels)
    total_channels = text_channels + voice_channels
    server_owner = server.owner
    server_region = server.region
    verification_level = server.verification_level.name
    embed = disnake.Embed(title=f"Информация о сервере {server.name}", color=0x7289DA)
    embed.set_thumbnail(url=server.icon_url)
    embed.add_field(name="Владелец", value=server_owner.mention, inline=False)
    embed.add_field(name="Регион", value=server_region, inline=True)
    embed.add_field(name="Уровень проверки", value=verification_level, inline=True)
    embed.add_field(name="Всего участников", value=total_members, inline=False)
    embed.add_field(name="Онлайн", value=online_members, inline=True)
    embed.add_field(name="Текстовые каналы", value=text_channels, inline=True)
    embed.add_field(name="Голосовые каналы", value=voice_channels, inline=True)
    embed.add_field(name="Всего каналов", value=total_channels, inline=False)
    await ctx.send(embed=embed)

# Команда для проверки задержки бота
@bot.command()
async def пинг(ctx):
    latency = bot.latency * 1000  # Преобразуем в миллисекунды
    await ctx.send(f'Пинг бота: {latency:.2f} мс')

# Команда для вывода информации о боте
@bot.command()
async def инфо(ctx):
    embed = disnake.Embed(title="Информация о боте", color=0x7289DA)
    embed.add_field(name="Автор", value="Your Name", inline=False)
    embed.add_field(name="Используемая библиотека", value="disnake", inline=False)
    embed.add_field(name="Версия", value="1.0", inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=embed)

# Команда для предложения новой команды
@bot.command()
async def предложить_команду(ctx, *, команда):
    owner = await bot.fetch_user(config.Config.OWNER_ID)
    await owner.send(f'Пользователь {ctx.author} предложил новую команду: {команда}')

# Команда для калькулятора
@bot.command()
async def калькулятор(ctx, *, выражение):
    try:
        результат = eval(выражение)
        await ctx.send(f'Результат: {результат}')
    except Exception as e:
        await ctx.send(f'Произошла ошибка: {e}')

# Команда для повторения текста
@bot.command()
async def повтори(ctx, *, текст):
    await ctx.send(текст)

# Команда для получения случайного ответа от шара судьбы
@bot.command()
async def шар(ctx, *, вопрос):
    ответы = [
        "Бесспорно", "Предрешено", "Никаких сомнений", "Определённо да", "Можешь быть уверен в этом",
        "Мне кажется — «да»", "Вероятнее всего", "Хорошие перспективы", "Знаки говорят — «да»",
        "Да", "Пока не ясно, попробуй снова", "Спроси позже", "Лучше не рассказывать",
        "Сейчас нельзя предсказать", "Сконцентрируйся и спроси опять", "Даже не думай",
        "Мой ответ — «нет»", "По моим данным — «нет»", "Перспективы не очень хорошие", "Весьма сомнительно"
    ]
    ответ = random.choice(ответы)
    await ctx.send(f'Ваш вопрос: {вопрос}\nМой ответ: {ответ}')

# Команда для генерации случайного числа
@bot.command()
async def число(ctx, начало: int, конец: int):
    случайное_число = random.randint(начало, конец)
    await ctx.send(f'Случайное число между {начало} и {конец}: {случайное_число}')

# Команда для броска монетки
@bot.command()
async def монетка(ctx):
    результат = random.choice(['орёл', 'решка'])
    await ctx.send(f'Выпало: {результат}')

# Команда для отправки случайной картинки с животными
@bot.command()
async def кот(ctx):
    await ctx.send('https://cataas.com/cat')

@bot.command()
async def собака(ctx):
    await ctx.send('https://random.dog/woof.json')

@bot.command()
async def слоник(ctx):
    await ctx.send('https://elephant-api.herokuapp.com/pictures/random')

@bot.command()
async def флажок(ctx):
    await ctx.send('https://www.randomflag.net/random')

# Команда для получения случайной цитаты
@bot.command()
async def цитата(ctx):
    цитаты = [
        "Мы не можем поменять направление ветра, но можем поднять паруса, чтобы достичь своей цели. – Джимми Дин",
        "Сложно предсказать, куда дует ветер. Но мы всегда можем решить, как поднять паруса. – Л. Толстой",
        "Не жди, что произойдет что-то хорошее, — рискни, что-то сделать сам. – Паульо Коэльо",
        "Любой путь, который ты выбираешь, будет неизбежно трудным. – Харлан Эллисон",
        "Успех — это способность идти от одной неудачи к другой, не теряя энтузиазма. – Уинстон Черчилль",
        "Успех — это способность сделать из неудачи последний шаг к тому, что вы хотели достичь. – Д.В. Линдсли"
    ]
    цитата = random.choice(цитаты)
    await ctx.send(цитата)

# Команда для получения случайного GIF
@bot.command()
async def гиф(ctx, тема: str):
    api_key = 'your_giphy_api_key'  # Замените на свой API-ключ GIPHY
    url = f'http://api.giphy.com/v1/gifs/random?api_key={api_key}&tag={тема}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            gif_url = data['data']['image_url']
            await ctx.send(gif_url)

# Команда для отправки случайной картинки с пандой
@bot.command()
async def панда(ctx):
    await ctx.send('https://some-random-api.ml/img/panda')

# Команда для отправки случайной картинки с лисой
@bot.command()
async def лиса(ctx):
    await ctx.send('https://some-random-api.ml/img/fox')

# Команда для отправки случайной картинки с птицей
@bot.command()
async def птица(ctx):
    await ctx.send('https://some-random-api.ml/img/birb')

# Команда для отправки случайной картинки с мемом
@bot.command()
async def мем(ctx):
    await ctx.send('https://some-random-api.ml/meme')

# Команда для отправки случайной картинки с котом
@bot.command()
async def кот(ctx):
    await ctx.send('https://some-random-api.ml/img/cat')

# Команда для отправки случайной картинки с собакой
@bot.command()
async def собака(ctx):
    await ctx.send('https://some-random-api.ml/img/dog')

# Команда для отправки случайной картинки с драконом
@bot.command()
async def дракон(ctx):
    await ctx.send('https://some-random-api.ml/img/dragon')

# Команда для отправки случайной картинки с пингвином
@bot.command()
async def пингвин(ctx):
    await ctx.send('https://some-random-api.ml/img/penguin')

# Команда для отправки случайной картинки с редким животным
@bot.command()
async def редкое_животное(ctx):
    await ctx.send('https://some-random-api.ml/img/redpanda')

# Команда для отправки случайной картинки с оленем
@bot.command()
async def олень(ctx):
    await ctx.send('https://some-random-api.ml/img/deer')

# Команда для отправки случайной картинки с орлом
@bot.command()
async def орел(ctx):
    await ctx.send('https://some-random-api.ml/img/eagle')

# Команда для отправки случайной картинки с гориллой
@bot.command()
async def горилла(ctx):
    await ctx.send('https://some-random-api.ml/img/gorilla')

# Команда для отправки случайной картинки с рысью
@bot.command()
async def рысь(ctx):
    await ctx.send('https://some-random-api.ml/img/lynx')

# Команда для отправки случайной картинки с енотом
@bot.command()
async def енот(ctx):
    await ctx.send('https://some-random-api.ml/img/raccoon')

# Команда для отправки случайной картинки с белкой
@bot.command()
async def белка(ctx):
    await ctx.send('https://some-random-api.ml/img/squirrel')

# Команда для отправки случайной картинки с буйволом
@bot.command()
async def буйвол(ctx):
    await ctx.send('https://some-random-api.ml/img/buffalo')

# Команда для отправки случайной картинки с крокодилом
@bot.command()
async def крокодил(ctx):
    await ctx.send('https://some-random-api.ml/img/crocodile')

# Команда для отправки случайной картинки с ламой
@bot.command()
async def лама(ctx):
    await ctx.send('https://some-random-api.ml/img/llama')

# Команда для отправки случайной картинки с лосем
@bot.command()
async def лось(ctx):
    await ctx.send('https://some-random-api.ml/img/moose')

# Команда для отправки случайной картинки с дельфином
@bot.command()
async def дельфин(ctx):
    await ctx.send('https://some-random-api.ml/img/dolphin')

# Команда для отправки случайной картинки с попугаем
@bot.command()
async def попугай(ctx):
    await ctx.send('https://some-random-api.ml/img/parrot')

# Команда для отправки случайной картинки с рыбой
@bot.command()
async def рыба(ctx):
    await ctx.send('https://some-random-api.ml/img/fish')

# Команда для отправки случайной картинки с черепахой
@bot.command()
async def черепаха(ctx):
    await ctx.send('https://some-random-api.ml/img/turtle')

# Команда для отправки случайной картинки с кенгуру
@bot.command()
async def кенгуру(ctx):
    await ctx.send('https://some-random-api.ml/img/kangaroo')

# Команда для отправки случайной картинки с змеей
@bot.command()
async def змея(ctx):
    await ctx.send('https://some-random-api.ml/img/snake')

# Команда для отправки случайной картинки с жирафом
@bot.command()
async def жираф(ctx):
    await ctx.send('https://some-random-api.ml/img/giraffe')

# Команда для отправки случайной картинки с волком
@bot.command()
async def волк(ctx):
    await ctx.send('https://some-random-api.ml/img/wolf')

# Команда для отправки случайной картинки с медведем
@bot.command()
async def медведь(ctx):
    await ctx.send('https://some-random-api.ml/img/bear')

# Команда для игры в крестики-нолики
@bot.command()
async def крестики_нолики(ctx, *, choice: str):
    choices = ['камень', 'ножницы', 'бумага']
    bot_choice = random.choice(choices)
    if choice == bot_choice:
        await ctx.send(f'Ничья! Бот тоже выбрал {bot_choice}.')
    elif (choice == 'камень' and bot_choice == 'ножницы') or (choice == 'ножницы' and bot_choice == 'бумага') or (choice == 'бумага' and bot_choice == 'камень'):
        await ctx.send(f'Вы победили! Бот выбрал {bot_choice}.')
    else:
        await ctx.send(f'Вы проиграли! Бот выбрал {bot_choice}.')

# Запускаем бота
bot.run(config.TOKEN)
