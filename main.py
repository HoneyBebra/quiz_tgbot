import os
import logging
from aiogram import Bot, Dispatcher, executor, types
import random
from dotenv import load_dotenv

from DB_model import WWWStatistics
from forming_data_for_message import (
    add_open_www_question_to_global_dict,
    forming_www_question_with_choice_data,
    add_open_triviador_question_to_global_dict,
    forming_triviador_question_with_choice_data
)

logging.basicConfig(level=logging.INFO)

load_dotenv()

bot = Bot(token=os.environ.get('TOKEN'))
# PROXY_URL = 'http://proxy.server:3128'
# bot = Bot(token=os.environ.get('TOKEN'), proxy=PROXY_URL)
dp = Dispatcher(bot)

global dict_questions
# For WWW open question:
# dict_questions = {
# user_id: [open_question, right_answer, additional_answer, comment, location_game, author, source, photo_href]
# }
# For triviador open question:
# dict_questions = {
# user_id: [open_triviador_question, right_answer]
# }
global quiz  # aiogram quiz

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

    try:
        try:
            dict_questions = add_open_triviador_question_to_global_dict(
                user_id=message.from_user.id,
                dict_questions=dict_questions
            )
        except NameError:
            dict_questions = add_open_triviador_question_to_global_dict(
                user_id=message.from_user.id
            )
        await message.answer(
            'Тривиадор:\n' +
            dict_questions[message.from_user.id][0] + '\n\n' +
            'Допускается ошибка на 1%',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer('Итак, твой ответ...')
    except ValueError:
        try:
            dict_questions = add_open_www_question_to_global_dict(
                user_id=message.from_user.id,
                dict_questions=dict_questions
            )
        except NameError:
            dict_questions = add_open_www_question_to_global_dict(
                user_id=message.from_user.id
            )
        await message.answer(
            str(dict_questions[message.from_user.id][4]) + '\n\n' +
            str(dict_questions[message.from_user.id][0]) + '\n' +
            str(dict_questions[message.from_user.id][5]),
            reply_markup=types.ReplyKeyboardRemove()
        )
        if len(dict_questions[message.from_user.id][7]) > 0:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=dict_questions[message.from_user.id][7]
            )
        await message.answer('Итак, твой ответ...')


@dp.message_handler(lambda message: str(message.text).lower() == "вопрос с вариантами")
async def game_variants(message: types.Message):
    global quiz

    if random.randint(1, 2) == 1:
        try:
            question, variants, right_answer = forming_www_question_with_choice_data()
            quiz = await bot.send_poll(chat_id=message.chat.id,
                                       question=f'Эрудитка:\n{question}',
                                       is_anonymous=False, options=variants, type="quiz",
                                       correct_option_id=variants.index(right_answer))

        except:
            question, variants, right_answer = forming_triviador_question_with_choice_data()
            quiz = await bot.send_poll(chat_id=message.chat.id,
                                       question=f'Тривиадор:\n{question}',
                                       is_anonymous=False,options=variants, type="quiz",
                                       correct_option_id=variants.index(right_answer)
                                       )
    else:
        question, variants, right_answer = forming_triviador_question_with_choice_data()
        quiz = await bot.send_poll(chat_id=message.chat.id,
                                   question=f'Тривиадор:\n{question}',
                                   is_anonymous=False, options=variants, type="quiz",
                                   correct_option_id=variants.index(right_answer)
                                   )


@dp.poll_answer_handler()
async def statistic_poll(quiz_answer: types.PollAnswer):
    global quiz
    if quiz.poll.correct_option_id == quiz_answer["option_ids"][0]:
        right_answer = True
    else:
        right_answer = False
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
                    if (dict_questions[message.from_user.id][1] * 0.99) < dict_questions[message.from_user.id][2] < \
                            (dict_questions[message.from_user.id][1] * 1.01):
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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
