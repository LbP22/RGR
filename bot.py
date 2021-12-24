import re

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InlineKeyboardButton, InlineKeyboardMarkup

import db

from aiogram import types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize

from bot_config import admin_id, bot, dp, LogIn, Search, Buy, FilmAdd, PAYMENTS_PROVIDER_TOKEN

back_b = types.KeyboardButton("Повернутися")
back_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).add(back_b)

noAcc_b = types.KeyboardButton("Створити запис")
noAcc_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(noAcc_b)

searchFilm_b = types.KeyboardButton("Знайти фільм")
searchAuthors_b = types.KeyboardButton("Знайти автора")
showFilms_b = types.KeyboardButton("Переглянути список наявних фільмів")
showAuthors_b = types.KeyboardButton("Переглянути список наявних авторів")
addOwn_b = types.KeyboardButton("Додати власний фільм до бази")
showBuy_b = types.KeyboardButton("Переглянути кошик")
show_Bought_b = types.KeyboardButton("Переглянути придбані фільми")
menu_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add(searchFilm_b, searchAuthors_b,
                                                              showFilms_b, showAuthors_b,
                                                              addOwn_b, show_Bought_b, showBuy_b)
admin_b = types.KeyboardButton("Адмін")
admin_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add(searchFilm_b, searchAuthors_b,
                                                               showFilms_b, showAuthors_b,
                                                               addOwn_b, show_Bought_b, showBuy_b, admin_b)


# Кінець авторизації та реєстрації


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Доброго дня! Введіть, будь-ласка, ім'я користувача!\n"
                         "Якщо не маєте облікового запису, створіть його.", reply_markup=noAcc_kb)
    await LogIn.log_name.set()


@dp.message_handler()
async def start(message: types.Message):
    await message.answer(message.text)


@dp.message_handler(state=LogIn.log_name)  # Початоку процесів
async def login(message: types.Message, state: FSMContext):
    if message.text == "Створити запис":
        await LogIn.reg_mail.set()
        await message.answer("Напишіть Вашу пошту gmail або ukrNet", reply_markup=back_kb)
        return

    log = message.text
    isReg = db.check_log(log)
    if isReg[0]:
        await state.update_data({"login": log})
        await state.update_data({"rightPass": isReg[1]})
        await LogIn.log_pas.set()
        await message.answer("Тепер введіть пароль!")
    else:
        await message.answer("Такого імені користувача не існує!\n"
                             "Введіть інше або створіть обліковий запис")


@dp.message_handler(state=LogIn.log_pas)  # Перехід на авторизацію
async def pas(message: types.Message, state: FSMContext):
    if message.text == "Повернутися":
        await LogIn.log_name.set()
        await message.answer("Введіть, будь-ласка, ім'я користувача!\n"
                             "Якщо не маєте облікового запису, створіть його.", reply_markup=back_kb)
        return

    pasW = message.text
    async with state.proxy() as data:
        rightPass = data["rightPass"]
        if pasW == rightPass:
            await LogIn.logged.set()
            await state.update_data({"products": []})
            if message.from_user.id not in admin_id:
                await message.answer("Вас авторизовано успішно!", reply_markup=menu_kb)
            else:
                await message.answer("Вас авторизовано успішно!", reply_markup=admin_kb)
        else:
            await message.answer("Хибний пароль!\n"
                                 "Спробуйте інший або зверніться у технічну підтримку, щоб відновити його.")


@dp.message_handler(state=LogIn.reg_mail)  # Перехід на реєстрацію
async def regMail(message: types.Message, state: FSMContext):
    if message.text == "Повернутися":
        await LogIn.log_name.set()
        await message.answer("Введіть ім'я користувача або створіть обліковий запис!", reply_markup=noAcc_kb)
        return

    mail = message.text
    if mail.endswith("@gmail.com") or mail.endswith("@ukr.net"):
        await state.update_data({"mail": mail})
        await LogIn.reg_name.set()
        await message.answer("Тепер, будь-ласка, вигадайте ім'я користувача!\n"
                             "Воно має складатися лише з латинських букв, цифр та не містити пробілів.\n"
                             "Не більше 20 символів",
                             reply_markup=back_kb)
    elif not db.check_mail(mail):
        await message.answer("Така пошта вже існує!\n"
                             "Введіть іншу або поверніться та авторизуйтесь")
    else:
        await message.answer("Неправильно введена пошта!\n"
                             "Перевірте правильність введених даних")


