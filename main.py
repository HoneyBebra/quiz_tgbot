import os
import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
from bs4 import BeautifulSoup as BS
import random
from dotenv import load_dotenv

from DB_model import WWWStatistics

logging.basicConfig(level=logging.INFO)

load_dotenv()

bot = Bot(token=os.environ.get('TOKEN'))
# PROXY_URL = 'http://proxy.server:3128'
# bot = Bot(token=os.environ.get('TOKEN'), proxy=PROXY_URL)
dp = Dispatcher(bot)

global dict_questions
global quiz

user_statistics_db = WWWStatistics()
user_statistics_db.create_table_fi_not_exists()


@dp.message_handler(commands=["start", 'help'])
async def cmd_start_help(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Открытый вопрос"),
                      types.KeyboardButton(text="Вопрос с вариантами"),
                      types.KeyboardButton(text="Рандом"),
                      types.KeyboardButton(text="Статистика"))
    await message.answer('Привет, это квиз-бот. Ты можешь выбрать вопросы с открытым ответом (из игр ЧГК), '
                         'вопросы с вариантами ответов (из игр Тривиадор и Эрудитка) '
                         'или рандомные вопросы. Бот черпает вдохновение из баз:\n'
                         'https://db.chgk.info/\n'
                         'https://topasnew24.com/', reply_markup=poll_keyboard)


