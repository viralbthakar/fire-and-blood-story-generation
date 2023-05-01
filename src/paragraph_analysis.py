import os
import numpy as np
import pandas as pd
import seaborn as sns
from heapq import nlargest
from collections import Counter
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from nltk.util import ngrams
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

from utils import plot_box_plot_hist_plot, plot_count_plot, styled_print


class ParagraphAnalysis(object):
    def __init__(self, paragraphs_dict, out_dir):
        self.paragraphs_dict = paragraphs_dict
        self.paragraphs_df = pd.DataFrame(
            paragraphs_dict.items(), columns=["id", "paragraphs"])
        self.out_dir = out_dir
        self.add_all_key_features()
        self.words_counts = len(self.raw_corpus)

    def add_all_key_features(self):
        self.tokenize_sentences()
        self.tokenize_words()
        self.create_vocabulary()
        self.add_paragraph_chars_count()
        self.add_paragraph_words_count()
        self.add_paragraph_avg_word_length()

    def tokenize_sentences(self):
        self.paragraphs_df["sentences"] = self.paragraphs_df["paragraphs"].apply(
            sent_tokenize)

    def tokenize_words(self):
        self.paragraphs_df["words"] = self.paragraphs_df["paragraphs"].apply(
            word_tokenize)

    def create_vocabulary(self):
        list_of_words = self.paragraphs_df["words"]
        self.raw_corpus = [
            word for sentence in list_of_words for word in sentence]

    def add_paragraph_chars_count(self):
        self.paragraphs_df["paragraph_chars_count"] = self.paragraphs_df["paragraphs"].str.len(
        )

    def add_paragraph_words_count(self):
        self.paragraphs_df["paragraph_words_count"] = self.paragraphs_df["words"].map(
            lambda x: len(x))

    def add_paragraph_avg_word_length(self):
        self.paragraphs_df["paragraph_avg_word_len"] = self.paragraphs_df["words"].apply(
            lambda x: [len(i) for i in x]).map(lambda x: np.mean(x))

    def characters_per_paragraph_histogram(self, figsize=(4, 4), dpi=300, save_flag=False):
        plot_box_plot_hist_plot(
            self.paragraphs_df,
            column="paragraph_chars_count",
            title="Characters per Paragraph Distribution Plot",
            figsize=figsize,
            dpi=dpi,
            save_flag=save_flag,
            file_path=os.path.join(
                self.out_dir, "paragraph-length-distribution.png")
        )

    def words_per_paragraph_histogram(self, figsize=(4, 4), dpi=300, save_flag=False):
        plot_box_plot_hist_plot(
            self.paragraphs_df,
            column="paragraph_words_count",
            title="Words per Paragraph Distribution Plot",
            figsize=figsize,
            dpi=dpi,
            save_flag=save_flag,
            file_path=os.path.join(
                self.out_dir, "paragraph-length-distribution.png")
        )

    def avg_word_len_per_paragraph_histogram(self, figsize=(4, 4), dpi=300, save_flag=False):
        plot_box_plot_hist_plot(
            self.paragraphs_df,
            column="paragraph_avg_word_len",
            title="Average Word Length per Paragraph Distribution Plot",
            figsize=figsize,
            dpi=dpi,
            save_flag=save_flag,
            file_path=os.path.join(
                self.out_dir, "paragraph-length-distribution.png")
        )

    def get_stop_words_corpus(self, language='english'):
        stop_words = set(stopwords.words(language))
        stop_words_corpus = defaultdict(int)
        for word in self.raw_corpus:
            if word in stop_words:
                stop_words_corpus[word] += 1
        return stop_words_corpus

    def get_top_k_stop_words(self, stop_words_corpus=None, top_k=10):
        if stop_words_corpus is None:
            stop_words_corpus = self.get_stop_words_corpus(language='english')
        top_k_keys = nlargest(top_k, stop_words_corpus,
                              key=stop_words_corpus.get)
        top_k_stop_words = {
            key: stop_words_corpus[key] for key in top_k_keys
        }
        return top_k_stop_words

    def plot_top_k_stop_words(self, top_k_stop_words, title="Stop Words Count Plot", figsize=(24, 24), dpi=300,
                              save_flag=False, file_path=None):
        df = pd.DataFrame(
            top_k_stop_words.items(), columns=["stop_words", "count"])
        fig, axs = plt.subplots(1, 1, figsize=figsize,
                                dpi=dpi, constrained_layout=False)
        pt = sns.barplot(data=df, x="count", y="stop_words",
                         palette=sns.color_palette("Set2"))
        axs.set_facecolor('white')
        plt.title(title)
        if save_flag:
            fig.savefig(file_path, dpi=dpi, facecolor='white')
            plt.close()

    def get_non_stop_words_corpus(self, language='english'):
        stop_words = set(stopwords.words(language))
        counter = Counter(self.raw_corpus)
        most = counter.most_common()
        non_stop_words_corpus = defaultdict(int)
        for word, count in most:
            if (word not in stop_words):
                non_stop_words_corpus[word] = count
        return non_stop_words_corpus

    def get_top_k_non_stop_words(self, non_stop_words_corpus=None, top_k=10):
        if non_stop_words_corpus is None:
            non_stop_words_corpus = self.get_non_stop_words_corpus(
                language='english')
        top_k_keys = nlargest(top_k, non_stop_words_corpus,
                              key=non_stop_words_corpus.get)
        top_k_non_stop_words = {
            key: non_stop_words_corpus[key] for key in top_k_keys
        }
        return top_k_non_stop_words

    def plot_top_k_non_stop_words(self, top_k_non_stop_words, title="Non-Stop Words Count Plot", figsize=(24, 24), dpi=300,
                                  save_flag=False, file_path=None):
        df = pd.DataFrame(
            top_k_non_stop_words.items(), columns=["non_stop_words", "count"])
        fig, axs = plt.subplots(1, 1, figsize=figsize,
                                dpi=dpi, constrained_layout=False)
        pt = sns.barplot(data=df, x="count", y="non_stop_words",
                         palette=sns.color_palette("Set2"))
        axs.set_facecolor('white')
        plt.title(title)
        if save_flag:
            fig.savefig(file_path, dpi=dpi, facecolor='white')
            plt.close()

    def get_ngrams(self, n=2, return_list=False):
        grams = ngrams(self.raw_corpus, n)
        if return_list:
            grams = list(grams)
        return grams

    def get_top_k_ngrams(self, n=2, top_k=10):
        vec = CountVectorizer(ngram_range=(n, n)).fit(
            self.paragraphs_df["paragraphs"])
        bag_of_words = vec.transform(self.paragraphs_df["paragraphs"])
        sum_words = bag_of_words.sum(axis=0)
        words_freq = [(word, sum_words[0, idx])
                      for word, idx in vec.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        grams = words_freq[:top_k]
        top_k_ngrams = defaultdict(int)
        for gram in grams:
            top_k_ngrams[gram[0]] = gram[1]
        return top_k_ngrams

    def plot_top_k_ngrams(self, top_k_ngrams, title="NGrams Count Plot", figsize=(24, 24), dpi=300,
                          save_flag=False, file_path=None):
        df = pd.DataFrame(
            top_k_ngrams.items(), columns=["ngrams", "count"])
        fig, axs = plt.subplots(1, 1, figsize=figsize,
                                dpi=dpi, constrained_layout=False)
        pt = sns.barplot(data=df, x="count", y="ngrams",
                         palette=sns.color_palette("Set2"))
        axs.set_facecolor('white')
        plt.title(title)
        if save_flag:
            fig.savefig(file_path, dpi=dpi, facecolor='white')
            plt.close()

    def build_lda(self, n_components=2):
        vectorizer = CountVectorizer()
        data_vectorized = vectorizer.fit_transform(
            self.paragraphs_df["paragraphs"])
        lda_model = LatentDirichletAllocation(n_components=n_components)
        lda_vectors = lda_model.fit_transform(data_vectorized)
        return vectorizer, lda_model, lda_vectors

    def extract_topics(self, vectorizer, model, words_per_topics=10):
        topics = {}
        for idx, topic in enumerate(model.components_):
            topics[idx] = []
            styled_print("Topic %d:" % (idx), header=True)
            for i in topic.argsort()[:-words_per_topics - 1:-1]:
                styled_print((vectorizer.get_feature_names_out()[i], topic[i]))
                topics[idx].append(vectorizer.get_feature_names_out()[i])
        return topics