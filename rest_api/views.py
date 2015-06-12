from cwe.models import CWE
from cwe.cwe_search import CWESearchLocator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_api.serializers import CWESerializer


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