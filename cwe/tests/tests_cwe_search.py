from django.test import TestCase
from cwe.cwe_search import CWESearchLocator, CWEKeywordSearch

# Create your tests here.

class CWESearchTest(TestCase):
    """
    This class is the test suite to test the methods of the CWESearchLocator class
    """

    def test_registration_with_service_locator(self):
        """
        Note: Here we are combining several test cases in a single method (or test case)
        because django treats each method as a separate test case and it seems that
        it runs test cases in parallel. In this case, the CWEServiceLocator only registers
        a CWESearchBase object if its priority is higher than that of the already registered
        one. So, registering a CWESearchBase object with some priority might fail if a
        CWESearchBase object with the higher priority has already been registered through
        some different test case.
        """

        # Note: Do not register with priority '1' because a default object of CWEKeywordSearch
        # is already registered in the init module (Refer __init__.py).

        # 'register' should successfully register an object of a concrete class of
        # the CWESearchBase and return 'True'
        cwe_keyword_search = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search, 2), True)

        # 'get_cwe_search' should return the object registered with highest priority
        self.assertEqual(CWESearchLocator.get_cwe_search(), cwe_keyword_search)

        # 'register' should successfully register an object of a concrete class of
        # the CWESearchBase with the priority higher than that of the already registered
        # object and return 'True'
        cwe_keyword_search2 = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search2, 3), True)

        # 'register' should not register an object of a concrete class of
        # the CWESearchBase with the priority equal to the priority of the already
        # registered object and return 'False'
        cwe_keyword_search3 = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search3, 3), False)

        # 'register' should not register an object of a concrete class of
        # the CWESearchBase with the priority lower than the priority of the already
        # registered object and return 'False'
        cwe_keyword_search2 = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search2, 1), False)


    def test_registration_with_service_locator_with_instance_not_of_type_CWESearchBase(self):
        """
        'register' should raise a value error when an object that doesn't inherits from
        CWESearchBase tries to register itself.
        """
        self.assertRaises(ValueError, CWESearchLocator.register, 'String Object', 100)