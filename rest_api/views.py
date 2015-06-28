import re
from cwe.models import CWE
from cwe.cwe_search import CWESearchLocator
from muo.models import UseCase
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_api.serializers import CWESerializer
from rest_api.serializers import MisuseCaseSerializer
from rest_api.serializers import UseCaseSerializer


class CWEAllList(APIView):
    """
    List all the CWEs that are available in the database.
    """
    queryset = CWE.objects.all()
    serializer_class = CWESerializer

    PARAM_OFFSET = "offset"
    PARAM_LIMIT = "limit"

    DEFAULT_OFFSET = "0"  # The default value of offset in GET method
    DEFAULT_LIMIT = "10"   # The default value of limit in GET method
    MAX_RETURN = "20"  # 20 CWEs will be returned at most, regardless many is specified in "limit".

    def _validate_parameter(self, value):
        # This regular expression matches integers like "1", "101", but not "+1", "-1", "1.2", "1.a", etc.
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^[0-9]+$"
        return re.match(param_pattern_regex, value) is not None

    def _form_err_msg_not_positive_integer(self, param_name, param_value):
        return ("Invalid arguments: '" + param_name +
                "' should be a positive integer like '101', but now '" + param_name +
                "' = '" + param_value + "'")

    def get(self, request):
        """
        @brief: Return the CWE objects in the database.
        @param: [in] request: The HTTP request.
        @return: rest_framework.response.Response
        """

        # Get the value of the parameters.

        offset_str = request.GET.get(self.PARAM_OFFSET)
        if offset_str is None:
            # No 'offset' is passed in.
            offset_str = self.DEFAULT_OFFSET
        else:
            # 'offset' is provided. Check if it is in the correct format.
            if self._validate_parameter(offset_str) is False:
                err_msg = self._form_err_msg_not_positive_integer(self.PARAM_OFFSET, offset_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        limit_str = request.GET.get(self.PARAM_LIMIT)
        if limit_str is None:
            # No 'limit' is passed in.
            limit_str = self.DEFAULT_LIMIT
        else:
            # 'limit' is provided. Check if it is in the correct format.
            if self._validate_parameter(limit_str) is False:
                err_msg = self._form_err_msg_not_positive_integer(self.PARAM_LIMIT, limit_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # 'offset' and 'limit' are string. Need to convert them to integers.
        # We do not want to use 'limit' as variable name because it conflicts
        # with a Python built-in function.
        offset = int(offset_str)
        limit = int(limit_str)
        limit = (limit if limit < self.MAX_RETURN else self.MAX_RETURN)

        # Now the arguments should be valid and we just fetch the required amount of objects
        # from database and return them.
        # Note: offset may be larger than the number of CWE objects. In this case, an empty
        # list will be returned.
        cwe_all = CWE.objects.all()[offset:offset+limit]
        serializer = CWESerializer(cwe_all, many=True)
        return Response(data=serializer.data)


class CWERelatedList(APIView):
    """
    @brief: List the CWEs that are related to the given text.
    """

    PARAM_TEXT = "text"

    def get(self, request):
        """
        @brief: Return the CWE objects that are suggested given the text.
        @param: [in] request: The HTTP request.
        @return: rest_framework.response.Response
        """

        text = request.GET.get(self.PARAM_TEXT)

        cwe_count_tuples = CWESearchLocator.get_instance().search_cwes(text)

        cwe_list = [cwe_count_tuple[0] for cwe_count_tuple in cwe_count_tuples]
        serializer = CWESerializer(cwe_list, many=True)

        return Response(data=serializer.data)


class MisuseCaseRelated(APIView):
    """
    @brief: List the misuse cases that are related to the specified CWEs.
    """

    PARAM_CWES = "cwes"

    def _validate_parameter(self, cwes_str):
        # This regular expression matches strings like "101" or "101,102,103".
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^([0-9]+,)*([0-9]+)$"
        return re.match(param_pattern_regex, cwes_str) is not None

    def _get_distinct_cwe_codes(self, cwes_str):
        return set(cwes_str.split(','))

    def _form_err_msg_malformed_cwes(self, cwes_str):
        return ("CWE code list is malformed: '" + cwes_str + "'. " +
                "It should be one or more positive integers separated by comma."
                )

    def _form_err_msg_cwes_not_found(self, cwe_codes_not_found):
        err_msg = ("The CWE of the following codes are not found: " +
                  ''.join(str(code)+"," for code in cwe_codes_not_found)
                   )
        return err_msg

    def get(self, request):
        """
        :param request: The HTTP request.
        :return: rest_framework.response.Response
        """

        # Get the "cwes" parameter value.
        cwes_str = request.GET.get(self.PARAM_CWES)

        # Validate the parameter or throw exception.
        if self._validate_parameter(cwes_str=cwes_str) is False:
            err_msg = self._form_err_msg_malformed_cwes(cwes_str)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the CWE codes from the parameter string.
        cwe_code_set = self._get_distinct_cwe_codes(cwes_str=cwes_str)

        # Create the list of returned misuse case.
        misuse_case_list = list()

        # Try to get all the CWE objects.
        cwes = CWE.objects.filter(code__in=cwe_code_set)

        # If there is any CWE not found, then we return an error.
        cwe_codes_fetched = set([str(cwe.code) for cwe in cwes])
        cwe_codes_not_found = cwe_code_set - cwe_codes_fetched

        if len(cwe_codes_not_found) > 0:
            err_msg = self._form_err_msg_cwes_not_found(cwe_codes_not_found)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Find the misuse cases that are related to the CWEs.
        for cwe in cwes:
            misuse_case_list += cwe.misuse_cases.all()

        # Remove the duplicated misuse cases, if there are any.
        misuse_case_list = list(set(misuse_case_list))
        serializer = MisuseCaseSerializer(misuse_case_list, many=True)

        return Response(data=serializer.data, exception=Exception())


class UseCaseRelated(APIView):
    """
    @brief: List the misuse cases that are related to the specified CWEs.
    """

    PARAM_MISUSE_CASES = "misuse_cases"

    def _validate_parameter(self, misuse_cases_str):
        # This regular expression matches strings like "1" or "1,2,3".
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^([0-9]+,)*([0-9]+)$"
        return re.match(param_pattern_regex, misuse_cases_str) is not None

    def _get_distinct_misuse_case_ids(self, misuse_cases_str):
        return set(misuse_cases_str.split(','))

    def _form_err_msg_malformed_misuse_cases(self, misuse_cases_str):
        return ("Misuse case ID list is malformed: '" + misuse_cases_str + "'. " +
                "It should be one or more positive integers separated by comma."
                )

    def get(self, request):
        """
        :param request: The HTTP request.
        :return: rest_framework.response.Response
        """

        # Get the "misuse_cases" parameter value.
        misuse_cases_str = request.GET.get(self.PARAM_MISUSE_CASES)

        # Validate the parameter or throw exception.
        if self._validate_parameter(misuse_cases_str=misuse_cases_str) is False:
            err_msg = self._form_err_msg_malformed_misuse_cases(misuse_cases_str)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the misuse case IDs from the parameter string.
        misuse_case_id_set = self._get_distinct_misuse_case_ids(misuse_cases_str=misuse_cases_str)

        # Create the list of returned use case.
        use_case_list = list()

        # Get all the use cases that are associated with the misuse cases.
        use_cases = UseCase.objects.filter(misuse_case__id__in=misuse_case_id_set)

        # Remove the duplicated use cases, if there are any.
        serializer = UseCaseSerializer(set(use_cases.all()), many=True)

        return Response(data=serializer.data, exception=Exception())