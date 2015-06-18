import json
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from cwe.models import CWE
from cwe.models import Keyword
from muo.models import MisuseCase
from muo.models import MUOContainer
from muo.models import UseCase
from rest_api.views import CWEAllList
from rest_api.views import MisuseCaseRelated
from rest_api.views import UseCaseRelated


class RestAPITestBase(TestCase):

    _cli = Client()     # The testing client

    AUTH_TOKEN_TYPE_ACTIVE_USER = 0
    AUTH_TOKEN_TYPE_INACTIVE_USER = 1
    AUTH_TOKEN_TYPE_NONE = 2

    def setUp(self):
        self.set_up_users_and_tokens()
        self.set_up_test_data()

    def tearDown(self):
        self.tear_down_users_and_tokens()
        self.tear_down_test_data()

    def set_up_users_and_tokens(self):
        test_user_active = User(username='test_user_active', is_active=True)
        test_user_active.save()
        test_user_active_id = test_user_active.id
        self._test_user_active_token = str(Token.objects.get(user__id=test_user_active_id))

        test_user_inactive = User(username='test_user_inactive', is_active=False)
        test_user_inactive.save()
        test_user_inactive_id = test_user_inactive.id
        self._test_user_inactive_token = Token.objects.get(user__id=test_user_inactive_id)

    def set_up_test_data(self):
        # To be overridden by the subclass.
        pass

    def tear_down_users_and_tokens(self):
        Token.objects.all().delete()
        User.objects.all().delete()

    def tear_down_test_data(self):
        # To be overridden by the subclass.
        pass

    def http_get(self, url, auth_token_type=AUTH_TOKEN_TYPE_ACTIVE_USER):
        auth_token = self._test_user_active_token
        if auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER:
            auth_token = self._test_user_inactive_token
        elif auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_NONE:
            auth_token = None
        return self._cli.get(url, HTTP_AUTHORIZATION='Token '+str(auth_token))