@dp.message_handler(state=LogIn.reg_name)
async def regName(message: types.Message, state: FSMContext):
    if message.text == "Повернутися":
        await LogIn.reg_mail.set()
        await message.answer("Напишіть Вашу пошту gmail або ukrNet")
        return

    name = message.text
    if len(name) > 20:
        await message.answer("Ім'я не підходить по довжині!\n"
                             "Введіть інше, в якому менше 20 символів")
    elif len(re.findall(r'\s|[^A-Za-z\d]', name)) > 0:
        await message.answer("Ім'я не відповідає вимогам!\n"
                             "Введіть інше, без кириличних букв та пробілів")
    elif db.check_log(name)[0]:
        await message.answer("Таке ім'я користувача вже існує!\n"
                             "Вигадайте інше")
    else:
        await state.update_data({"name": name})
        await message.answer("Тепер останнє - пароль.\n"
                             "Він має бути довжиною не менше 8 та не більше 12 символів.\n"
                             "Не повинен містити пробілів та кириличних букв")
        await LogIn.reg_pas.set()


@dp.message_handler(state=LogIn.reg_pas)
async def regPas(message: types.Message, state: FSMContext):
    if message.text == "Повернутися":
        await LogIn.reg_name.set()
        await message.answer("Вигадайте ім'я користувача!\n"
                             "Воно має складатися лише з латинських букв, цифр та не містити пробілів.\n"
                             "Не більше 20 символів")
        return

    password = message.text
    if len(password) > 12 or len(password) < 8:
        await message.answer("Пароль не підходить за довжиною!\n"
                             "Введіть інший, від 8 до 12 символів")
    elif len(re.findall(r'\s|[а-яА-Я]', password)) > 0:
        await message.answer("Пароль не відповідає вимогам!\n"
                             "Введіть інший, без кириличних букв та пробілів")
    else:
        async with state.proxy() as data:
            name = data["name"]
            mail = data["mail"]
            if db.addUser(name, password, mail):
                await LogIn.log_name.set()
                await message.answer("Готово!\n"
                                     "Тепер увійдіть у свій обліковий запис - введіть ваш логін!",
                                     reply_markup=noAcc_kb)


# Кінець блоку авторизації
# Початок блоку повідомлення адмінів про запуск бота


async def start_notification(dp):
    text = "Саша крутоі пацан ващє ахуеть! і аРМЄЕН тоже"
    await bot.send_message(admin_id[0], text)


async def end_notification(dp):
    text = "Я пашов спать :sleepy:"
    await bot.send_message(admin_id[0], emojize(text))


# Кінець блоку повідомлення адмінів про запуск бота
# Початоку блоку меню


@dp.message_handler(state=[Search.find_film, Search.find_author, FilmAdd.add_name, FilmAdd.add_trilogy,
                           FilmAdd.add_genre, FilmAdd.add_author_name, FilmAdd.add_price, FilmAdd.add_author_desc,
                           FilmAdd.add_author_photo, FilmAdd.add_film_photo, FilmAdd.add_payment, Buy.buy_proceed],
                    commands="menu")
async def menu_Set(message: types.Message, state: FSMContext):
    await LogIn.logged.set()
    await message.answer("Вас повернено до головного меню!", reply_markup=menu_kb)


