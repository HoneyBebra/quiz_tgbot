from quiz_parser import (
    OpenWWWQuestions,
    WWWQuestionsWithChoice,
    OpenTriviadorQuestions,
    TriviadorQuestionsWithChoice
)


def add_open_www_question_to_global_dict(user_id, dict_questions=None):
    if dict_questions is None:
        dict_questions = dict()
    questions_page = ''
    question = ''
    bad_question = True
    while bad_question:
        questions_page = OpenWWWQuestions()
        question = questions_page.get_question()
        if any(keyword in question for keyword in ['Раздаточный материал', 'z-checkdb', 'Блиц', 'Дуплет']):
            continue
        else:
            bad_question = False
    photo_href = questions_page.get_photo_href()
    question_attributes = questions_page.get_question_attributes()
    dict_questions[user_id] = [
        question,
        question_attributes[0],  # right_answer
        question_attributes[1],  # additional_answer
        question_attributes[2],  # comment
        question_attributes[3],  # location_game
        question_attributes[4],  # author
        question_attributes[5],  # source
        photo_href
    ]
    return dict_questions


def forming_www_question_with_choice_data():
    question = ''
    variants = ''
    right_answer = ''
    bad_question = True
    while bad_question:
        question_page = WWWQuestionsWithChoice()
        question = question_page.get_question()
        if question == '' or any(keyword in question for keyword in ('предыдущ', 'вопрос')):
            continue
        variants, right_answer = question_page.get_question_attributes()
        if len(variants) != 4:
            continue
        bad_question = False

    return question, variants, right_answer


def add_open_triviador_question_to_global_dict(user_id, dict_questions=None):
    if dict_questions is None:
        dict_questions = dict()
    questions_page = ''
    question = ''
    bad_question = True
    while bad_question:
        questions_page = OpenTriviadorQuestions()
        question = questions_page.get_question()
        if question == '':
            continue
        bad_question = False
    right_answer = questions_page.get_question_attributes()
    dict_questions[user_id] = [question, right_answer]
    return dict_questions


def forming_triviador_question_with_choice_data():
    question = ''
    variants = ''
    right_answer = ''
    bad_question = True
    while bad_question:
        question_page = TriviadorQuestionsWithChoice()
        question = question_page.get_question()
        variants, right_answer = question_page.get_question_attributes()
        if len(variants) != 4:
            continue
        try:
            variants.index(right_answer)
            bad_question = False
        except ValueError:
            continue
    return question, variants, right_answer


def forming_open_answer_response_message(dict_questions, user_id, right_answer: bool):
    answer_category = {
        True: 'Верный ответ!',
        False: 'Ответ неверен'
    }
    if len(dict_questions[user_id]) == 3:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}'
        return bot_answer

    if len(dict_questions[user_id][3]) >= 1 and len(dict_questions[user_id][2]) >= 1 \
            and len(dict_questions[user_id][6]) >= 1:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}\n\n' + \
                     f'Принимаются ответы: {dict_questions[user_id][2]}\n\n' + \
                     f'Комментарий: {dict_questions[user_id][3]}\n{dict_questions[user_id][6]}'
    elif len(dict_questions[user_id][3]) >= 1 and len(dict_questions[user_id][2]) >= 1:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}\n\n' + \
                     f'Принимаются ответы: {dict_questions[user_id][2]}\n\nКомментарий: {dict_questions[user_id][3]}'
    elif len(dict_questions[user_id][3]) >= 1 and len(dict_questions[user_id][6]) >= 1:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}\n\n' + \
                     f'Комментарий: {dict_questions[user_id][3]}\n{dict_questions[user_id][6]}'
    elif len(dict_questions[user_id][3]) >= 1:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}\n\n' + \
                     f'Комментарий: {dict_questions[user_id][3]}'
    elif len(dict_questions[user_id][2]) >= 1 and len(dict_questions[user_id][6]) >= 1:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}\n\n' + \
                     f'Принимаются ответы: {dict_questions[user_id][2]}\n{dict_questions[user_id][6]}'
    elif len(dict_questions[user_id][2]) >= 1:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}\n\n' + \
                     f'Принимаются ответы: {dict_questions[user_id][2]}'
    elif len(dict_questions[user_id][6]) >= 1:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}\n{dict_questions[user_id][6]}'
    else:
        bot_answer = f'{answer_category[right_answer]}\n\n{dict_questions[user_id][1]}'
    return bot_answer
