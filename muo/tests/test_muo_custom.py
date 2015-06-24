from django.test import TestCase
from cwe.models import CWE
from muo.models import MUOContainer, MisuseCase, UseCase
from django.contrib.auth.models import User
from django.db import IntegrityError


class TestCustomMUO(TestCase):
    '''
    This class is the test suite for the MUOContainer model class to test the behavior
    of the custom MUOs.
    '''

    def setUp(self):
        """
        This method does the general setup needed for the test methods.
        For now it just creates a custom MUOContainer object
        """
        test_user = User(username='test_user', is_active=True)
        test_user.save()
        self.user = test_user

        cwe1 = CWE(code=1, name='CWE-1')
        cwe1.save()
        cwe2 = CWE(code=2, name='CWE-2')
        cwe2.save()

        misuse_case = MisuseCase()
        misuse_case.save()
        misuse_case.cwes.add(*[cwe1, cwe2])

        muo_container = MUOContainer.objects.create(misuse_case = misuse_case, isCustom=True, status='draft')
        muo_container.save()
        muo_container.cwes.add(*[cwe1, cwe2])
        # The id field is auto incremental and we need to know the id of the currently created object
        self.current_id = muo_container.id

        use_case = UseCase(muo_container=muo_container, misuse_case=misuse_case)
        use_case.save()


    def tearDown(self):
        '''
        All the clean up happens here after all the test cases are run
        '''
        UseCase.objects.all().delete()
        MUOContainer.objects.all().delete()
        MisuseCase.objects.all().delete()
        CWE.objects.all().delete()


    def test_action_promote_with_status_draft(self):
        '''
        action_promote should change the status to 'approved' when called on the MUOContainer object with status 'draft'
        '''
        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = 'draft'  # Make sure the status is 'draft'
        muo_container.action_promote()
        self.assertEqual(muo_container.status, 'approved')

    def test_action_promote_with_status_in_review(self):
        '''
        action_promote should raise the 'ValueError' when called on the MUOContainer object with status 'in_review'
        '''
        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = 'in_review'  # Make sure the status is 'in_review'

        self.assertRaises(ValueError, muo_container.action_promote)

    def test_action_promote_with_status_in_approved(self):
        '''
        action_promote should raise the 'ValueError' when called on the MUOContainer object with status 'approved'
        '''
        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = 'approved'  # Make sure the status is 'approved'

        self.assertRaises(ValueError, muo_container.action_promote)

    def test_action_promote_with_status_in_rejected(self):
        '''
        action_promote should raise the 'ValueError' when called on the MUOContainer object with status 'rejected'
        '''
        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = 'rejected'  # Make sure the status is 'rejected'

        self.assertRaises(ValueError, muo_container.action_promote)

    def test_action_promote_without_custom_muo(self):
        '''
        action_promote should raise the 'ValueError' when called on the non custom MUOContainer object
        '''
        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = 'draft'  # Make sure the status is 'draft'
        muo_container.isCustom = False  # Make sure the is_custom flag is 'False'

        self.assertRaises(ValueError, muo_container.action_promote)

    def test_create_custom_muo_with_valid_arguments(self):
        '''
        'create_custom_muo' should create a MUO Container with is_custom flag 'True' and status 'draft' if passed
        all the required arguments
        '''
        cwes = [1, 2]
        misuse_case_description = 'This is a misuse case'
        use_case_description = 'This is a use case'
        osr = 'This is a osr'

        MUOContainer.create_custom_muo(cwes, misuse_case_description, use_case_description, osr, self.user)

        self.assertIsNotNone(MUOContainer.objects.get(created_by=self.user))
        self.assertEqual(MUOContainer.objects.get(created_by=self.user).status, 'draft')
        self.assertEqual(MUOContainer.objects.get(created_by=self.user).isCustom, True)
        self.assertEqual(MUOContainer.objects.get(created_by=self.user).cwes.count(), len(cwes))
        self.assertEqual(MUOContainer.objects.get(created_by=self.user).misuse_case.description, misuse_case_description)
        self.assertEqual(MUOContainer.objects.get(created_by=self.user).usecase_set.first().description, use_case_description)

    def test_create_custom_muo_with_no_cwes(self):
        cwes = []
        misuse_case_description = 'This is a misuse case'
        use_case_description = 'This is a use case'
        osr = 'This is a osr'

        self.assertRaises(IntegrityError, MUOContainer.create_custom_muo(cwes, misuse_case_description, use_case_description, osr, self.user))

    def test_create_custom_muo_with_invalid_cwes(self):
        cwes = ['1']
        misuse_case_description = 'This is a misuse case'
        use_case_description = 'This is a use case'
        osr = 'This is a osr'

        self.assertRaises(IntegrityError, MUOContainer.create_custom_muo(cwes, misuse_case_description, use_case_description, osr, self.user))

    # def test_create_custom_muo_with_non_existent_cwe(self):
    #     cwes = [1, 100]
    #     misuse_case_description = 'This is a misuse case'
    #     use_case_description = 'This is a use case'
    #     osr = 'This is a osr'
    #
    #     self.assertEqual(ValueError, MUOContainer.create_custom_muo(cwes, misuse_case_description, use_case_description, osr, self.user))