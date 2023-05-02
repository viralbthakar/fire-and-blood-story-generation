import string
import pandas as pd
from collections import defaultdict

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class ParagraphCleaner(object):
    def __init__(self, paragraphs_dict):
        self.paragraphs_dict = paragraphs_dict

    def remove_punctuation(self, text):
        punctuation_to_remove = string.punctuation.replace(".", "")
        for punctuation in punctuation_to_remove:
            text = text.replace(punctuation, ' ')
        return text

    def lowercase(self, text):
        text = text.lower()
        return text

    def remove_numbers(self, text):
        text = ''.join([i for i in text if not i.isdigit()])
        return text

    def tokenize_text(self, text):
        tokenized = word_tokenize(text)
        return tokenized

    def remove_stopwords(self, text, language='english'):
        stop_words = set(stopwords.words(language))
        tokenized = word_tokenize(text)
        text = [
            word for word in tokenized if not word in stop_words]
        return text

    def lemmatize(self, text):
        lemmatizer = WordNetLemmatizer()  # Instantiate lemmatizer
        text = [lemmatizer.lemmatize(word) for word in text]  # Lemmatize
        text = " ".join(text)
        return text

    def clean_paragraphs(self):
        cleaned_dict = {}
        for key, value in self.paragraphs_dict.items():
            text = self.remove_punctuation(value)
            text = self.lowercase(text)
            # text = self.remove_stopwords(text)
            # text = self.lemmatize(text)

            cleaned_dict[key] = text
        return cleaned_dict