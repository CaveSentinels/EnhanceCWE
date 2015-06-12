from django.test import TestCase
from django.test import Client
from rest_framework import status
from cwe.models import CWE
from cwe.models import Keyword
from rest_api.views import CWEAllList


class TestCWETextRelated(TestCase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests
    KEYWORD_NAMES = ["authent", "overflow", "bypass"]      # The names of keywords

    cli = Client()  # The Client utility

    def setUp(self):
        # Create the keywords
        kw_auth = Keyword(name=self.KEYWORD_NAMES[0])
        kw_auth.save()
        kw_overflow = Keyword(name=self.KEYWORD_NAMES[1])
        kw_overflow.save()
        kw_bypass = Keyword(name=self.KEYWORD_NAMES[2])
        kw_bypass.save()

        # Create the CWEs
        cwe101 = CWE(code=self.CWE_CODES[0], name="CWE #"+str(self.CWE_CODES[0]))
        cwe101.save()
        cwe101.keywords.add(kw_auth)    # Only one keyword

        cwe102 = CWE(code=self.CWE_CODES[1], name="CWE #"+str(self.CWE_CODES[1]))
        cwe102.save()
        cwe102.keywords.add(kw_overflow, kw_bypass)    # Multiple keywords

        cwe103 = CWE(code=self.CWE_CODES[2], name="CWE #"+str(self.CWE_CODES[2]))
        cwe103.save()
        cwe103.keywords.add(kw_overflow, kw_bypass)    # Multiple keywords

    def tearDown(self):
        # Delete all CWEs.
        CWE.objects.all().delete()
        # Delete all keywords.
        Keyword.objects.all().delete()

    # Helper methods

    def _form_url(self, text):
        url = 'http://localhost:8080/restapi/cwe/text_related/'
        # After the text, there must have the trailing slash, otherwise an HTTP 301 will be returned.
        # See http://stackoverflow.com/questions/1579846/django-returning-http-301
        url += (text + '/')
        return url

    def _cwe_info_found(self, content, code):
        cwe_repr = "{\"id\":" + str(code-100) + ",\"code\":" + str(code) + ",\"name\":\"CWE #" + str(code) + "\"}"
        return cwe_repr in content

    def _cwe_info_empty(self, content):
        return content == '[]'

    # Positive test cases

    def test_positive_search_text_1_keyword(self):
        text = "authentication fails because ..."
        response = self.cli.get(self._form_url(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_positive_search_text_multiple_keywords(self):
        text = "the user can bypass the file access check due to a stack overflow caused by ..."
        response = self.cli.get(self._form_url(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    # Negative test cases

    def test_negative_search_text_no_match(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.cli.get(self._form_url(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)


class TestCWEAllList(TestCase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests
    cli = Client()  # The Client testing utility

    def setUp(self):
        # Construct the test database
        for code in self.CWE_CODES:
            cwe = CWE(code=code, name="CWE #"+str(code))
            cwe.save()

    def tearDown(self):
        # Destruct the test database
        for code in self.CWE_CODES:
            cwe = CWE.objects.get(code=code)
            cwe.delete()

    # Helper methods

    def _form_url(self, offset, max_return):
        url = 'http://localhost:8080/restapi/cwe/all/'
        url += ((str(offset)+'/') if offset is not None else '')
        url += ((str(max_return)+'/') if offset is not None and max_return is not None else '')
        return url

    def _cwe_info_found(self, content, code):
        cwe_repr = "{\"id\":" + str(code-100) + ",\"code\":" + str(code) + ",\"name\":\"CWE #" + str(code) + "\"}"
        return cwe_repr in content

    def _cwe_info_empty(self, content):
        return content == '[]'

    # Positive test cases

    def test_positive_get_default_default(self):
        CWEAllList.DEFAULT_MAX = 2  # For test purpose we only return at most two CWEs.
        response = self.cli.get(self._form_url(offset=None, max_return=None))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)

    def test_positive_get_2_default(self):
        CWEAllList.DEFAULT_MAX = 2  # For test purpose we only return at most two CWEs.
        response = self.cli.get(self._form_url(offset=2, max_return=None))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_0_0(self):
        response = self.cli.get(self._form_url(offset=0, max_return=0))
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_0_1(self):
        response = self.cli.get(self._form_url(offset=0, max_return=1))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)

    def test_positive_get_0_2(self):
        response = self.cli.get(self._form_url(offset=0, max_return=2))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)

    def test_positive_get_0_10(self):
        response = self.cli.get(self._form_url(offset=0, max_return=10))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_0(self):
        response = self.cli.get(self._form_url(offset=2, max_return=0))
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_2_1(self):
        response = self.cli.get(self._form_url(offset=2, max_return=1))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_10(self):
        response = self.cli.get(self._form_url(offset=2, max_return=10))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    # Negative test cases

    def test_negative_get_3_default(self):
        response = self.cli.get(self._form_url(offset=3, max_return=None))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_3_0(self):
        response = self.cli.get(self._form_url(offset=3, max_return=0))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_3_1(self):
        response = self.cli.get(self._form_url(offset=3, max_return=1))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_3_10(self):
        response = self.cli.get(self._form_url(offset=3, max_return=10))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_n1_1(self):
        response = self.cli.get(self._form_url(offset=-1, max_return=1))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_1_n1(self):
        response = self.cli.get(self._form_url(offset=1, max_return=-1))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)