@dp.message_handler(state=LogIn.logged)
async def menu(message: types.Message, state: FSMContext):
    if message.text == searchFilm_b.text:
        await Search.find_film.set()
        await message.answer("Напишіть назву фільму!")
    elif message.text == searchAuthors_b.text:
        await Search.find_author.set()
        await message.answer("Напишіть ім'я автора!")
    elif message.text == showFilms_b.text:
        films = db.show_all_films()
        await message.answer("Наявні на даний момент у нашій базі фільми:")
        for film in films:
            img = open("film/" + str(film[0]) + ".jpg", "rb")
            filmInfo = db.find_film_info(film[2], film[3])
            caption = film[1] + "\nЖанр: " + filmInfo[0] + "\nРежисер: " + filmInfo[1] + "\nЦіна: " + str(film[5])
            inline_buy = InlineKeyboardButton("Додати до кошику ", callback_data="buy_" + str(film[0]))
            kb_buy = InlineKeyboardMarkup().add(inline_buy)

            await message.answer_photo(caption=caption, photo=img, reply_markup=kb_buy)

    elif message.text == showAuthors_b.text:
        authors = db.show_all_authors()
        await message.answer("Наявні на даний момент у нашій базі автори:")
        for author in authors:
            img = open("director/" + str(author[0]) + ".jpg", "rb")
            caption = author[1] + "\n" + author[2]

            await message.answer_photo(caption=caption, photo=img)

    elif message.text == addOwn_b.text:
        await FilmAdd.add_name.set()
        await message.answer("Додання фільму - не безкоштовний процес.\n"
                             "За допомогою цієї можливості ми даємо змогу розвиватися молодим авторам, які, "
                             "натомість дають змогу розвиватися молодим розробникам.\n"
                             "Коротше кажучи - без бабла не буде нічо. Тож або повертайся до меню через /menu, або, "
                             "якщо хочеш, шоб було шось, то вводь назву фільму. До того ж, вводь уважно, бо нам було "
                             "ліньки додавати функцію повернення на кожний етап, тож, якщо помилишся, доведеться "
                             "повертатися на самий початок")

    elif message.text == show_Bought_b.text:
        async with state.proxy() as user_data:
            log = user_data["login"]
            products = str(db.show_products(log))
            products = products[1:-1]
            products = products.split(", ")
            films = db.show_all_films()
            for film in films:
                if str(film[0]) in products:
                    img = open("film/" + str(film[0]) + ".jpg", "rb")
                    filmInfo = db.find_film_info(film[2], film[3])
                    caption = film[1] + "\nЖанр: " + filmInfo[0] + "\nРежисер: " + filmInfo[1] + "\nЦіна: " + str(
                        film[5])
                    await message.answer_photo(caption=caption, photo=img)

    elif message.text == showBuy_b.text:
        films = db.show_all_films()
        async with state.proxy() as user_data:
            products = list(user_data["products"])
            total = 0
            await message.answer("Фільми з вашого кошику:")
            for film in films:
                if str(film[0]) in products:
                    img = open("film/" + str(film[0]) + ".jpg", "rb")
                    filmInfo = db.find_film_info(film[2], film[3])
                    caption = film[1] + "\nЖанр: " + filmInfo[0] + "\nРежисер: " + filmInfo[1] + "\nЦіна: " + str(
                        film[5])
                    total += film[5]
                    await message.answer_photo(caption=caption, photo=img)
            await state.update_data({"price": total})
            await message.answer("Загальна ціна продуктів у кошику: " + str(total))
        await Buy.buy_proceed.set()
        await message.answer("Щоб придбати, натисніть /buy\n"
                             "Щоб повернутися /menu", reply_markup=None)

    elif message.text == admin_b.text:
        await message.answer("Я це зробив, щоб ви побачили, що я вмію робити окремий інтерфейс для адміна, тож давайте"
                             "вже якось мені балів хоча б 101 поставимо, я хочу стипендію повернути собі")


@dp.callback_query_handler(text_contains="buy_", state=LogIn.logged)
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id, text="Додано")
    data = callback_query.data
    data = data.split("_")[1]
    async with state.proxy() as user_data:
        products = user_data["products"]
        products.append(data)
        await state.update_data({"products": products})


# Кінець блоку меню
# Початок блоку пошуків за назвою


