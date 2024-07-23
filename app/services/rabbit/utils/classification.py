import nltk
import re
import spacy
import pymorphy2
import emoji
import torch
import joblib
import os
import warnings

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from num2words import num2words
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import AutoModel, AutoTokenizer
from decouple import config

warnings.filterwarnings("ignore")


model_path = config('CLASSIFICATION_MODEL')
classifier = joblib.load(model_path)

"""nltk.download('punkt')
nltk.download('stopwords')"""


class Cleaner:
    def __init__(self):
        self.model_lemmatizer = pymorphy2.MorphAnalyzer()
        self.nlp = spacy.load("ru_core_news_sm")

    def clean_text(self, input_text):
        clean_text = re.sub('<[^<]+?>', '', input_text)
        clean_text = re.sub(r'http\S+', '', clean_text)
        clean_text = self.emojis_words(clean_text)
        clean_text = clean_text.lower()
        clean_text = re.sub('\s+', ' ', clean_text)
        clean_text = re.sub('[^A-Za-zА-Яа-я0-9\s]', '', clean_text)
        clean_text = self.replace_numbers_with_words(clean_text)
        stop_words_ru = set(stopwords.words('russian'))
        stop_words_en = set(ENGLISH_STOP_WORDS)
        all_stop_words = stop_words_en.union(stop_words_ru)
        tokens = word_tokenize(clean_text)
        tokens = [token for token in tokens if token not in all_stop_words]
        clean_text = ' '.join(tokens)
        clean_text = re.sub(r'[^\w\s]', '', clean_text)

        return clean_text

    @staticmethod
    def replace_numbers_with_words(text):
        number_pattern = r'\b\d+\b'

        def replace(match):
            number = int(match.group(0))
            return num2words(number, lang='ru')

        return re.sub(number_pattern, replace, text)

    @staticmethod
    def emojis_words(text):
        clean_text = emoji.demojize(text, delimiters=(" ", " "))
        clean_text = clean_text.replace(":", "").replace("_", " ")
        return clean_text


cleaner = Cleaner()
m = 'cointegrated/rubert-tiny'
tokenizer = AutoTokenizer.from_pretrained(m)
model = AutoModel.from_pretrained(m)


def get_embeddings(texts):
    tokens = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=256)
    input_ids = tokens['input_ids']
    attention_mask = tokens['attention_mask']

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

    return embeddings


def classify_text(text):
    data = cleaner.clean_text(text)
    new_embeddings = get_embeddings(data)
    prediction = classifier.predict(new_embeddings)

    return prediction


if __name__ == '__main__':
    print(classify_text('Реклама, советую плотно прочитать!'))
    print(classify_text('Какие крутые новости'))
    print(classify_text('Екатерина Мизулина осудила Асхаба Тамаева! '
              'На этот раз в руки главы «Лиги Безопасного Интернета» попала история о том,'
              'как Тамаев слил в сеть личные данные своего разоблачителя и в итоге заставил '
              'того извиняться. Екатерина выпустила большую серию постов в своем тг-канале, '
              'она заявила, что Асхаб не уважает ислам, а также несколько раз назвала блогера '
              '«скамером». Разборки дошли до того, что Мизулиной стали присылать угрозы в личные '
              'сообщения…'))
