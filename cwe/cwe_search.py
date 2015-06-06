from abc import ABCMeta, abstractmethod
from nltk.stem.porter import *


class CWESearchLocator:
    """
    This class is the service locator class and provides methods for the CWE search service
    providers i.e. cwe search algorithm and the views. CWE search service providers register
    with the class as a service providers and assign a priority to themselves. The class also
    provides a method for the views to get the service providers with the highest priority.
    """

    highest_priority = 0  # static property to store the highest priority
    service_provider = None  # static property that stores a reference to the highest priority service provider

    @staticmethod
    def register(cwe_search, priority):
        """
        This class method is called by the service providers to register themselves with the
        service locator
        :param cwe_search: a reference to the object that is willing to register itself
        :param priority: the priority, which the object want to assign to itself
        :return: returns 'True' or 'False' depending on whether the registration is success or not
        """

        if isinstance(cwe_search, CWESearchBase):
            if priority > CWESearchLocator.highest_priority:
                CWESearchLocator.highest_priority = priority
                CWESearchLocator.service_provider = cwe_search
                return True
            else:
                return False
        else:
            raise ValueError('Registration as service provider failed: objects, which inherits CWESearchBase can only'
                             'register as the service provider')

    @staticmethod
    def get_cwe_search():
        """
        This class method is called by the views who wants to get a reference of the highest
        priority service provider
        :return: a reference to the highest priority service provider
        """
        return CWESearchLocator.service_provider



class CWESearchBase:
    """
    It is an abstract class acting as an interface for Keyword search module.
    All the cwe search algorithm class must inherit from this class and
    implement all the abstract methods.
    """
    __metaclass__ = ABCMeta

    # Abstract method declaration
    @abstractmethod
    def search_cwes(self, text):
        """
        This is the main abstract method which receives a string and passes the CWE Objects with their match counts
        It also invokes two other methods, i.e, remove_stopwords() and stem_text() to remove redundant words and stem
        the remaining text
        :param text: A string which corresponds to description
        :return: A list of tuples wherein the first item will be a CWE Object and second item will be its match count
        """
        pass

    @abstractmethod
    def remove_stopwords(self, text):
        """
        This abstract method reads stop words from a text file and removes the redundant words like a, an, the from the
        description
        :param text: A string which corresponds to description
        :return: A collection of words from the description from which all the stop words have been removed
        """
        pass

    @abstractmethod
    def stem_text(self, text):
        """
        This abstract method receives a collection of words. It forms a collection of stemmed words and send it to the calling function
        :param text: A collection of words from the description from which all the stop words have been removed
        :return: A collection of stemmed words
        """
        pass


#  Concrete Class definition
class CWEKeywordSearch(CWESearchBase):

    def __init__(self):
        """
        This is a constructor of the class which reads stop words from a file and stores them.
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
        """
        This is the concrete implementation of the super class' abstract method
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
        """
        This is the concrete implementation of the super class' abstract method
        """
        words_in_text = text.split()  # Tokenize the words

        # Remove Stop words
        filtered_words = words_in_text[:]  # make a copy of the word_list
        filtered_words = [word for word in words_in_text if word not in self.stop_words]
        return filtered_words


    def stem_text(self, filtered_words):
        """
        This is the concrete implementation of the super class' abstract method
        """

        st = PorterStemmer()  # Initialize a stemmer

        # Build stemmed list
        stemmed = [st.stem(word) for word in filtered_words]

        return stemmed


# Register a default CWESearchBase object with the service locator
try:
    CWESearchLocator.register(CWEKeywordSearch(), 1)
except ValueError as e:
    print e.message