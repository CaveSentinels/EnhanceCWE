from django.test import TestCase
from cwesearch import CWEKeywordSearch

# Create your tests here
class CWESearchTests(TestCase):
    cwe_keyword_search_obj = CWEKeywordSearch()

    def setUp(self):
        """ Predefined database to set up database
        :param text: None
        :return: None
        """
        self.construct_test_database()

    def tearDown(self):
        """ Predefined database to delete the database
        :param text: None
        :return: None
        """
        pass

    def construct_test_database(self):
        """ This function creates the temporary database
        :param text: None
        :return: None
        """
        from models import Keyword, Category, CWE

        kw = Keyword(name='xml') # 1
        kw.save()

        kw = Keyword(name='execut') # 2
        kw.save()

        kw = Keyword(name='remot') # 3
        kw.save()

        kw = Keyword(name='scripting') # 4
        kw.save()

        kw = Keyword(name='cross-sit') # 5
        kw.save()

        kw = Keyword(name='upload') # 6
        kw.save()

        kw = Keyword(name='fil') # 7
        kw.save()

        kw = Keyword(name='cod') # 8
        kw.save()

        kw = Keyword(name='javascript') # 9
        kw.save()

        kw = Keyword(name='ver') # 10
        kw.save()

        kw = Keyword(name='lack') # 11
        kw.save()

        kw = Keyword(name='valid') # 12
        kw.save()

        kw = Keyword(name='unauth') # 13
        kw.save()

        kw = Keyword(name='bypass') # 14
        kw.save()

        kw = Keyword(name='auth') # 15
        kw.save()

        kw = Keyword(name='inject') # 16
        kw.save()

        kw = Keyword(name='sql') # 17
        kw.save()

        cat = Category(name='Category5')
        cat.save()

        cat = Category(name='Category4')
        cat.save()

        cat = Category(name='Category3')
        cat.save()

        cat = Category(name='Category2')
        cat.save()

        cat = Category(name='Category1')
        cat.save()


        cwe = CWE(code=106, name='XML Injection')
        cwe.save()
        cwe.keywords.add(1)
        cwe.keywords.add(16)
        cwe.save()

        cwe = CWE(code=105, name='Remote Code Execution')
        cwe.save()
        cwe.keywords.add(2)
        cwe.keywords.add(3)
        cwe.keywords.add(8)
        cwe.save()

        cwe = CWE(code=104, name='Cross site scripting')
        cwe.save()
        cwe.keywords.add(4)
        cwe.keywords.add(5)
        cwe.save()

        cwe = CWE(code=103, name='File Upload Vulnerability')
        cwe.save()
        cwe.keywords.add(6)
        cwe.keywords.add(7)
        cwe.save()

        cwe = CWE(code=102, name='Code Injection')
        cwe.save()
        cwe.keywords.add(8)
        cwe.keywords.add(9)
        cwe.keywords.add(16)
        cwe.save()

        cwe = CWE(code=101, name='Authentication bypass')
        cwe.save()
        cwe.keywords.add(10)
        cwe.keywords.add(11)
        cwe.keywords.add(12)
        cwe.keywords.add(13)
        cwe.keywords.add(14)
        cwe.keywords.add(15)
        cwe.save()

        cwe = CWE(code=100, name='SQL Injection')
        cwe.save()
        cwe.keywords.add(16)
        cwe.keywords.add(17)
        cwe.save()


    def test_check_suggestion_sqlinjection(self):
        """ This test case tests the algorithm for SQL Injection
        :param text: None
        :return: None
        """
        # Test # 1: SQL Injection
        text="This module exploits a stacked SQL injection in order to add an administrator user to the " \
                    "SolarWinds Orion database."
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'SQL Injection' in cwe.name and count > 0].__len__() > 0:
            res=True
        self.assertEqual(res, True)


    def test_check_suggestion_file_upload_vulnerability(self):
        """ This test case tests the algorithm for File upload vulnerability
        :param text: None
        :return: None
        """
        # Test # 2: File upload vulnerability
        text = "This module exploits a file upload vulnerability in all versions of the Holding Pattern theme found in " \
             "the upload_file.php script which contains no session or file validation. It allows unauthenticated users " \
             "to upload files of any type and subsequently execute PHP scripts in the context of the web server."
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'File Upload Vulnerability' in cwe.name and count > 0].__len__() > 0:
            res=True
        self.assertEqual(res, True)

    def test_check_suggestion_cross_site_scripting(self):
        """ This test case tests the algorithm for Cross site scripting
        :param text: None
        :return: None
        """
        # Test # 3: Cross site scripting
        text = "This module exploits a universal cross-site scripting (UXSS) vulnerability found in Internet Explorer " \
               "10 and 11. By default, you will steal the cookie from TARGET_URI (which cannot have X-Frame-Options or " \
               "it will fail). You can also have your own custom JavaScript by setting the CUSTOMJS option. Lastly, " \
               "you might need to configure the URIHOST option if you are behind NAT."
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'Cross site scripting' in cwe.name and count > 0].__len__() > 0:
            res=True
        self.assertEqual(res, True)

    def test_check_suggestion_blank_text(self):
        """ This test case tests the algorithm for Blank text
        :param text: None
        :return: None
        """
        # Test # 4: Blank text
        text="".lower()
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'SQL Injection' in cwe.name and count > 0].__len__() > 0:
            res=True

        self.assertEqual(res, False)

    def test_check_suggestion_sql_injection_not_exists(self):
        """ This test case tests the algorithm for 'SQL Injection' does not exist in the description
        :param text: None
        :return: None
        """
        # Test # 5: 'SQL Injection' does not exist in the description
        text="This module exploits a hidden backdoor API in Apple's Admin framework on Mac OS X to escalate privileges " \
             "to root, dubbed \"Rootpipe.\" This module was tested on Yosemite 10.10.2 and should work on previous versions. " \
             "The patch for this issue was not backported to older releases. Note: you must run this exploit as an " \
             "admin user to escalate to root."
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'SQL Injection' in cwe.name and count > 0].__len__() > 0:
            res=True
        self.assertEqual(res, False)

    def test_check_suggestion_all_integers(self):
        """ This test case tests the algorithm for All Integers
        :param text: None
        :return: None
        """
        # Test # 6: All Integers
        text="111111111111111122222222222222223333333333333444444444"
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'SQL Injection' in cwe.name and count > 0].__len__() > 0:
            res=True
        self.assertEqual(res, False)

    def test_check_suggestion_blank_text(self):
        """ This test case tests the algorithm for File upload vulnerability
        :param text: None
        :return: None
        """
        # Test # 7: None
        text = ""
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'SQL Injection' in cwe.name and count > 0].__len__() > 0:
            res=True
        self.assertEqual(res, False)

    def test_check_suggestion_reverse_test_case(self):
        """ This test case tests the algorithm for File upload vulnerability
        :param text: None
        :return: None
        """
        # Test # 8: Reverse test cases
        # Authentication Bypass - It gives three suggestions
        text = "This module exploits an authentication bypass vulnerability in Solarwinds Storage Manager. " \
             "The vulnerability exists in the AuthenticationFilter, which allows to bypass authentication with specially crafted URLs. " \
             "After bypassing authentication, is possible to use a file upload function to achieve remote code execution. " \
             "This module has been tested successfully in Solarwinds Store Manager Server 5.1.0 and 5.7.1 on Windows 32 bits, Windows 64 bits and " \
             "Linux 64 bits operating systems."

        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if [cwe for cwe, count in results if 'Authentication bypass' in cwe.name and count > 0].__len__() > 0:
            res = True
        self.assertEqual(res, True)

        cwe_matches = [cwe for cwe, count in results if 'Authentication bypass' in cwe.name and count > 0]


        # Test # 9: Reverse test cases
        # The above test gives 3 suggestions -
        # 101 - Authentication Bypass
        # 103 - File Upload Vulnerability
        # 105 - Remote Code Execution
        # Now we will check whether they really exist in the description
        from cwe.models import CWE
        for matched_cwe in cwe_matches:
            # Check for 101
            cwe_list = CWE.objects.filter(name=matched_cwe).distinct()
            res1 = False
            for cwe in cwe_list: # iterate over CWEs
                for keyword in cwe.keywords.all():
                    if not str(keyword) in text:
                        res1 = False
                    else:
                        res1 = True

            # If res1 remains False, it means that there was no keyword which was there in the text
            # It it becomes True at some point, it means atleast one keyword matched
            self.assertEqual(res, True)
