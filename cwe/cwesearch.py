#!/usr/bin/env python
__author__ = "Sankalp Anand"

from abc import ABCMeta, abstractmethod
from nltk.stem.lancaster import LancasterStemmer
import nltk
import operator


# Abstract class definition
class CWESearchBase:
    __metaclass__ = ABCMeta

    # Abstract method declaration
    @abstractmethod
    def searchcwes(text):
        pass

    @abstractmethod
    def stemtext(text):
        pass

    @abstractmethod
    def removestopwords(text):
        pass


#  Concrete Class definition
class CWEKeywordSearch(CWESearchBase):

    @staticmethod  # To avoid passing 'self'
    def searchcwes(text):

        cwekeywordsearchobj = CWEKeywordSearch()

        # Call Stop Word method here
        filtered_words = cwekeywordsearchobj.removestopwords(text)

        # Call stemmer here
        stemmed_list = cwekeywordsearchobj.stemtext(filtered_words)

        #  Form a dictionary with the count zero
        from cwe.models import CWE, Category, Keyword
        matchcount = {}
        cwelist = CWE.objects.all()

        for cwe in cwelist:
            name = cwe.name.encode('ascii')  # ASCII encoding to remove unwanted 'u' for unicode
            matchcount[name] = 0

        #  Count the exact number of occurrences
        for cwe in cwelist: # iterate over CWEs
            for CWETag in cwe.keywords.all():  # iterate over tags
                if CWETag.name in stemmed_list:  # check if the tags exist or not
                    matchcount[cwe.name] += 1

        matchcount_sorted = sorted(matchcount.items(), key=operator.itemgetter(1), reverse=True)
        return matchcount_sorted

    @staticmethod  # To avoid passing 'self'
    def stemtext(filtered_words):
        st = LancasterStemmer()  # Initialize a stemmer

        # Build stemmed list
        stemmed = []
        for word in filtered_words:
            stemmed.append(st.stem(word))

        return stemmed

    @staticmethod  # To avoid passing 'self'
    def removestopwords(text):
        wordsintext = text.split()  # Tokenize the words

        # Read stop words in a collection
        import os
        stop_words = []
        with open(os.getcwd() + '/cwe/stopwords.txt', 'r') as f:
            for line in f:
                for word in line.split():
                    stop_words.append(word)

        # Remove Stop words
        filtered_words = wordsintext[:]  # make a copy of the word_list
        for word in wordsintext:  # iterate over word_list
            if word in stop_words:
                filtered_words.remove(word) # remove word from filtered_word_list if it is a stopword

        return filtered_words




