from django.test import TestCase
from django.db import IntegrityError
from cwe.models import Category, CWE
from muo.models import MisuseCase


class TestCWEDeletion(TestCase):
    """
    This class is the test suite to test the deletion behavior of the Category and CWE deletion
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
