import json
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from cwe.models import CWE
from cwe.models import Keyword
from muo.models import MisuseCase
from muo.models import MUOContainer
from muo.models import UseCase
from rest_api.views import CWERelatedList
from rest_api.views import CWEAllList
from rest_api.views import MisuseCaseRelated
from rest_api.views import UseCaseRelated
from rest_api.views import SaveCustomMUO


class RestAPITestBase(TestCase):

    _cli = Client()     # The testing client

    AUTH_TOKEN_TYPE_ACTIVE_USER = 0
    AUTH_TOKEN_TYPE_INACTIVE_USER = 1
    AUTH_TOKEN_TYPE_NONE = 2

    def setUp(self):
        self.set_up_users_and_tokens()
        self.set_up_test_data()

    def tearDown(self):
        self.tear_down_test_data()
        self.tear_down_users_and_tokens()

    def set_up_users_and_tokens(self):
        self._user_1 = User(username='user_1', is_active=True)
        self._user_1.save()
        self._user_1_token = str(Token.objects.get(user__id=self._user_1.id))

        self._user_2 = User(username='user_2', is_active=True)
        self._user_2.save()
        self._user_2_token = str(Token.objects.get(user__id=self._user_2.id))

        self._user_3_inactive = User(username='user_3_inactive', is_active=False)
        self._user_3_inactive.save()
        self._user_3_inactive_id = self._user_3_inactive.id
        self._user_3_inactive_token = Token.objects.get(user__id=self._user_3_inactive_id)

    def set_up_test_data(self):
        # To be overridden by the subclass.
        pass

    def tear_down_users_and_tokens(self):
        Token.objects.all().delete()
        User.objects.all().delete()

    def tear_down_test_data(self):
        # To be overridden by the subclass.
        pass

    def http_get(self, url, params, auth_token_type=AUTH_TOKEN_TYPE_ACTIVE_USER):
        auth_token = self._user_1_token
        if auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER:
            auth_token = self._user_3_inactive_token
        elif auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_NONE:
            auth_token = None
        return self._cli.get(url, data=params, HTTP_AUTHORIZATION='Token '+str(auth_token))

    def http_post(self, url, data, auth_token_type=AUTH_TOKEN_TYPE_ACTIVE_USER):
        auth_token = self._user_1_token
        if auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER:
            auth_token = self._user_3_inactive_token
        elif auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_NONE:
            auth_token = None
        return self._cli.post(url, data, HTTP_AUTHORIZATION='Token '+str(auth_token))


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

    def _get_base_url(self):
        return reverse("restapi_CWETextRelated")

    def _form_url_params(self, text):
        return {CWERelatedList.PARAM_TEXT: text}

    def _cwe_info_found(self, content, code):
        cwe_repr = "{\"id\":" + str(code-100) + ",\"code\":" + str(code) + ",\"name\":\"CWE #" + str(code) + "\"}"
        return cwe_repr in content

    def _cwe_info_empty(self, content):
        return content == '[]'

    # Positive test cases

    def test_positive_search_text_1_keyword(self):
        text = "authentication fails because ..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_positive_search_text_multiple_keywords(self):
        text = "the user can bypass the file access check due to a stack overflow caused by ..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    # Negative test cases

    def test_negative_search_text_no_match(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_negative_no_authentication_token(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
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

    def _get_base_url(self):
        return reverse("restapi_CWEAll")

    def _form_url_params(self, offset=None, limit=None, code=None, name_contains=None):
        params = dict()
        if offset is not None:
            params[CWEAllList.PARAM_OFFSET] = str(offset)
        if limit is not None:
            params[CWEAllList.PARAM_LIMIT] = str(limit)
        if code is not None:
            params[CWEAllList.PARAM_CODE] = str(code)
        if name_contains is not None:
            params[CWEAllList.PARAM_NAME_CONTAINS] = str(name_contains)
        return params

    def _cwe_info_found(self, content, code):
        cwe_repr = "{\"id\":" + str(code-100) + ",\"code\":" + str(code) + ",\"name\":\"CWE #" + str(code) + "\"}"
        return cwe_repr in content

    def _cwe_info_empty(self, content):
        return content == '[]'

    # Positive test cases

    def test_positive_get_default_default(self):
        original_max_return = CWEAllList.DEFAULT_OFFSET
        CWEAllList.DEFAULT_LIMIT = 2  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=None, limit=None))
        
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_2_default(self):
        CWEAllList.DEFAULT_LIMIT = 2  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=None))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_default_2(self):
        original_max_return = CWEAllList.DEFAULT_OFFSET
        CWEAllList.DEFAULT_OFFSET = 0  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=None, limit=2))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_0_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=0))
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_0_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=1))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)

    def test_positive_get_0_2(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=2))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)

    def test_positive_get_0_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=10))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=0))
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_2_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=10))
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_0_1_max_2(self):
        original_max_return = CWEAllList.MAX_RETURN
        CWEAllList.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_0_10_max_2(self):
        original_max_return = CWEAllList.MAX_RETURN
        CWEAllList.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=10))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_0_3_102_None(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=3, code=102))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_positive_get_0_3_None_CWE(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=3, name_contains="CWE"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_0_2_None_CWE(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=2, name_contains="CWE"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    # Negative test cases

    def test_negative_get_3_default(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=0))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=10))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_n1_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=-1, limit=1))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_1_n1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=1, limit=-1))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_invalid_inputs(self):
        invalid_inputs = [
            ("0", "a"),     # 'limit' is not integer.
            ("0", "1a"),    # 'limit' is not integer.
            ("0", "a1"),    # 'limit' is not integer.
            ("a", "1"),     # 'offset' is not integer.
            ("1a", "1"),    # 'offset' is not integer.
            ("a1", "1"),    # 'offset' is not integer.
        ]
        for input_pair in invalid_inputs:
            response = self.http_get(self._get_base_url(), self._form_url_params(input_pair[0], input_pair[1]))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_get_0_2_None_name(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=2, name_contains="name"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_0_3_code_name_contains_both_present(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=3, code=102, name_contains="CWE"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_0_3_abc_None(self):
        invalid_codes = [
            "102a",
            "a102",
            "abc",
            "+-*/"
        ]
        for invalid_code in invalid_codes:
            response = self.http_get(self._get_base_url(),
                                     self._form_url_params(offset=0, limit=3, code=invalid_code))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestMisuseCaseSuggestion(RestAPITestBase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests

    def _create_muo_and_misuse_case(self, cwes, muc_desc, custom, approved, creator):
        # Create the MUO container
        cwe_ids = [cwe.id for cwe in cwes]
        MUOContainer.create_custom_muo(cwe_ids,
                                       misusecase=muc_desc,
                                       usecase="",    # Use Case is not important here.
                                       osr="",    # OSR is not important here.
                                       created_by=creator
                                       )
        # We can find this MUO container because only one misuse case is associated with it.
        muo = MUOContainer.objects.get(misuse_case__description=muc_desc)

        if not custom:
            # This is not a custom MUO. We need to change its is_custom field.
            muo.is_custom = False

        if approved:
            # By default, the newly created MUO container is in 'draft' state.
            # If it should be in 'approved' state, we need to submit and approve it.
            muo.action_submit()
            muo.action_approve()

    def set_up_test_data(self):
        # Create CWEs.
        cwe101 = CWE(code=self.CWE_CODES[0])
        cwe101.save()
        cwe102 = CWE(code=self.CWE_CODES[1])
        cwe102.save()
        cwe103 = CWE(code=self.CWE_CODES[2])
        cwe103.save()

        # Create the MUO containers and misuse cases.
        self._create_muo_and_misuse_case(cwes=[cwe101],
                                         muc_desc="Misuse Case 1",
                                         custom=False,
                                         approved=True,     # Approved, so it's generic.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe102],
                                         muc_desc="Misuse Case 2",
                                         custom=True,
                                         approved=True,     # Approved, so it's generic but also custom.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe102, cwe103],
                                         muc_desc="Misuse Case 3",
                                         custom=True,
                                         approved=False,    # Not approved, so it's custom.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe102],
                                         muc_desc="Misuse Case 4",
                                         custom=True,
                                         approved=False,    # Not approved, so it's custom.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe103],
                                         muc_desc="Misuse Case 5",
                                         custom=True,
                                         approved=False,    # Not approved, so it's custom.
                                         creator=self._user_2)  # By another user

    def tear_down_test_data(self):
        # Delete all the MUO containers first.
        MUOContainer.objects.all().delete()
        # Then delete all the misuse cases.
        MisuseCase.objects.all().delete()
        # Then delete all the CWEs.
        CWE.objects.all().delete()

    # Helper methods

    def _get_base_url(self):
        return reverse("restapi_MisuseCase_CWERelated")

    def _form_url_params(self, cwe_code_list):
        cwes_str = "".join(str(code)+"," for code in cwe_code_list).rstrip(',')
        return {MisuseCaseRelated.PARAM_CWES: cwes_str}

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
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0]]))
        json_content = json.loads(response.content)
        # Make sure exactly one misuse case is returned.
        self.assertEqual(len(json_content), 1)
        # Make sure the first misuse case is returned.
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

    def test_positive_multiple_cwes(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0], self.CWE_CODES[2]]))
        json_content = json.loads(response.content)
        # Make sure exactly two misuse cases are returned.
        self.assertEqual(len(json_content), 2)
        # Make sure the first, and third misuse cases are returned.
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

    def test_positive_all_cwes(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(self.CWE_CODES))
        json_content = json.loads(response.content)
        self.assertEqual(len(json_content), 4)
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

    def test_positive_distinct_misuse_cases(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[1], self.CWE_CODES[2]]))
        json_content = json.loads(response.content)
        # Both keyword #102 and #103 are associated with both misuse case #3.
        # We want to make sure that the same misuse case is returned only once.
        self.assertEqual(len(json_content), 3)
        self.assertEqual(self._misuse_case_info_found(json_content, 1), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

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
            # Note we cannot use the _get_base_url() and _form_url_params() because these two methods
            # will construct a valid Http request, while here we want an invalid one.
            response = self.http_get(self._get_base_url()+'?'+MisuseCaseRelated.PARAM_CWES+'='+cwes_str, None)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # Make sure the error message is generated using this method.
            self.assertEqual(response.content,
                             # Because response.content has been JSONized, we need to JSONize the
                             # error message in order to compare for equality.
                             str(json.dumps(MisuseCaseRelated()._form_err_msg_malformed_cwes(cwes_str)))
                             )

    def test_negative_not_found_cwes(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([101, 102, 103, 104, 105]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Make sure the error message is generated using this method.
        self.assertEqual(response.content,
                         # Because response.content has been JSONized, we need to JSONize the
                         # error message in order to compare for equality.
                         str(json.dumps(MisuseCaseRelated()._form_err_msg_cwes_not_found([104, 105])))
                         )

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0]]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0]]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUseCaseSuggestion(RestAPITestBase):

    DESCRIPTION_BASE_MISUSE_CASE = "Misuse Case "     # Don't forget the trailing blank space.
    DESCRIPTION_BASE_USE_CASE = "Use Case "     # Don't forget the trailing blank space.
    DESCRIPTION_BASE_OSR = "Overlooked Security Requirement "   # Don't forget the trailing blank space.
    NAME_BASE_USE_CASE = "UC/"  # No trailing blank space. Must be changed according to UseCase's model.

    def _create_muo_and_misuse_case(self, cwes, muc_desc, custom, approved, creator):
        # Create the misuse case and establish the relationship with the CWEs
        misuse_case = MisuseCase(description=muc_desc,
                                 created_by=creator
                                 )
        misuse_case.save()
        misuse_case.cwes.add(*cwes)  # Establish the relationship between the misuse case and CWEs

        # Create the MUO container for the misuse case and establish the relationship between the
        # MUO Container and CWEs
        muo_container = MUOContainer(is_custom=custom,
                                     status='draft',
                                     misuse_case=misuse_case,
                                     created_by=creator
                                     )
        muo_container.save()
        muo_container.cwes.add(*cwes) # Establish the relationship between the muo container and cwes

        return misuse_case, muo_container

    def _create_use_case_and_link_muo(self, index, muc, muo, creator):
        uc = UseCase(description=self.DESCRIPTION_BASE_USE_CASE+str(index),
                     osr=self.DESCRIPTION_BASE_OSR+str(index),
                     created_by=creator
                     )
        uc.muo_container = muo
        uc.misuse_case = muc
        uc.save()

    def _approve_muo_container(self, muo_container):
        muo_container.action_submit()
        muo_container.action_approve()

    def set_up_test_data(self):
        # Create some CWEs.
        cwe101 = CWE(code=101)
        cwe101.save()
        cwe102 = CWE(code=102)
        cwe102.save()
        cwe103 = CWE(code=103)
        cwe103.save()

        # Create the MUO containers and misuse cases.
        muc1, muo1 = self._create_muo_and_misuse_case(
            cwes=[cwe101],
            muc_desc="Misuse Case 1",
            custom=False,
            approved=True,  # Approved, so it's generic.
            creator=self._user_1
        )
        muc2, muo2 = self._create_muo_and_misuse_case(
            cwes=[cwe102],
            muc_desc="Misuse Case 2",
            custom=True,
            approved=True,  # Approved, so it's generic but also custom.
            creator=self._user_1
        )
        muc3, muo3 = self._create_muo_and_misuse_case(
            cwes=[cwe102, cwe103],
            muc_desc="Misuse Case 3",
            custom=True,
            approved=False,  # Not approved, so it's custom.
            creator=self._user_1
        )
        muc4, muo4 = self._create_muo_and_misuse_case(
            cwes=[cwe102],
            muc_desc="Misuse Case 4",
            custom=True,
            approved=False,  # Not approved, so it's custom.
            creator=self._user_1
        )
        muc5, muo5 = self._create_muo_and_misuse_case(
            cwes=[cwe103],
            muc_desc="Misuse Case 5",
            custom=True,
            approved=False,  # Not approved, so it's custom.
            creator=self._user_2
        )  # By another user

        # Create some use cases(with OSRs)
        self._create_use_case_and_link_muo(1, muc1, muo1, self._user_1)
        self._create_use_case_and_link_muo(2, muc2, muo2, self._user_1)
        self._create_use_case_and_link_muo(3, muc2, muo2, self._user_1)
        self._create_use_case_and_link_muo(4, muc3, muo3, self._user_1)
        self._create_use_case_and_link_muo(5, muc4, muo4, self._user_1)
        self._create_use_case_and_link_muo(6, muc4, muo4, self._user_1)
        self._create_use_case_and_link_muo(7, muc5, muo5, self._user_2)

        # Approve some of the MUO containers.
        self._approve_muo_container(muo1)
        self._approve_muo_container(muo2)

    def tear_down_test_data(self):
        # Delete all the use cases
        UseCase.objects.all().delete()
        # Delete all the MUO containers.
        MUOContainer.objects.all().delete()
        # Delete all the misuse cases
        MisuseCase.objects.all().delete()
        # Delete all the CWEs.
        CWE.objects.all().delete()

    def _get_base_url(self):
        return reverse("restapi_UseCase_MisuseCaseRelated")

    def _form_url_params(self, misuse_case_id_list):
        misuse_cases_str = "".join(str(code)+"," for code in misuse_case_id_list).rstrip(',')
        return {UseCaseRelated.PARAM_MISUSE_CASES: misuse_cases_str}

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
        response = self.http_get(self._get_base_url(), self._form_url_params([1]))
        json_content = json.loads(response.content)
        # Make sure exactly one use case is returned.
        self.assertEqual(len(json_content), 1)
        # Make sure the first use case is returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)
        self.assertEqual(self._use_case_info_found(json_content, 2), False)
        self.assertEqual(self._use_case_info_found(json_content, 3), False)
        self.assertEqual(self._use_case_info_found(json_content, 4), False)
        self.assertEqual(self._use_case_info_found(json_content, 5), False)
        self.assertEqual(self._use_case_info_found(json_content, 6), False)
        self.assertEqual(self._use_case_info_found(json_content, 7), False)

    def test_positive_multiple_misuse_cases(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([1, 2]))
        json_content = json.loads(response.content)
        # Make sure all the use cases are returned.
        self.assertEqual(len(json_content), 3)
        # Make sure all the use cases are returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)
        self.assertEqual(self._use_case_info_found(json_content, 2), True)
        self.assertEqual(self._use_case_info_found(json_content, 3), True)
        self.assertEqual(self._use_case_info_found(json_content, 4), False)
        self.assertEqual(self._use_case_info_found(json_content, 5), False)
        self.assertEqual(self._use_case_info_found(json_content, 6), False)
        self.assertEqual(self._use_case_info_found(json_content, 7), False)

    def test_positive_all_misuse_cases(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([n for n in range(1, 8)]))
        json_content = json.loads(response.content)
        # Make sure all the use cases are returned.
        self.assertEqual(len(json_content), 6)
        # Make sure all the use cases are returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)
        self.assertEqual(self._use_case_info_found(json_content, 2), True)
        self.assertEqual(self._use_case_info_found(json_content, 3), True)
        self.assertEqual(self._use_case_info_found(json_content, 4), True)
        self.assertEqual(self._use_case_info_found(json_content, 5), True)
        self.assertEqual(self._use_case_info_found(json_content, 6), True)
        self.assertEqual(self._use_case_info_found(json_content, 7), False)

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
            # Note we cannot use the _get_base_url() and _form_url_params() because these two methods
            # will construct a valid Http request, while here we want an invalid one.
            response = self.http_get(self._get_base_url()+'?'+UseCaseRelated.PARAM_MISUSE_CASES+'='+misuse_cases_str,
                                     None)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # Make sure the error message is generated using this method.
            self.assertEqual(response.content,
                             # Because response.content has been JSONized, we need to JSONize the
                             # error message in order to compare for equality.
                             str(json.dumps(UseCaseRelated()._form_err_msg_malformed_misuse_cases(misuse_cases_str)))
                             )

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([1]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([1]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestSaveCustomMUO(RestAPITestBase):

    _cli = Client()

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests
    CWE_IDS = []
    DESCRIPTION_MISUSE_CASE = "Sample Misuse Case Description"
    DESCRIPTION_USE_CASE = "Sample Use Case Description"
    DESCRIPTION_OSR = "Sample Overlooked Security Requirement Description"

    def set_up_test_data(self):
        # Clear the current CWE ID list.
        self.CWE_IDS = []

        # Create the CWEs
        cwe101 = CWE(code=self.CWE_CODES[0], name="CWE #"+str(self.CWE_CODES[0]))
        cwe101.save()
        self.CWE_IDS.append(cwe101.id)

        cwe102 = CWE(code=self.CWE_CODES[1], name="CWE #"+str(self.CWE_CODES[1]))
        cwe102.save()
        self.CWE_IDS.append(cwe102.id)

        cwe103 = CWE(code=self.CWE_CODES[2], name="CWE #"+str(self.CWE_CODES[2]))
        cwe103.save()
        self.CWE_IDS.append(cwe103.id)

    def tear_down_test_data(self):
        # Delete MUO containers.
        MUOContainer.objects.all().delete()
        # Delete misuse cases
        MisuseCase.objects.all().delete()
        # Delete use cases
        UseCase.objects.all().delete()

    def _form_base_url(self):
        return reverse("restapi_CustomMUO_Create")

    def _form_post_data(self, cwe_id_list, muc, uc, osr):
        cwe_ids_str = ("".join(str(cwe_id)+',' for cwe_id in cwe_id_list)).rstrip(',')
        return {SaveCustomMUO.PARAM_CWE_IDS: cwe_ids_str,
                SaveCustomMUO.PARAM_MISUSE_CASE_DESCRIPTION: muc,
                SaveCustomMUO.PARAM_USE_CASE_DESCRIPTION: uc,
                SaveCustomMUO.PARAM_OSR_DESCRIPTION: osr
                }

    def test_positive_all_valid(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_id_list=[self.CWE_IDS[0]],      # One CWE ID
                                    muc="",     # Empty description
                                    uc="",      # Empty description
                                    osr=""      # Empty description
                                    )
        response = self.http_post(base_url, data)
        # The POST method returned OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the post-conditions.
        # One and only one MUO was created.
        self.assertEqual(MUOContainer.objects.count(), 1)
        # The CWEs are associated correctly.
        muo = MUOContainer.objects.all()[0]
        cwes = CWE.objects.filter(muo_container=muo)
        associated_cwe_ids = {int(cwe.id) for cwe in cwes}
        passed_in_cwe_ids = {self.CWE_IDS[0]}
        self.assertEqual(associated_cwe_ids, passed_in_cwe_ids)
        # The misuse case was created correctly.
        self.assertEqual(muo.misuse_case.description, "")
        # Verify use case & OSR.
        use_cases = UseCase.objects.filter(muo_container=muo)
        self.assertEqual(use_cases.count(), 1)
        uc = use_cases[0]
        self.assertEqual(uc.description, "")
        self.assertEqual(uc.osr, "")

    def test_positive_all_valid_2(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_id_list=self.CWE_IDS,      # Multiple CWE ID
                                    muc=self.DESCRIPTION_MISUSE_CASE,   # Non-empty description
                                    uc=self.DESCRIPTION_USE_CASE,       # Non-empty description
                                    osr=self.DESCRIPTION_OSR        # Non-empty description
                                    )
        response = self.http_post(base_url, data)
        # The POST method returned OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the post-conditions.
        # One and only one MUO was created.
        self.assertEqual(MUOContainer.objects.count(), 1)
        # The CWEs are associated correctly.
        muo = MUOContainer.objects.all()[0]
        cwes = CWE.objects.filter(muo_container=muo)
        associated_cwe_ids = {int(cwe.id) for cwe in cwes}
        passed_in_cwe_ids = set(self.CWE_IDS)
        self.assertEqual(associated_cwe_ids, passed_in_cwe_ids)
        # The misuse case was created correctly.
        self.assertEqual(muo.misuse_case.description, self.DESCRIPTION_MISUSE_CASE)
        # Verify use case & OSR.
        use_cases = UseCase.objects.filter(muo_container=muo)
        self.assertEqual(use_cases.count(), 1)
        uc = use_cases[0]
        self.assertEqual(uc.description, self.DESCRIPTION_USE_CASE)
        self.assertEqual(uc.osr, self.DESCRIPTION_OSR)

    def test_negative_invalid_cwe_ids(self):
        invalid_cwes_str_list = [
            "",     # Empty code list
            "101,102,",     # Additional ',' at the end
            "101|102",  # Not using ',' as separator
            "101.1,102.2",  # Not using integers
            "10a",  # Not using numeric values
            "10a,20b"   # Not using numeric values
        ]
        base_url = self._form_base_url()
        for invalid_cwes_str in invalid_cwes_str_list:
            data = {SaveCustomMUO.PARAM_CWE_IDS: invalid_cwes_str,
                    SaveCustomMUO.PARAM_MISUSE_CASE_DESCRIPTION: self.DESCRIPTION_MISUSE_CASE,
                    SaveCustomMUO.PARAM_USE_CASE_DESCRIPTION: self.DESCRIPTION_USE_CASE,
                    SaveCustomMUO.PARAM_OSR_DESCRIPTION: self.DESCRIPTION_OSR
                    }
            response = self.http_post(base_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(MUOContainer.objects.count(), 0)   # No MUO was created.
            self.assertEqual(MisuseCase.objects.count(), 0)     # No misuse cases was created.
            self.assertEqual(UseCase.objects.count(), 0)     # No use cases was created.

    def test_negative_inactive_user(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_id_list=self.CWE_IDS,      # Valid CWE IDs
                                    muc=self.DESCRIPTION_MISUSE_CASE,   # Non-empty description
                                    uc=self.DESCRIPTION_USE_CASE,       # Non-empty description
                                    osr=self.DESCRIPTION_OSR        # Non-empty description
                                    )
        response = self.http_post(base_url, data, auth_token_type=self.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MUOContainer.objects.count(), 0)   # No MUO was created.
        self.assertEqual(MisuseCase.objects.count(), 0)     # No misuse cases was created.
        self.assertEqual(UseCase.objects.count(), 0)     # No use cases was created.

    def test_negative_no_auth(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_id_list=self.CWE_IDS,      # Valid CWE IDs
                                    muc=self.DESCRIPTION_MISUSE_CASE,   # Non-empty description
                                    uc=self.DESCRIPTION_USE_CASE,       # Non-empty description
                                    osr=self.DESCRIPTION_OSR        # Non-empty description
                                    )
        response = self.http_post(base_url, data, auth_token_type=self.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MUOContainer.objects.count(), 0)   # No MUO was created.
        self.assertEqual(MisuseCase.objects.count(), 0)     # No misuse cases was created.
        self.assertEqual(UseCase.objects.count(), 0)     # No use cases was created.
