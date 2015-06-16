import re
from cwe.models import CWE
from cwe.cwe_search import CWESearchLocator
from muo.models import MisuseCase
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

    DEFAULT_OFFSET = 0  # The default value of offset in GET method
    DEFAULT_MAX = 100   # The default value of max in GET method

    def get(self, request, offset=DEFAULT_OFFSET, max_return=DEFAULT_MAX):
        """
        @brief: Return the CWE objects in the database.
        @param: [in] request: The HTTP request.
        @param: [in] offset: The starting index of all the CWE objects. Must be >= 0 and
            less than the count of all the CWE objects.
        @param: [in] max_return: The count of CWE objects to be returned at most.
            Must be >= 0.
        @return: rest_framework.response.Response
        """

        # offset and max are string. Need to convert them to integers.
        offset = int(offset)
        max_return = int(max_return)

        # offset and max should not be negative numbers.
        # TODO: However, because the URL pattern ensures that offset and max will be non-negative
        # integers, should we still verify the arguments here?
        if offset < 0 or max_return < 0:
            err_msg = ("Invalid arguments: 'offset' and 'max_return' should not be negative, but offset=" +
                       str(offset) + " and max_return=" + str(max_return))
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Although offset can be greater than the size of CWE objects from Python's view
        # because Python's list access is rewound if the index exceeds the size,
        # it may make no sense to the API users because they can't assume the implementation
        # language and can only comprehend the behavior with a common sense while the
        # common sense expects an access violation when upper limit is exceeded.
        if offset > CWE.objects.all().count():
            err_msg = ("Invalid argument: 'offset' should not exceed the count of CWE objects, but CWE has " +
                       str(len(CWE.objects.all())) + " object(s) while offset=" + str(offset))
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Now the arguments should be valid and we just fetch the required amount of objects
        # from database and return them.
        cwe_all = CWE.objects.all()[offset:offset+max_return]
        serializer = CWESerializer(cwe_all, many=True)
        return Response(data=serializer.data)


class CWERelatedList(APIView):
    """
    @brief: List the CWEs that are related to the given text.
    """

    def _find_related_cwes(self, text):
        """
        @brief: Find the CWEs that are related with the given text.
        @param: [in] text: The CWEs will be searched against the given text.
        @return: A list of CWEs.
        """

        cwe_count_tuples = CWESearchLocator.get_instance().search_cwes(text)
        cwe_list = [cwe_count_tuple[0] for cwe_count_tuple in cwe_count_tuples]

        return cwe_list

    def get(self, request, text):
        """
        @brief: Return the CWE objects that are suggested given the text.
        @param: [in] request: The HTTP request.
        @param: [in] text: The text which should be parsed and related CWEs be extracted from.
        @return: rest_framework.response.Response
        """

        cwe_list = self._find_related_cwes(text=text)
        serializer = CWESerializer(cwe_list, many=True)

        return Response(data=serializer.data)


class MisuseCaseRelated(APIView):
    """
    @brief: List the misuse cases that are related to the specified CWEs.
    """

    def _validate_parameter(self, cwes_str):
        # This regular expression matches strings like "101" or "101,102,103".
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^([0-9]+,)*([0-9]+)$"
        return re.match(param_pattern_regex, cwes_str) is not None

    def _get_distinct_cwe_codes(self, cwes_str):
        return set(cwes_str.split(','))

    def _form_err_msg_malformed_cwes(self, cwes_str):
        return ("CWE code list is malformed: \"" + cwes_str + "\". " +
                "It should be in the form of either \"101\" or \"101,102,103\""
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
        cwes_str = request.GET.get("cwes")

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

    def _validate_parameter(self, misuse_cases_str):
        # This regular expression matches strings like "1" or "1,2,3".
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^([0-9]+,)*([0-9]+)$"
        return re.match(param_pattern_regex, misuse_cases_str) is not None

    def _get_distinct_misuse_case_ids(self, misuse_cases_str):
        return set(misuse_cases_str.split(','))

    def _form_err_msg_malformed_misuse_cases(self, misuse_cases_str):
        return ("Misuse case ID list is malformed: \"" + misuse_cases_str + "\". " +
                "It should be in the form of either \"1\" or \"1,2,3\""
                )

    def get(self, request):
        """
        :param request: The HTTP request.
        :return: rest_framework.response.Response
        """

        # Get the "misuse_cases" parameter value.
        misuse_cases_str = request.GET.get("misuse_cases")

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