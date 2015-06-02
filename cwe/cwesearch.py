from abc import ABCMeta, abstractmethod
from nltk.stem.lancaster import LancasterStemmer
import nltk
import operator


# Abstract class definition
class CWESearchBase:
    __metaclass__ = ABCMeta

    # Abstract method declaration
    @abstractmethod
    def searchCWEs(text): pass

    @abstractmethod
    def stemText(text): pass


class CWEKeywordSearch(CWESearchBase):

    @staticmethod #  To avoid passing 'self'
    def searchCWEs(text):

        wordsintext = text.split()


        # Read stop words in a collection
        import os
        stop_words = []
        with open(os.getcwd() + '/cwe/StopWords.txt', 'r') as f:
            for line in f:
                for word in line.split():
                    stop_words.append(word)

        # Remove Stop Words
        filtered_words = wordsintext[:]  # make a copy of the word_list
        for word in wordsintext:  # iterate over word_list
            if word in stop_words:
                filtered_words.remove(word) # remove word from filtered_word_list if it is a stopword



        # call stemText here
        CWEKeywordSearchObj = CWEKeywordSearch()
        stemmedList = CWEKeywordSearchObj.stemText(filtered_words)

        # print '\nStemmed description...'
        # print ' '.join(stemmed)

        #  Form a dictionary with the count zero for each
        from cwe.models import CWE, Category, Keyword
        matchcount = {}
        CWEList = CWE.objects.all()

        for cwe in CWEList:
            name = cwe.name.encode('ascii')
            matchcount[name] = 0

        #  Count the exact number of occurrences
        for cwe in CWEList: # iterate over CWEs
            for CWETag in cwe.keywords.all():  # iterate over tags
                if CWETag.name in stemmedList:  # check if the tags exist or not
                    matchcount[cwe.name] += 1



        matchcount_sorted = sorted(matchcount.items(), key=operator.itemgetter(1), reverse=True)


        # print sorted_x
        # for CWE in matchcount_sorted:
        #     print CWE



        return matchcount_sorted




    @staticmethod #  To avoid passing 'self'
    def stemText(filtered_words):
        st = LancasterStemmer()

        # Build stemmed list
        stemmed = []
        for word in filtered_words:
            stemmed.append(st.stem(word))

        return stemmed


