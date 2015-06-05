#!/usr/bin/env python

from abc import ABCMeta, abstractmethod
from nltk.stem.porter import *
import operator



class CWESearchBase:
    """ It is an abstract class acting as an interface for Keyword search module
    """
    __metaclass__ = ABCMeta

    # Abstract method declaration
    @abstractmethod
    def search_cwes(self, text):
        """This is the main abstract method which receives a string and passes the CWE Objects with their match counts
        It also invokes two other methods, i.e, remove_stopwords() and stem_text() to remove redundant words and stem
        the remaining text
        :param text: A string which corresponds to description
        :return: A list of tuples wherein the first item will be a CWE Object and second item will be its match count
        """
        pass

    @abstractmethod
    def remove_stopwords(self, text):
        """ This abstract method reads stop words from a text file and removes the redundant words like a, an, the from the
        description
        :param text: A string which corresponds to description
        :return: A collection of words from the description from which all the stop words have been removed
        """
        pass

    @abstractmethod
    def stem_text(self, text):
        """ This abstract method receives a collection of words. It forms a collection of stemmed words and send it to the calling function
        :param filtered_words: A collection of words from the description from which all the stop words have been removed
        :return: A collection of stemmed words
        """
        pass


#  Concrete Class definition
class CWEKeywordSearch(CWESearchBase):

    def __init__(self):
        """  This is a constructor of the class which reads stop words from a file and stores them.
        The words don't need to be read from the disk again and again for every request.
        """

        # Read stop words in a collection from a file stored in the disk
        import os
        self.stop_words = []
        with open(os.getcwd() + '/cwe/stopwords.txt', 'r') as f:
            for line in f:
                for word in line.split():
                    self.stop_words.append(word)

    def search_cwes(self, text):
        """This is the main method which receives a string and passes the CWE Objects with their match counts
        It also invokes two other methods, i.e, remove_stopwords() and stem_text() to remove redundant words and stem
        the remaining text
        :param text: A string which corresponds to description
        :return: A list of tuples wherein the first item will be a CWE Object and second item will be its match count
        """

        # Call Stop Word method here
        filtered_words = self.remove_stopwords(text)

        # Call stemmer here
        stemmed_list = self.stem_text(filtered_words)

        #  Form a dictionary with the count zero
        from cwe.models import CWE
        match_count = []
        cwe_list = CWE.objects.filter(keywords__name__in = stemmed_list).distinct()

        #  Count the exact number of occurrences
        for cwe in cwe_list: # iterate over CWEs
            match_count.append((cwe, cwe.keywords.filter(name__in = stemmed_list).count()))

        match_count.sort(key= lambda x: x[1], reverse=True)
        return match_count




    def remove_stopwords(self, text):
        """ This methods reads stop words from a text file and removes the redundant words like a, an, the from the
        description
        :param text: A string which corresponds to description
        :return: A collection of words from the description from which all the stop words have been removed
        """
        words_in_text = text.split()  # Tokenize the words

        # Remove Stop words
        filtered_words = words_in_text[:]  # make a copy of the word_list
        filtered_words = [word for word in words_in_text if word not in self.stop_words]
        return filtered_words


    def stem_text(self, filtered_words):
        """ This methods receives a collection of words. It forms a collection of stemmed words and send it to the calling function
        :param filtered_words: A collection of words from the description from which all the stop words have been removed
        :return: A collection of stemmed words
        """

        st = PorterStemmer()  # Initialize a stemmer

        # Build stemmed list
        stemmed = [st.stem(word) for word in filtered_words]

        return stemmed