class TestCWETextRelated(RestAPITestBase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests
    KEYWORD_NAMES = ["authent", "overflow", "bypass"]      # The names of keywords

    def set_up_test_data(self):
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

    def tear_down_test_data(self):
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
        response = self.http_get(self._form_url(text))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_positive_search_text_multiple_keywords(self):
        text = "the user can bypass the file access check due to a stack overflow caused by ..."
        response = self.http_get(self._form_url(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    # Negative test cases

    def test_negative_search_text_no_match(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._form_url(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_negative_no_authentication_token(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._form_url(text), auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._form_url(text), auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCWEAllList(RestAPITestBase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests

    def set_up_test_data(self):
        # Construct the test database
        for code in self.CWE_CODES:
            cwe = CWE(code=code, name="CWE #"+str(code))
            cwe.save()

    def tear_down_test_data(self):
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
        response = self.http_get(self._form_url(offset=None, max_return=None))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)

    def test_positive_get_2_default(self):
        CWEAllList.DEFAULT_MAX = 2  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._form_url(offset=2, max_return=None))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_0_0(self):
        response = self.http_get(self._form_url(offset=0, max_return=0))
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_0_1(self):
        response = self.http_get(self._form_url(offset=0, max_return=1))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)

    def test_positive_get_0_2(self):
        response = self.http_get(self._form_url(offset=0, max_return=2))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)

    def test_positive_get_0_10(self):
        response = self.http_get(self._form_url(offset=0, max_return=10))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_0(self):
        response = self.http_get(self._form_url(offset=2, max_return=0))
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_2_1(self):
        response = self.http_get(self._form_url(offset=2, max_return=1))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_10(self):
        response = self.http_get(self._form_url(offset=2, max_return=10))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    # Negative test cases

    def test_negative_get_3_default(self):
        response = self.http_get(self._form_url(offset=3, max_return=None))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_3_0(self):
        response = self.http_get(self._form_url(offset=3, max_return=0))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_3_1(self):
        response = self.http_get(self._form_url(offset=3, max_return=1))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_3_10(self):
        response = self.http_get(self._form_url(offset=3, max_return=10))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_n1_1(self):
        response = self.http_get(self._form_url(offset=-1, max_return=1))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_1_n1(self):
        response = self.http_get(self._form_url(offset=1, max_return=-1))
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._form_url(offset=2, max_return=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._form_url(offset=2, max_return=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestMisuseCaseSuggestion(RestAPITestBase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests

    def set_up_test_data(self):
        # Create CWEs.
        cwe101 = CWE(code=self.CWE_CODES[0])
        cwe101.save()
        cwe102 = CWE(code=self.CWE_CODES[1])
        cwe102.save()
        cwe103 = CWE(code=self.CWE_CODES[2])
        cwe103.save()

        # Create misuse cases that are associated with the CWEs
        mu1 = MisuseCase(description="Misuse Case 1")
        mu1.save()
        mu1.cwes.add(cwe101)
        mu2 = MisuseCase(description="Misuse Case 2")
        mu2.save()
        mu2.cwes.add(cwe102)
        mu3 = MisuseCase(description="Misuse Case 3")
        mu3.save()
        mu3.cwes.add(cwe102, cwe103)

    def tear_down_test_data(self):
        # Delete all the misuse cases first.
        MisuseCase.objects.all().delete()
        # Then delete all the CWEs.
        CWE.objects.all().delete()

    # Helper methods

    def _form_url(self, cwe_code_list):
        return ('http://localhost:8080/restapi/misuse_case/cwe_related?cwes=' +
            "".join(str(code)+"," for code in cwe_code_list)
            ).rstrip(',')

    def _misuse_case_info_found(self, json_content, mu_index):
        mu_name = "MU/0000" + str(mu_index)
        mu_description = "Misuse Case " + str(mu_index)
        found = False
        for json_mu in json_content:
            if (json_mu['id'] == mu_index
                    and json_mu['name'] == mu_name
                    and json_mu['description'] == mu_description):
                found = True
                break
        return found

    # Positive test cases

    def test_positive_single_cwe(self):
        response = self.http_get(self._form_url([self.CWE_CODES[0]]))
        json_content = json.loads(response.content)

        # Make sure exactly one misuse case is returned.
        self.assertEqual(len(json_content), 1)
        # Make sure the first misuse case is returned.
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)

    def test_positive_multiple_cwes(self):
        response = self.http_get(self._form_url([self.CWE_CODES[0], self.CWE_CODES[2]]))
        json_content = json.loads(response.content)
        # Make sure exactly two misuse cases are returned.
        self.assertEqual(len(json_content), 2)
        # Make sure the first and third misuse cases are returned.
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)

    def test_positive_distinct_misuse_cases(self):
        response = self.http_get(self._form_url([self.CWE_CODES[1], self.CWE_CODES[2]]))
        json_content = json.loads(response.content)
        # Both keyword #102 and #103 are associated with both misuse case #3.
        # We want to make sure that the same misuse case is returned only once.
        self.assertEqual(len(json_content), 2)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)

    # Negative test cases

    def test_negative_malformed_cwes(self):
        cwes_str_list = [
            "",     # Empty code list
            "101,102,",     # Additional ',' at the end
            "101|102",  # Not using ',' as separator
            "101.1,102.2",  # Not using integers
            "10a",  # Not using numeric values
            "10a,20b"   # Not using numeric values
        ]
        for cwes_str in cwes_str_list:
            response = self.http_get('http://localhost:8080/restapi/misuse_case/cwe_related?cwes='+cwes_str)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # Make sure the error message is generated using this method.
            self.assertEqual(response.content,
                             # Because response.content has been JSONized, we need to JSONize the
                             # error message in order to compare for equality.
                             str(json.dumps(MisuseCaseRelated()._form_err_msg_malformed_cwes(cwes_str)))
                             )

    def test_negative_not_found_cwes(self):
        response = self.http_get(self._form_url([101, 102, 103, 104, 105]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Make sure the error message is generated using this method.
        self.assertEqual(response.content,
                         # Because response.content has been JSONized, we need to JSONize the
                         # error message in order to compare for equality.
                         str(json.dumps(MisuseCaseRelated()._form_err_msg_cwes_not_found([104, 105])))
                         )

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._form_url([self.CWE_CODES[0]]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._form_url([self.CWE_CODES[0]]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUseCaseSuggestion(RestAPITestBase):

    cli = Client()  # The Client utility

    URL_BASE = "http://localhost:8080/restapi/use_case/misuse_case_related?misuse_cases="
    DESCRIPTION_BASE_MISUSE_CASE = "Misuse Case "     # Don't forget the trailing blank space.
    DESCRIPTION_BASE_USE_CASE = "Use Case "     # Don't forget the trailing blank space.
    DESCRIPTION_BASE_OSR = "Overlooked Security Requirement "   # Don't forget the trailing blank space.
    NAME_BASE_USE_CASE = "UC/"  # No trailing blank space. Must be changed according to UseCase's model.

    def set_up_test_data(self):
        # Create some misuse cases
        mu1 = MisuseCase(description=self.DESCRIPTION_BASE_MISUSE_CASE+"1")
        mu1.save()
        mu2 = MisuseCase(description=self.DESCRIPTION_BASE_MISUSE_CASE+"2")
        mu2.save()

        # Create an MUO container so we can save the use cases successfully.
        muo1 = MUOContainer(misuse_case=mu1)
        muo1.save()
        muo2 = MUOContainer(misuse_case=mu2)
        muo2.save()

        # Create some use cases(with OSRs)
        uc1 = UseCase(description=self.DESCRIPTION_BASE_USE_CASE+"1",
                      osr=self.DESCRIPTION_BASE_OSR+"1")
        uc1.muo_container = muo1
        uc1.save()
        uc2 = UseCase(description=self.DESCRIPTION_BASE_USE_CASE+"2",
                      osr=self.DESCRIPTION_BASE_OSR+"2")
        uc2.muo_container = muo2
        uc2.save()
        uc3 = UseCase(description=self.DESCRIPTION_BASE_USE_CASE+"3",
                      osr=self.DESCRIPTION_BASE_OSR+"3")
        uc3.muo_container = muo2
        uc3.save()

        # Create the foreign key relationships.
        mu1.usecase_set.add(uc1)
        mu2.usecase_set.add(uc2, uc3)

    def tear_down_test_data(self):
        # Delete all the MUO containers first.
        MUOContainer.objects.all().delete()
        # Delete all the use cases
        UseCase.objects.all().delete()
        # Delete all the misuse cases
        MisuseCase.objects.all().delete()

    def _form_url(self, misuse_case_id_list):
        return (self.URL_BASE + "".join(str(id)+"," for id in misuse_case_id_list)).rstrip(',')

    def _use_case_info_found(self, json_content, uc_index):
        uc_name = "UC/{0:05d}".format(uc_index)
        uc_description = self.DESCRIPTION_BASE_USE_CASE + str(uc_index)
        osr = self.DESCRIPTION_BASE_OSR + str(uc_index)
        found = False
        for json_uc in json_content:
            if (json_uc['id'] == uc_index
                    and json_uc['name'] == uc_name
                    and json_uc['description'] == uc_description
                    and json_uc['osr'] == osr):
                found = True
                break
        return found

    # Positive test cases

    def test_positive_single_misuse_case(self):
        response = self.http_get(self._form_url([1]))
        json_content = json.loads(response.content)

        # Make sure exactly one use case is returned.
        self.assertEqual(len(json_content), 1)
        # Make sure the first use case is returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)

    def test_positive_multiple_misuse_cases(self):
        response = self.http_get(self._form_url([1, 2]))
        json_content = json.loads(response.content)

        # Make sure all the use cases are returned.
        self.assertEqual(len(json_content), 3)
        # Make sure all the use cases are returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)
        self.assertEqual(self._use_case_info_found(json_content, 2), True)
        self.assertEqual(self._use_case_info_found(json_content, 3), True)

    # Negative test cases

    def test_negative_malformed_misuse_cases(self):
        misuse_cases_str_list = [
            "",     # Empty id list
            "1,2,",     # Additional ',' at the end
            "1|2",  # Not using ',' as separator
            "1.1,2.2",  # Not using integers
            "1a",  # Not using numeric values
            "1a,2b"   # Not using numeric values
        ]
        for misuse_cases_str in misuse_cases_str_list:
            response = self.http_get(self.URL_BASE+misuse_cases_str)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # Make sure the error message is generated using this method.
            self.assertEqual(response.content,
                             # Because response.content has been JSONized, we need to JSONize the
                             # error message in order to compare for equality.
                             str(json.dumps(UseCaseRelated()._form_err_msg_malformed_misuse_cases(misuse_cases_str)))
                             )

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._form_url([1]), auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._form_url([1]), auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)