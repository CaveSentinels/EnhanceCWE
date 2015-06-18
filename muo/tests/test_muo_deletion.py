from django.test import TestCase
from django.db import IntegrityError
from muo.models import MisuseCase, UseCase


class TestMUODeletion(TestCase):
    """
    This class is the test suite to test the deletion behavior of MisuseCase, UseCase and OSR
    """

    def test_misuse_case_deletion_without_referring_use_cases(self):
        """
        This is a positive test case
        'delete()' should delete the MisuseCase that has not been referred by any UseCase.
        """

        misuse_case = MisuseCase.objects.create(description='misuse_case')
        misuse_case.delete()
        self.assertEqual(MisuseCase.objects.count(), 0)


    # An investigation is required on how to write unit test cases for the deletion of the
    # models that have a foreign key relation with another model. Currently this test case
    # is raising error.
    # Bug Created in Jira: MAS-514

    # def test_misuse_case_deletion_with_referring_use_cases(self):
    #     """
    #     This is a negative test case
    #     'delete()' should raise the IntegrityError when trying to delete a Misuse that has
    #     been referred by one or more UseCases.
    #     """
    #
    #     misuse_case = MisuseCase.objects.create(description='misuse_case')
    #     UseCase.objects.create(description='use_case' ,misuse_case=misuse_case)
    #     self.assertRaises(IntegrityError, misuse_case.delete)
