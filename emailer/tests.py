from django.core import mail
from django.test import TestCase
from mock import patch
from muo.models import MUOContainer, MisuseCase, UseCase
from cwe.models import CWE
from django.contrib.auth.models import User

class EmailTest(TestCase):

    # This is to test if the email sending functionality(SMTP Server is correctly configured)
    def setUp(self):
        test_user = User(username='test_user', is_active=True)
        test_user.save()
        self.user = test_user
        cwe1 = CWE(code=1, name='CWE-1')
        cwe1.save()
        misuse_case = MisuseCase()
        misuse_case.save()
        misuse_case.cwes.add(*[cwe1])
        muo_container = MUOContainer.objects.create(misuse_case=misuse_case,status='in_review')
        muo_container_draft = MUOContainer.objects.create(misuse_case=misuse_case,status='draft')
        muo_container_draft.save()
        muo_container.save()
        muo_container.cwes.add(*[cwe1])
        muo_container.save()
        self.muo_container = muo_container

    def test_send_email(self):
        # Send message.
        mail.send_mail('Subject here', 'Here is the message.',
            'enhancedcwe@gmail.com', ['example@gmail.com'],
            fail_silently=False)
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')

    # This is to test to check if signals are generated when muo gets accepted
    @patch('muo.signals.muo_accepted.send')
    def test_muo_accepted_signal_triggered(self, mock):
        self.muo_container.action_approve(self.user)
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that your signal was called only once.
        self.assertEqual(mock.call_count, 1)

    # This is to test to check if signals are generated when muo gets rejected
    @patch('muo.signals.muo_rejected.send')
    def test_muo_rejected_signal_triggered(self, mock):
        self.muo_container.action_reject("reason",self.user)
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count, 1)

    # This is to test to check if signals are generated when muo is voted up
    @patch('muo.signals.muo_voted_up.send')
    def test_muo_votedup_signal_triggered(self, mock):
        # TODO the action for voted up should be invoked
        # muo_container.(method name)
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count, 1)

    # This is to test to check if signals are generated when muo is voted down
    @patch('muo.signals.muo_voted_down.send')
    def test_muo_voteddown_signal_triggered(self, mock):
        # TODO the action for voted down should be invoked
        # muo_container.method_name
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count, 1)

    @patch('muo.signals.muo_commented.send')
    def test_muo_commented_signal_triggered(self, mock):
        # TODO the action for muo commented should be invoked
        # muo_container.method_name
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count,1)


    @patch('muo.signals.muo_submitted_for_review.send')
    def test_muo_submitted_for_review_signal_triggered(self, mock):
        cwe1 = CWE(code=3, name='CWE-1')
        cwe1.save()
        misuse_case = MisuseCase()
        misuse_case.save()
        misuse_case.cwes.add(*[cwe1])
        muo_container = MUOContainer.objects.create(misuse_case=misuse_case,status='draft')
        use_case = UseCase(muo_container=muo_container, misuse_case=misuse_case)
        use_case.save()

       # muo_container_draft.save()
        muo_container.save()
        muo_container.cwes.add(*[cwe1])
        muo_container.save()
        # TODO the action for muo submitted for review should be invoked
        # muo_container.method_name
        # Check that the signal was called.

        muo_container.action_submit()
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count,1)
