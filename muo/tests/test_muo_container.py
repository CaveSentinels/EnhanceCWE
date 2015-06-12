from django.test import TestCase
from django.core.exceptions import ValidationError
from muo.models import MUOContainer, MisuseCase, UseCase

# Create your tests here.

class TestMUOContainer(TestCase):
    """
    This class is the test suite for the MUOContainer model class. It contains
    test cases for the custom methods in the MUOContainer model.
    """

    def setUp(self):
        """
        This method does the general setup needed for the test methods.
        For now it just creates a MUOContainer object, but can be used to
        do any default settings
        """
        misuse_case = MisuseCase()
        misuse_case.save()
        muo_container = MUOContainer.objects.create(misuse_case = misuse_case)  # MUOContainer cannot be created without misuse case
        use_case = UseCase(muo_container=muo_container)  # Usecase cannot be created without MUOContainer
        use_case.save()  # save in the database


    def get_muo_container(self, status):
        """
        This method sets the status of the MUOContainer object with the one
        received in arguments.
        """

        muo_container = MUOContainer.objects.get(pk=1)
        muo_container.status = status
        muo_container.save()
        return muo_container


    # Test 'action_approve'

    def test_action_approve_with_status_in_review_and_without_usecase_in_muocontainer(self):
        """
        'action_approve' should raise the Validation Error when an attempt is made to approve the muo container
        without the use case i.e. when container is not complete
        """

        misuse_case = MisuseCase()
        misuse_case.save()
        muo_container = MUOContainer.objects.create(misuse_case = misuse_case)  # MUOContainer cannot be created without misuse case
        muo_container.status = 'in_review'
        muo_container.save()
        self.assertRaises(ValidationError, muo_container.action_approve)


    def test_action_approve_with_status_in_review(self):
        """
        This is a positive test case
        'action_approve' should set the status to 'approved' when called on a MUOContainer object with status 'in_review'.
        """

        muo_container = self.get_muo_container('in_review')
        muo_container.action_approve()
        self.assertEqual(muo_container.status, 'approved')


    def test_action_approve_with_status_draft(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'draft'.
        """

        muo_container = self.get_muo_container('draft')
        self.assertRaises(ValueError, muo_container.action_approve)


    def test_action_approve_with_status_rejected(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'rejected'.
        """

        muo_container = self.get_muo_container('rejected')
        self.assertRaises(ValueError, muo_container.action_approve)


    def test_action_approve_with_status_approved(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'approved'.
        """

        muo_container = self.get_muo_container('approved')
        self.assertRaises(ValueError, muo_container.action_approve)


    def test_action_approve_with_status_invalid(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a MUOContainer
        object with an invalid status value.
        """

        muo_container = self.get_muo_container('XXX')
        self.assertRaises(ValueError, muo_container.action_approve)


    # Test 'action_reject'

    def test_action_reject_with_status_in_review(self):
        """
        This is a positive test case
        'action_reject' should set the status to 'rejected' when called on a MUOContainer
        object with status 'in_review'.
        """

        muo_container = self.get_muo_container('in_review')
        muo_container.action_reject()
        self.assertEqual(muo_container.status, 'rejected')


    def test_action_reject_with_status_approved(self):
        """
        This is a positive test case
        'action_reject' should set the status to 'rejected' when called on a MUOContainer
        object with status 'in_review'.
        """

        muo_container = self.get_muo_container('approved')
        muo_container.action_reject()
        self.assertEqual(muo_container.status, 'rejected')


    def test_action_reject_with_status_draft(self):
        """
        This is a negative test case
        'action_reject' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'draft'.
        """

        muo_container = self.get_muo_container('draft')
        self.assertRaises(ValueError, muo_container.action_reject)


    def test_action_reject_with_status_rejected(self):
        """
        This is a negative test case
        'action_reject' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'rejected'.
        """

        muo_container = self.get_muo_container('rejected')
        self.assertRaises(ValueError, muo_container.action_reject)


    def test_action_reject_with_status_invalid(self):
        """
        This is a negative test case
        'action_reject' should raise a 'ValueError' exception when called on a MUOContainer
        object with an invalid status value.
        """

        muo_container = self.get_muo_container('XXX')
        self.assertRaises(ValueError, muo_container.action_reject)


    # Test 'action_submit'


    def test_action_submit_with_status_draft_and_without_usecase_in_muocontainer(self):
        """
        'action_aubmit' should raise the Validation Error when an attempt is made to submit the muo container
        without the use case i.e. when container is not complete
        """

        misuse_case = MisuseCase()
        misuse_case.save()
        muo_container = MUOContainer.objects.create(misuse_case = misuse_case)  # MUOContainer cannot be created without misuse case
        muo_container.status = 'draft'
        muo_container.save()
        self.assertRaises(ValidationError, muo_container.action_submit)


    def test_action_submit_with_status_draft(self):
        """
        This is a positive test case
        'action_submit' should set the status to 'in_review' when called on a MUOContainer
        object with status 'draft'.
        """

        muo_container = self.get_muo_container('draft')
        muo_container.action_submit()

        self.assertEqual(muo_container.status, 'in_review')


    def test_action_submit_with_status_approved(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'approved'.
        """

        muo_container = self.get_muo_container('approved')
        self.assertRaises(ValueError, muo_container.action_submit)


    def test_action_submit_with_status_rejected(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'rejected'.
        """

        muo_container = self.get_muo_container('rejected')
        self.assertRaises(ValueError, muo_container.action_submit)


    def test_action_submit_with_status_in_review(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'in_review'.
        """

        muo_container = self.get_muo_container('in_review')
        self.assertRaises(ValueError, muo_container.action_submit)


    def test_action_submit_with_status_invalid(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a MUOContainer
        object with an invalid status value.
        """

        muo_container = self.get_muo_container('XXX')
        self.assertRaises(ValueError, muo_container.action_submit)


    # Test 'action_save_in_draft'

    def test_action_save_in_draft_with_status_in_review(self):
        """
        This is a positive test case
        'action_save_in_draft' should set the status to 'draft' when called on a MUOContainer
        object with status 'in_review'.
        """

        muo_container = self.get_muo_container('in_review')
        muo_container.action_save_in_draft()
        self.assertEqual(muo_container.status, 'draft')


    def test_action_save_in_draft_with_status_rejected(self):
        """
        This is a positive test case
        'action_save_in_draft' should set the status to 'draft' when called on a MUOContainer
        object with status 'rejected'.
        """

        muo_container = self.get_muo_container('rejected')
        muo_container.action_save_in_draft()
        self.assertEqual(muo_container.status, 'draft')


    def test_action_save_in_draft_with_status_approved(self):
        """
        This is a negative test case
        'action_save_in_draft' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'approved'.
        """

        muo_container = self.get_muo_container('approved')
        self.assertRaises(ValueError, muo_container.action_save_in_draft)


    def test_action_save_in_draft_with_status_draft(self):
        """
        This is a negative test case
        'action_save_in_draft' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'draft'.
        """

        muo_container = self.get_muo_container('draft')
        self.assertRaises(ValueError, muo_container.action_save_in_draft)


    def test_action_save_in_draft_with_status_invalid(self):
        """
        This is a negative test case
        'action_save_in_draft' should raise a 'ValueError' exception when called on a MUOContainer
        object with an invalid status value.
        """

        muo_container = self.get_muo_container('XXX')
        self.assertRaises(ValueError, muo_container.action_save_in_draft)


    # Test relationship creation/deletion on approve and reject

    def test_relationship_creation_on_action_approve(self):
        '''
        on 'action_approve', the relationship between the misuse case of the muo container and
        all the use cases of the container should get created
        '''

        muo_container = self.get_muo_container('in_review')  # This method return muo container in which misuse case already has a relationship created with the use case
        use_case = UseCase(muo_container=muo_container)  # Usecase cannot be created without MUOContainer
        use_case.save()  # save in the database
        muo_container.action_approve()  # a relationship should get created between the misuse case of the muocontainer and this new use case
        self.assertEqual(muo_container.status, 'approved')
        self.assertEqual(muo_container.misuse_case.usecase_set.count(), 2)


    def test_relationship_deletion_on_action_reject(self):
        '''
        on action_reject, the relationship between the misuse case of then muo container and all the use cases
        of the container should get removed
        '''

        muo_container = self.get_muo_container('approved')  # This method return muo container in which misuse case already has a relationship created with the use case
        use_case = UseCase(muo_container=muo_container)  # Usecase cannot be created without MUOContainer
        muo_container.misuse_case.usecase_set.add(use_case)  # Relate misuse case and use case
        use_case.save()  # save in the database
        muo_container.action_reject()  # the relationship between the misuse case and all the use cases should get removed.
        self.assertEqual(muo_container.status, 'rejected')
        self.assertEqual(muo_container.misuse_case.usecase_set.count(), 0)
        self.assertEqual(muo_container.usecase_set.count(), 2)