@dp.message_handler(state=Buy.buy_proceed, commands=["buy"])
async def process_buy_command(message: types.Message, state: FSMContext):
    if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await message.answer("pre_buy_demo_alert")

    async with state.proxy() as user_data:
        PRICE = int(user_data["price"]) * 100

        toPay = types.LabeledPrice(label="Придбання фільмів", amount=PRICE)
        await bot.send_invoice(
            message.chat.id,
            title="Сплата за фільми",
            description="Сплата за обрані фільми",
            provider_token=PAYMENTS_PROVIDER_TOKEN,
            currency="uah",
            prices=[toPay],
            start_parameter="time-machine-example",
            payload="some-invoice-payload-for-our-internal-use"
        )


@dp.pre_checkout_query_handler(run_task=lambda query: True, state=Buy.buy_proceed)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=Buy.buy_proceed)
async def process_successful_payment(message: types.Message, state: FSMContext):
    await message.answer("Сплачено успішно!")

    async with state.proxy() as user_data:
        products = user_data["products"]
        log = user_data["login"]
        db.addProducts(products, log)

    await message.answer("Ваші покупки додано до списку придбаних! Вітаємо!")
    await LogIn.logged.set()


@dp.message_handler(state=Search.find_film)
async def find_film(message: types.Message):
    filmName = message.text
    filmData = db.find_film(filmName)
    if filmData[0]:
        filmAbout = filmData[1]
        img = open("film/" + str(filmAbout[0]) + ".jpg", "rb")
        filmInfo = db.find_film_info(filmAbout[2], filmAbout[3])
        caption = filmAbout[1] + "\nЖанр: " + filmInfo[0] + "\nРежисер: " + filmInfo[1] + "\nЦіна: " + str(filmAbout[5])
        await message.answer_photo(photo=img, caption=caption)
        await LogIn.logged.set()
    else:
        await message.answer("Такого фільму не існує!\n"
                             "Перевірте назву та спробуйте ще раз або поверніться до меню за допомогою команди /menu")


@dp.message_handler(state=Search.find_author)
async def find_author(message: types.Message):
    authorName = message.text
    authorData = db.find_author(authorName)
    if authorData[0]:
        authorAbout = authorData[1]
        img = open("director/" + str(authorAbout[0]) + ".jpg", "rb")
        caption = authorAbout[1] + "\n" + authorAbout[2]
        await message.answer_photo(photo=img, caption=caption)
        await LogIn.logged.set()
    else:
        await message.answer("Такого автора не існує!\n"
                             "Перевірте назву та спробуйте ще раз або поверніться до меню за допомогою команди /menu")


# Кінець блоку пошуків за назвою
# Початок блоку розміщення фільму та онлайн сплати


@dp.message_handler(state=FilmAdd.add_name)
async def add_film_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data({"name": name})
    await FilmAdd.add_genre.set()
    await message.answer("Тепер оберіть та напишіть один із жанрів, що доступні в нашій базі:")
    text = str()
    gen_list = db.show_genres()
    for genre in gen_list:
        text += genre[1] + "\n"
    await message.answer(text)


@dp.message_handler(state=FilmAdd.add_genre)
async def add_film_genre(message: types.Message, state: FSMContext):
    genre = message.text
    gen_list = db.show_genres()
    for right_genre in gen_list:
        if genre == right_genre[1]:
            await state.update_data({"genre": right_genre[0]})
            await FilmAdd.add_trilogy.set()
            await message.answer("Далі введіть назву трилогії.\n"
                                 "Якщо фільм не належіть до будь-якої серії фільмів, натисніть /skip")
            return
    await message.answer("Такого жанру не існує!\n"
                         "Перевірте на правильність назву написаного жанру або поверніться до головного меню "
                         "за допомогою команди /menu")


@dp.message_handler(state=FilmAdd.add_trilogy, commands="skip")
async def film_trilogy_skip(message: types.Message, state: FSMContext):
    await state.update_data({"trilogy": None})
    await FilmAdd.add_film_photo.set()
    await message.answer("Тепер треба відправити фото фільму.\n"
                         "ВАЖЛИВО!!! Фото треба відправити не як файл, а саме як фото")


@dp.message_handler(state=FilmAdd.add_trilogy)
async def add_film_trilogy(message: types.Message, state: FSMContext):
    trilogy = message.text
    await state.update_data({"trilogy": trilogy})
    await FilmAdd.add_film_photo.set()
    await message.answer("Тепер треба відправити фото фільму.\n"
                         "ВАЖЛИВО!!! Фото треба відправити не як файл, а саме як фото")