@dp.message_handler(lambda message: str(message.text).lower() == "открытый вопрос")
async def game_open_questions(message: types.Message):
    global dict_questions

    async def open_WWW_ques():
        global dict_questions

        page = requests.get('https://db.chgk.info/random/types1234/1105442716/limit1')
        page_open_ques = str(page.text)
        soup = BS(page_open_ques, "html.parser")
        random_ques = str(soup.find('div', class_='random_question').get_text())

        flag = 0

        # Removing inappropriate questions
        while flag != 1:
            if 'Раздаточный материал' in random_ques or 'z-checkdb' in random_ques or 'Блиц' in random_ques or \
                    'Дуплет' in random_ques:
                page = requests.get('https://db.chgk.info/random/1329656998/limit1')
                page_open_ques = str(page.text)
                soup = BS(page_open_ques, "html.parser")
                random_ques = str(soup.find('div', class_='random_question').get_text())
            else:
                flag = 1

        # Removing inappropriate hyphens
        question = ' '.join(random_ques[random_ques.find('Вопрос 1:') + 10:random_ques.find('Ответ:') - 6].split())

        photo_href = ''
        try:
            photo_href = soup.find('div', class_='random_question').find('img')['src']
        except TypeError:
            pass

        # CAD - list [comment, answer, additional answer, author, source]
        CAD = soup.find('div', class_='collapsible').find_all('p')
        answer = ' '.join(CAD[0].get_text()[8:].split())
        real_game = soup.select_one('.random_question > p').text
        author = CAD[-1].text
        add_answer = ''
        comment = ''
        if 'Зачёт:' in str(CAD) and 'Комментарий:' in str(CAD):
            add_ans = str(CAD[1].get_text()[8:])
            if 'Незачет' in add_ans:
                add_answer = ' '.join(add_ans[:add_ans.find('Незачет') + 1].split())
            else:
                add_answer = add_ans
            comment = ' '.join(CAD[2].get_text()[14:].split())
        elif 'Зачёт:' in str(CAD):
            add_ans = str(CAD[1].get_text()[8:])
            if 'Незачет' in add_ans:
                add_answer = ' '.join(add_ans[:add_ans.find('Незачет') + 1].split())
            else:
                add_answer = add_ans
        elif 'Комментарий:' in str(CAD):
            comment = ' '.join(CAD[1].get_text()[14:].split())

        if 'Источник(и):' in str(CAD):
            # Removing unnecessary margins
            source = CAD[-2].text.replace('    ', '')
        else:
            source = ''

        if 'Источник(и):' not in source:
            source = ''
        else:
            pass

        try:
            dict_questions[message.from_user.id] = [question, answer, add_answer, comment, real_game, author, source,
                                                    photo_href]
        except NameError:
            dict_questions = {message.from_user.id: [question, answer, add_answer, comment, real_game, author, source,
                                                     photo_href]}

        if 'Автор' in dict_questions[message.from_user.id][5]:
            await message.answer(
                dict_questions[message.from_user.id][4] + '\n\n' + dict_questions[message.from_user.id][0] + '\n' +
                dict_questions[message.from_user.id][5], reply_markup=types.ReplyKeyboardRemove())

            if len(dict_questions[message.from_user.id][7]) > 0:
                await bot.send_photo(chat_id=message.chat.id, photo=dict_questions[message.from_user.id][7])
            else:
                pass

            await message.answer('Итак, твой ответ...')
        else:
            await message.answer(
                dict_questions[message.from_user.id][4] + '\n\n' + dict_questions[message.from_user.id][0],
                reply_markup=types.ReplyKeyboardRemove())

            if len(dict_questions[message.from_user.id][7]) > 0:
                await bot.send_photo(chat_id=message.chat.id, photo=photo_href)
            else:
                pass

            await message.answer('Итак, твой ответ...')

    # try to open triviador question
    page_triv_open = requests.get(f'https://topasnew24.com/voprosi/page/{random.randint(1, 131)}/')
    soup_triv_open = BS(page_triv_open.text, 'html.parser')

    Ques_triviador_open = soup_triv_open.select('.img-short-title > a')

    url_Q_open = Ques_triviador_open[random.randint(0, len(Ques_triviador_open) - 1)]['href']

    page_Q_open = requests.get(url_Q_open)
    soup_Q = BS(page_Q_open.text, 'html.parser')
    use_text_open = soup_Q.select_one('.full-news-short').text

    QUES_T_open = use_text_open[2:use_text_open.find('?') + 1]
    try:
        ANSW_T = int(use_text_open[use_text_open.find('ответ:') + 7:-10])

        try:
            dict_questions[message.from_user.id] = [QUES_T_open, ANSW_T]
        except NameError:
            dict_questions = {message.from_user.id: [QUES_T_open, ANSW_T]}

        await message.answer('Тривиадор:\n' + dict_questions[message.from_user.id][0] + '\n\nДопускается ошибка на 5%',
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer('Итак, твой ответ...')

    except ValueError:
        await open_WWW_ques()


@dp.message_handler(lambda message: str(message.text).lower() == "вопрос с вариантами")
async def game_variants(message: types.Message):
    global quiz

    QUES_T = ''
    ANSW_T = ''

    async def game_TRIVIADOR():
        global quiz

        page_triv = requests.get(f'https://topasnew24.com/voprosi/page/{random.randint(1, 131)}/')
        soup_triv = BS(page_triv.text, 'html.parser')

        Ques_triviador = soup_triv.select('.img-short-title > a')

        flag_T = 0
        while flag_T == 0:
            url_Q = Ques_triviador[random.randint(0, len(Ques_triviador) - 1)]['href']

            page_Q = requests.get(url_Q)
            soup_Q = BS(page_Q.text, 'html.parser')
            use_text = soup_Q.select_one('.full-news-short').text

            # Removing inappropriate hyphens
            QUES_T = ' '.join(use_text[2:use_text.find('?') + 1].split())

            # index 0 means that variants are not yet ready to be sent
            if len(QUES_T) == 0:
                QUES_T = use_text[2:use_text.find(':') + 1]
                VAR_0 = use_text[use_text.find(':') + 1:]
                VAR_0 = VAR_0[:VAR_0.find('.')]
                if VAR_0[0] == ' ':
                    VAR_0 = VAR_0[1:]
            else:
                VAR_0 = use_text[use_text.find('?') + 1:]
                VAR_0 = VAR_0[:VAR_0.find('.')]
                if VAR_0[0] == ' ':
                    VAR_0 = VAR_0[1:]
            VAR_T = VAR_0.split(';')
            if len(VAR_T) != 4:
                VAR_T = VAR_0.split(',')

            if len(VAR_T) != 4:
                continue
            else:
                ANSW_T = use_text[use_text.find('ответ:') + 7:-10]

            try:
                VAR_T.index(ANSW_T)
                flag_T = 1
            except ValueError:
                continue

            quiz = await bot.send_poll(chat_id=message.chat.id,
                                       question=f'Тривиадор:\n{QUES_T}',
                                       is_anonymous=False, options=VAR_T, type="quiz",
                                       correct_option_id=VAR_T.index(ANSW_T))

    if random.randint(1, 2) == 1:
        try:
            flag_ERUDITKA = 0

            answer1 = ''
            answer2 = ''
            answer3 = ''
            answer4 = ''

            while flag_ERUDITKA != 1:

                page_E = requests.get('https://db.chgk.info/random/types6/900533565/limit1')
                soup_E = BS(page_E.text, 'html.parser')

                ACA = soup_E.find('div', class_='collapsible').find_all('p')
                answer_right0 = ACA[0].text[1:]
                ANSW_T = answer_right0[answer_right0.find(') ') + 2:]
                QUE_text = soup_E.find('div', class_='random_question').text

                if 'предыдущ' in QUE_text and 'вопрос' in QUE_text:
                    continue
                else:
                    pass

                if '1)' in QUE_text and '2)' in QUE_text and '3)' in QUE_text and '4)' in QUE_text:
                    QUES_T = QUE_text[QUE_text.find('Вопрос 1:') + 10:QUE_text.find('1)') - 6]
                    answer1 = QUE_text[QUE_text.find('1)') + 3:QUE_text.find('2)') - 6]
                    answer2 = QUE_text[QUE_text.find('2)') + 3:QUE_text.find('3)') - 6]
                    answer3 = QUE_text[QUE_text.find('3)') + 3:QUE_text.find('4)') - 6]
                    answer4 = QUE_text[QUE_text.find('4)') + 3:QUE_text.find('...') - 2]
                    flag_ERUDITKA = 1
                elif 'а)' in QUE_text and 'б)' in QUE_text and 'в)' in QUE_text and 'г)' in QUE_text:
                    QUES_T = QUE_text[QUE_text.find('Вопрос 1:') + 10:QUE_text.find('а)') - 6]
                    answer1 = QUE_text[QUE_text.find('а)') + 3:QUE_text.find('б)') - 6]
                    answer2 = QUE_text[QUE_text.find('б)') + 3:QUE_text.find('в)') - 6]
                    answer3 = QUE_text[QUE_text.find('в)') + 3:QUE_text.find('г)') - 6]
                    answer4 = QUE_text[QUE_text.find('г)') + 3:QUE_text.find('...') - 2]
                    flag_ERUDITKA = 1
                elif 'a)' in QUE_text and 'b)' in QUE_text and 'c)' in QUE_text and 'd)' in QUE_text:
                    QUES_T = QUE_text[QUE_text.find('Вопрос 1:') + 10:QUE_text.find('a)') - 6]
                    answer1 = QUE_text[QUE_text.find('a)') + 3:QUE_text.find('b)') - 6]
                    answer2 = QUE_text[QUE_text.find('b)') + 3:QUE_text.find('c)') - 6]
                    answer3 = QUE_text[QUE_text.find('c)') + 3:QUE_text.find('d)') - 6]
                    answer4 = QUE_text[QUE_text.find('d)') + 3:QUE_text.find('...') - 2]
                    flag_ERUDITKA = 1
                else:
                    continue

            QUES_T = ' '.join(QUES_T.split())  # Removing inappropriate hyphens
            VAR_T = [answer1, answer2, answer3, answer4]

            quiz = await bot.send_poll(chat_id=message.chat.id,
                                       question=f'Эрудитка:\n{QUES_T}',
                                       is_anonymous=False, options=VAR_T, type="quiz",
                                       correct_option_id=VAR_T.index(ANSW_T))

        except:  # Any mistake transfers to the triviador
            await game_TRIVIADOR()
    else:
        await game_TRIVIADOR()


@dp.poll_answer_handler()
async def statistic_poll(quiz_answer: types.PollAnswer):
    global quiz
    if quiz.poll.correct_option_id == quiz_answer["option_ids"][0]:
        right_answer = True
    else:
        right_answer = True
    user_statistics_db.user_statistics_update(user_id=quiz_answer["user"]["id"], right_answer=right_answer)


@dp.message_handler(lambda message: str(message.text).lower() == "рандом")
async def game_random(message: types.Message):
    if random.randint(1, 2) == 1:
        await game_variants(message)
    else:
        await game_open_questions(message)


@dp.message_handler(lambda message: str(message.text).lower() == "статистика")
async def statistics(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Открытый вопрос"),
                      types.KeyboardButton(text="Вопрос с вариантами"),
                      types.KeyboardButton(text="Рандом"),
                      types.KeyboardButton(text="Статистика"))

    user_statistics = user_statistics_db.get_user_statistics(message.from_user.id)

    if user_statistics[0][0] is None:
        await message.answer(f'Очки телезрителей: 0\n'
                             f'Очки знатоков: 0', reply_markup=poll_keyboard)
    elif str(user_statistics[0][0]) == '0':
        await message.answer(f'Очки телезрителей: {user_statistics[0][1]}\n'
                             f'Очки знатоков: 0\n'
                             f'Процент верных ответов: 0', reply_markup=poll_keyboard)
    elif str(user_statistics[0][1]) == '0':
        await message.answer(f'Очки телезрителей: 0\n'
                             f'Очки знатоков: {user_statistics[0][0]}\n', reply_markup=poll_keyboard)
    else:
        await message.answer(f'Очки телезрителей: {user_statistics[0][1]}\n'
                             f'Очки знатоков: {user_statistics[0][0]}\n'
                             f'Процент верных ответов: '
                             f'{((user_statistics[0][0] / (user_statistics[0][0] + user_statistics[0][1])) * 100):.2f}'
                             f'%', reply_markup=poll_keyboard)


@dp.message_handler(lambda message: str(message.text).lower() == "volkodav3121")
async def easter_egg(message: types.Message):
    with open('local_data/egg.jpg', 'rb') as photo:
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption='Чит-код активирован')


