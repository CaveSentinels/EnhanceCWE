from rest_framework import serializers
from cwe.models import CWE
from muo.models import MisuseCase
from muo.models import UseCase


class CWESerializer(serializers.ModelSerializer):
    class Meta:
        # Associate this serializer with CWE
        model = CWE
        # The fields that this serializer processes
        fields = ('id',    # The ID of the CWE
                  'code',  # The code of the CWE
                  'name',  # The name of the CWE
                  )


class MisuseCaseSerializer(serializers.ModelSerializer):
    class Meta:
        # Associate this serializer with MisuseCase
        model = MisuseCase
        # The fields that this serializer processes
        fields = ('id',     # The ID of the misuse case
                  'name',   # The name of the misuse case
                  'description',    # The description of the misuse case
                  )


class UseCaseSerializer(serializers.ModelSerializer):
    class Meta:
        # Associate this serializer with UseCase
        model = UseCase
        # The fields that this serializer processes
        fields = ('id',     # The ID of the use case
                  'name',   # The name of the use case
                  'description',    # The description of the use case
                  'osr',    # The description of overlooked security requirement
                  )