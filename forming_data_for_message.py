from quiz_parser import OpenWWWQuestions, OpenTriviadorQuestions


def add_open_www_question_to_global_dict(user_id, dict_questions=None):
    if dict_questions is None:
        dict_questions = dict()
    open_www_questions_page = ''
    open_www_question = ''
    bad_question = True
    while bad_question:
        open_www_questions_page = OpenWWWQuestions()
        open_www_question = open_www_questions_page.get_question()
        if any(keyword in open_www_question for keyword in ['Раздаточный материал', 'z-checkdb', 'Блиц', 'Дуплет']):
            continue
        else:
            bad_question = False
    photo_href = open_www_questions_page.get_photo_href()
    question_attributes = open_www_questions_page.get_question_attributes()
    dict_questions[user_id] = [
        open_www_question,
        question_attributes[0],  # right_answer
        question_attributes[1],  # additional_answer
        question_attributes[2],  # comment
        question_attributes[3],  # location_game
        question_attributes[4],  # author
        question_attributes[5],  # source
        photo_href
    ]
    return dict_questions


def add_open_triviador_question_to_global_dict(user_id, dict_questions=None):
    if dict_questions is None:
        dict_questions = dict()
    open_triviador_questions_page = OpenTriviadorQuestions()
    open_triviador_question = open_triviador_questions_page.get_question()
    right_answer = open_triviador_questions_page.get_question_attributes()
    dict_questions[user_id] = [open_triviador_question, right_answer]
    return dict_questions