@dp.message_handler()
async def func_answer_WWW(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Открытый вопрос"),
                      types.KeyboardButton(text="Вопрос с вариантами"),
                      types.KeyboardButton(text="Рандом"),
                      types.KeyboardButton(text="Статистика"))
    global dict_questions

    async def right_answer():

        user_statistics_db.user_statistics_update(user_id=message.from_user.id, right_answer=True)

        # message answer
        if len(dict_questions[message.from_user.id][3]) >= 1 and len(dict_questions[message.from_user.id][2]) >= 1 \
                and len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Верный ответ!\n\n{dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}\n'
                                 f'{dict_questions[message.from_user.id][6]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][3]) >= 1 and len(dict_questions[message.from_user.id][2]) >= 1:
            await message.answer(f'Верный ответ!\n\n{dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][3]) >= 1 and len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Верный ответ!\n\n{dict_questions[message.from_user.id][1]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}\n'
                                 f'{dict_questions[message.from_user.id][6]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][3]) >= 1:
            await message.answer(f'Верный ответ!\n\n{dict_questions[message.from_user.id][1]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][2]) >= 1 and len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Верный ответ!\n\n{dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}\n'
                                 f'{dict_questions[message.from_user.id][6]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][2]) >= 1:
            await message.answer(f'Верный ответ!\n\n{dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}',
                                 reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Верный ответ!\n\n'
                                 f'{dict_questions[message.from_user.id][1]}\n'
                                 f'{dict_questions[message.from_user.id][6]}', reply_markup=poll_keyboard)

        else:
            await message.answer(f'Верный ответ!\n\n'
                                 f'{dict_questions[message.from_user.id][1]}',
                                 reply_markup=poll_keyboard)

    async def wrong_answer():

        user_statistics_db.user_statistics_update(user_id=message.from_user.id, right_answer=False)

        # message answer
        if len(dict_questions[message.from_user.id][3]) >= 1 and len(dict_questions[message.from_user.id][2]) >= 1 \
                and len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}\n'
                                 f'{dict_questions[message.from_user.id][6]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][3]) >= 1 and len(dict_questions[message.from_user.id][2]) >= 1:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][3]) >= 1 and len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}\n'
                                 f'{dict_questions[message.from_user.id][6]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][3]) >= 1:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}\n\n'
                                 f'Комментарий: {dict_questions[message.from_user.id][3]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][2]) >= 1 and len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}\n'
                                 f'{dict_questions[message.from_user.id][6]}', reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][2]) >= 1:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}\n\n'
                                 f'Принимаются ответы: {dict_questions[message.from_user.id][2]}',
                                 reply_markup=poll_keyboard)

        elif len(dict_questions[message.from_user.id][6]) >= 1:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}\n'
                                 f'{dict_questions[message.from_user.id][6]}',
                                 reply_markup=poll_keyboard)

        else:
            await message.answer(f'Ответ неверен\n\n'
                                 f'Верный ответ: {dict_questions[message.from_user.id][1]}',
                                 reply_markup=poll_keyboard)

    # response processing
    # IF received a non-command message, no question was asked (that is, it is not an answer to the question)
    try:
        # IF received a non-command message, no question was asked (that is, it is not an answer to the question)
        if message.from_user.id in dict_questions:

            # WWW responses
            if len(dict_questions[message.from_user.id]) > 2:
                dict_questions[message.from_user.id].append(str(message.text))
                if len(dict_questions[message.from_user.id][-1]) == 1 and len(
                        dict_questions[message.from_user.id][1]) != 1:
                    await wrong_answer()

                    dict_questions.pop(message.from_user.id)
                else:
                    flag_2 = 0
                    for word in dict_questions[message.from_user.id][-1].lower().split():
                        if len(word) > 1:
                            if word in dict_questions[message.from_user.id][1].lower() or word in \
                                    dict_questions[message.from_user.id][2].lower():
                                await right_answer()

                                flag_2 = 1
                                dict_questions.pop(message.from_user.id)
                                break
                        else:
                            continue

                    if flag_2 == 0:
                        await wrong_answer()

                        dict_questions.pop(message.from_user.id)

            # Triviador responses
            else:
                try:
                    dict_questions[message.from_user.id].append(int(message.text))
                    if (dict_questions[message.from_user.id][1] * 0.95) < dict_questions[message.from_user.id][2] < \
                            (dict_questions[message.from_user.id][1] * 1.05):
                        await message.answer(f'Верный ответ!\n\n'
                                             f'{dict_questions[message.from_user.id][1]}',
                                             reply_markup=poll_keyboard)

                        user_statistics_db.user_statistics_update(user_id=message.from_user.id, right_answer=True)

                        dict_questions.pop(message.from_user.id)

                    else:
                        await message.answer(f'Ответ неверен\n\n'
                                             f'Верный ответ: {dict_questions[message.from_user.id][1]}',
                                             reply_markup=poll_keyboard)

                        user_statistics_db.user_statistics_update(user_id=message.from_user.id, right_answer=False)

                        dict_questions.pop(message.from_user.id)

                except ValueError:
                    await message.answer(f'Ответ неверен\n\n'
                                         f'Верный ответ: {dict_questions[message.from_user.id][1]}',
                                         reply_markup=poll_keyboard)

                    await user_statistics_db.user_statistics_update(user_id=message.from_user.id, right_answer=False)

                    dict_questions.pop(message.from_user.id)

        else:
            await message.answer('Выбери, в какие вопросы ты хочешь играть', reply_markup=poll_keyboard)
    except NameError:
        await message.answer('Выбери, в какие вопросы ты хочешь играть', reply_markup=poll_keyboard)


# RUN
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)