import requests
from bs4 import BeautifulSoup
import random


class OpenWWWQuestions:
    def __init__(self):
        self.page = requests.get('https://db.chgk.info/random/types1234/1105442716/limit1').text
        self.soup = BeautifulSoup(self.page, "html.parser")

    def get_question(self):
        random_question = self.soup.find('div', class_='random_question').get_text()
        question = ' '.join(
            random_question[random_question.find('Вопрос 1:') + 10:random_question.find('Ответ:') - 6].split()
        )
        return question

    def get_photo_href(self):
        photo_href = ''
        try:
            photo_href = self.soup.find('div', class_='random_question').find('img')['src']
        except TypeError:
            pass
        return photo_href

    def get_question_attributes(self):
        collapsible_class = self.soup.find('div', class_='collapsible').find_all('p')
        right_answer = ' '.join(collapsible_class[0].get_text()[8:].split())
        author = collapsible_class[-1].text
        if 'Автор' not in author:
            author = 'Неизвестен'
        location_game = self.soup.select_one('.random_question > p').text
        additional_answer = ''
        comment = ''
        source = ''

        if all(keyword in str(collapsible_class) for keyword in ('Зачёт', 'Комментарий')):
            comment = ' '.join(collapsible_class[2].get_text()[14:].split())
            additional_answer = collapsible_class[1].get_text()[8:]
            if 'Незачет' in collapsible_class[1].get_text()[8:]:
                additional_answer = ' '.join(additional_answer[:additional_answer.find('Незачет') + 1].split())
        elif 'Зачёт:' in str(collapsible_class):
            additional_answer = str(collapsible_class[1].get_text()[8:])
            if 'Незачет' in additional_answer:
                additional_answer = ' '.join(additional_answer[:additional_answer.find('Незачет') + 1].split())
        elif 'Комментарий:' in str(collapsible_class):
            comment = ' '.join(collapsible_class[1].get_text()[14:].split())
        if 'Источник(и):' in str(collapsible_class):
            source = collapsible_class[-2].text.replace('    ', '')
            if 'Источник(и):' not in source:
                source = ''

        return right_answer, additional_answer, comment, location_game, author, source


class WWWQuestionsWithChoice:
    def __init__(self):
        self.page = requests.get('https://db.chgk.info/random/types6/900533565/limit1').text
        self.soup = BeautifulSoup(self.page, "html.parser")

    def get_question(self):
        random_question = self.soup.find('div', class_='random_question').text
        question = ''
        if all(keyword in random_question for keyword in ('1)', '2)', '3)', '4)')):
            question = random_question[random_question.find('Вопрос 1:') + 10:random_question.find('1)') - 6]
        elif all(keyword in random_question for keyword in ('а)', 'б)', 'в)', 'г)')):
            question = random_question[random_question.find('Вопрос 1:') + 10:random_question.find('а)') - 6]
        elif all(keyword in random_question for keyword in ('a)', 'b)', 'c)', 'd)')):
            question = random_question[random_question.find('Вопрос 1:') + 10:random_question.find('a)') - 6]
        question = ' '.join(question.split())
        return question

    def get_question_attributes(self):
        right_answer = self.soup.find('div', class_='collapsible').find_all('p')
        right_answer = right_answer[0].text[1:]
        right_answer = right_answer[right_answer.find(') ') + 2:]

        random_question = self.soup.find('div', class_='random_question').text
        variants = []
        if all(keyword in random_question for keyword in ('1)', '2)', '3)', '4)')):
            answer1 = random_question[random_question.find('1)') + 3:random_question.find('2)') - 6]
            answer2 = random_question[random_question.find('2)') + 3:random_question.find('3)') - 6]
            answer3 = random_question[random_question.find('3)') + 3:random_question.find('4)') - 6]
            answer4 = random_question[random_question.find('4)') + 3:random_question.find('...') - 2]
            variants = [answer1, answer2, answer3, answer4]
        elif all(keyword in random_question for keyword in ('а)', 'б)', 'в)', 'г)')):
            answer1 = random_question[random_question.find('а)') + 3:random_question.find('б)') - 6]
            answer2 = random_question[random_question.find('б)') + 3:random_question.find('в)') - 6]
            answer3 = random_question[random_question.find('в)') + 3:random_question.find('г)') - 6]
            answer4 = random_question[random_question.find('г)') + 3:random_question.find('...') - 2]
            variants = [answer1, answer2, answer3, answer4]
        elif all(keyword in random_question for keyword in ('a)', 'b)', 'c)', 'd)')):
            answer1 = random_question[random_question.find('a)') + 3:random_question.find('b)') - 6]
            answer2 = random_question[random_question.find('b)') + 3:random_question.find('c)') - 6]
            answer3 = random_question[random_question.find('c)') + 3:random_question.find('d)') - 6]
            answer4 = random_question[random_question.find('d)') + 3:random_question.find('...') - 2]
            variants = [answer1, answer2, answer3, answer4]

        return variants, right_answer


class OpenTriviadorQuestions:
    def __init__(self):
        random_page = requests.get(f'https://topasnew24.com/voprosi/page/{random.randint(1, 157)}/')
        random_page_soup = BeautifulSoup(random_page.text, 'html.parser')
        questions_list = random_page_soup.select('.img-short-title > a')
        random_question_url = questions_list[random.randint(0, len(questions_list) - 1)]['href']
        self.page = requests.get(random_question_url)
        self.soup = BeautifulSoup(self.page.text, 'html.parser')

    def get_question(self):
        random_question = self.soup.select_one('.full-news-short').text
        question = ' '.join(random_question[2:random_question.find('?') + 1].split())
        if question == '':
            question = ' '.join(random_question[2:random_question.find(':') + 1].split())
        if question == '':
            question = ' '.join(random_question[2:random_question.find('.') + 1].split())
        return question

    def get_question_attributes(self):
        random_question = self.soup.select_one('.full-news-short').text
        right_answer = int(random_question[random_question.find('ответ:') + 7:-10])
        return right_answer


class TriviadorQuestionsWithChoice(OpenTriviadorQuestions):
    def get_question(self):
        random_question = self.soup.select_one('.full-news-short').text
        question = ' '.join(random_question[2:random_question.find('?') + 1].split())
        if len(question) == 0:
            question = ' '.join(random_question[2:random_question.find(':') + 1].split())
        return question

    def get_question_attributes(self):
        random_question = self.soup.select_one('.full-news-short').text
        question = ' '.join(random_question[2:random_question.find('?') + 1].split())

        if len(question) == 0:
            attributes = random_question[random_question.find(':') + 1:]
        else:
            attributes = random_question[random_question.find('?') + 1:]
        attributes = attributes[:attributes.find('.')]
        if attributes[0] == ' ':
            attributes = attributes[1:]

        variants = attributes.split(';')
        if len(variants) != 4:
            variants = attributes.split(',')

        right_answer = random_question[random_question.find('ответ:') + 7:-10]
        return variants, right_answer
