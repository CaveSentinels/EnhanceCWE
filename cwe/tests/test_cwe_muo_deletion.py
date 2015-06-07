from django.test import TestCase
from django.db import IntegrityError
from cwe.models import Category, CWE
from muo.models import MisuseCase, UseCase, OSR, MUOContainer


class TestDeletion(TestCase):
    """
    This class is the test suite to test the deletion behavior of the Category, CWE,
    MisuseCase, UseCase, OSR and MUOContainer models.
    """

    def test_category_deletion_without_referring_cwes(self):
        """
        This is a positive test case
        'delete()' should delete the category that has not been referred by any CWE.
        """

        category = Category.objects.create(name='category1')
        category.delete()
        self.assertEqual(Category.objects.count(), 0)


    def test_category_deletion_with_referring_cwes(self):
        """
        This is a negative test case
        'delete()' should raise the IntegrityError when trying to delete the category
        that has been referred by one or more CWE.
        """

        category = Category.objects.create(name='category1')
        cwe = CWE.objects.create(code=123, name='CWE1')
        cwe.categories.add(category)
        self.assertRaises(IntegrityError, category.delete)


    def test_cwe_deletion_without_referring_misuse_cases(self):
        """
        This is a positive test case
        'delete()' should delete the CWE that has not been referred by any MisuseCase.
        """

        cwe = CWE.objects.create(code=123, name='CWE1')
        cwe.delete()
        self.assertEqual(CWE.objects.count(), 0)


    def test_cwe_deletion_with_referring_misuse_cases(self):
        """
        This is a negative test case
        'delete()' should raise the IntegrityError when trying to delete the CWE that has
        been referred by one or more MisuseCases.
        """

        cwe = CWE.objects.create(code=123, name='CWE1')
        misuse_case = MisuseCase.objects.create(description='misuse_case')
        misuse_case.cwes.add(cwe)
        self.assertRaises(IntegrityError, cwe.delete)


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


    def test_use_case_deletion_without_referring_osrs(self):
        """
        This is a positive test case
        'delete()' should delete the UseCase that has not been referred by any OSR.
        """

        misuse_case = MisuseCase.objects.create(description='misuse_case')
        use_case = UseCase.objects.create(description='use_case', misuse_case=misuse_case)
        use_case.delete()
        self.assertEqual(UseCase.objects.count(), 0)


    # An investigation is required on how to write unit test cases for the deletion of the
    # models that have a foreign key relation with another model. Currently this test case
    # is raising error.
    # Bug Created in Jira: MAS-514

    # def test_use_case_deletion_with_referring_osrs(self):
    #     """
    #     This is a negative test case
    #     'delete()' should raise the IntegrityError when trying to delete a UseCase that has
    #     been referred by one or more OSRs.
    #     """
    #
    #     misuse_case = MisuseCase.objects.create(description='misuse_case')
    #     use_case = UseCase.objects.create(description='use_case', misuse_case=misuse_case)
    #     OSR.objects.create(description='osr', use_case=use_case)
    #     self.assertRaises(IntegrityError, use_case.delete)


    def test_osr_delete(self):
        """
        This is a positive test case
        'delete()' should delete the OSR.
        """

        misuse_case = MisuseCase.objects.create(description='misuse_case')
        use_case = UseCase.objects.create(description='use_case', misuse_case=misuse_case)
        osr = OSR.objects.create(description='osr', use_case=use_case)
        osr.delete()
        self.assertEqual(OSR.objects.count(), 0)