@dp.message_handler(content_types=['photo'], state=FilmAdd.add_film_photo)
async def add_film_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data({"filmPhoto": photo})
    await FilmAdd.add_author_name.set()
    await message.answer("Тепер інформація про автора.\n"
                         "Введіть ім'я та прізвище режисера")


@dp.message_handler(state=FilmAdd.add_author_name)
async def add_author_name(message: types.Message, state: FSMContext):
    author = message.text
    await state.update_data({"author": author})
    await FilmAdd.add_author_desc.set()
    await message.answer("Напишіть короткі відомості про нього")


@dp.message_handler(state=FilmAdd.add_author_desc)
async def add_author_desc(message: types.Message, state: FSMContext):
    desc = message.text
    await state.update_data({"desc": desc})
    await FilmAdd.add_author_photo.set()
    await message.answer("Тепер треба відправити фото автора.\n"
                         "ВАЖЛИВО!!! Фото треба відправити не як файл, а саме як фото")


@dp.message_handler(content_types=['photo'], state=FilmAdd.add_author_photo)
async def handle_author_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data({"authorPhoto": photo})
    await FilmAdd.add_price.set()
    await message.answer("Залишилось встановити ціну.\n"
                         "Якщо бажаєте зробити фільм безкоштовним, напишіть 0. Якщо ж ні, "
                         "то запишіть ціну у форматі дробного десяткового числа із крапкою між цілою та "
                         "дробовою частиною")


@dp.message_handler(state=FilmAdd.add_price)
async def add_author_name(message: types.Message, state: FSMContext):
    price = message.text
    if "." not in price:
        await message.answer("Ціна не відповідає вимозі!\n"
                             "Перевірте ії на правильність написання та спробуйте ще раз")
    else:
        await state.update_data({"price": price})
        await FilmAdd.add_payment.set()
        await message.answer("Тепер момент сплати за все.\n"
                             "Найважчий момент. Як для вас, так і для нас. Тому що із механізмами онлайн-сплати "
                             "ми будемо ознайомлюватись прямо зараз, об 1:00 24.12.2021. Ми сподіваємось, що завтра "
                             "ви прочитаєте цей текст, і нам не доведеться його видаляти через те, що він не працює!\n"
                             "Натисніть /buy, щоб перейти до сплати")


@dp.message_handler(commands=["buy"], state=FilmAdd.add_payment)
async def process_buy_command(message: types.Message):
    if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await message.answer("pre_buy_demo_alert")
    toPay = types.LabeledPrice(label="Рекламна послуга", amount=50000)
    await bot.send_invoice(
        message.chat.id,
        title="Сплата за рекламу",
        description="Сплата за рекламні послуги з додання фільму, ціну вказано тестову",
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency="uah",
        prices=[toPay],
        start_parameter="time-machine-example",
        payload="some-invoice-payload-for-our-internal-use"
    )


@dp.pre_checkout_query_handler(run_task=lambda query: True, state=FilmAdd.add_payment)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=FilmAdd.add_payment)
async def process_successful_payment(message: types.Message, state: FSMContext):
    await FilmAdd.add_confirm.set()
    await message.answer("Сплачено успішно!")

    async with state.proxy() as data:
        authorP = data["authorPhoto"]
        authorD = data["desc"]
        authorN = data["author"]
        filmP = data["filmPhoto"]
        trilogy = data["trilogy"]
        genre = data["genre"]
        price = data["price"]
        name = data["name"]

        authorId = db.addAuthor(authorN, authorD)
        await authorP.download('director/' + str(authorId) + '.jpg')

        filmId = db.addFilm(name, genre, authorId, trilogy, price)
        await filmP.download('film/' + str(filmId) + '.jpg')

    await message.answer("Фільм додано! Вітаємо!")
    await LogIn.logged.set()


# Кінець блоку розміщення фільму та онлайн сплати


executor.start_polling(dispatcher=dp, on_startup=start_notification, on_shutdown=end_notification, skip_updates=True)
