def check_www_user_answer(dict_questions, user_id):
    if len(dict_questions[user_id][-1]) == 1 and len(dict_questions[user_id][1]) != 1:
        return False
    else:
        for word in dict_questions[user_id][-1].lower().split():
            if len(word) > 1:
                if word in dict_questions[user_id][1].lower() or \
                        word in dict_questions[user_id][2].lower():
                    return True
        return False


def check_triviador_user_answer(dict_questions, user_id):
    try:
        if (dict_questions[user_id][1] * 0.99) < dict_questions[user_id][2] < (dict_questions[user_id][1] * 1.01):
            return True
        else:
            return False
    except ValueError:
        return False
