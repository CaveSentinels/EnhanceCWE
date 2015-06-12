from rest_framework import serializers
from cwe.models import CWE


class CWESerializer(serializers.ModelSerializer):
    class Meta:
        # Associate this serializer with CWE
        model = CWE
        # The fields that this serializer processes
        fields = ('id',    # The ID of the CWE
                  'code',  # The code of the CWE
                  'name',  # The name of the CWE
                  )
