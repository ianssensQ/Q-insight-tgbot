import nltk
import re
import spacy
import pymorphy2
import emoji
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from num2words import num2words
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import AutoModel, AutoTokenizer
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from torch.utils.data import DataLoader, TensorDataset

nltk.download('punkt')
nltk.download('stopwords')


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


def classify_text(text):
    data = cleaner.clean_text(text)


m = 'cointegrated/rubert-tiny'
tokenizer = AutoTokenizer.from_pretrained(m)
model = AutoModel.from_pretrained(m)

