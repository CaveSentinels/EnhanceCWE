from django.core import mail
from django.test import TestCase


class EmailTest(TestCase):
    # This is to test if the email sending functionality(SMTP Server is correctly configured)

    def test_send_email(self):
        # Send message.
        mail.send_mail('Subject here', 'Here is the message.',
            'enhancedcwe@gmail.com', ['swati201088@gmail.com'],
            fail_silently=False)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')



    @patch('full.path.to.signals.question_posted.send')
    def test_question_posted_signal_triggered(self, mock):
        #form = YourForm()
        form.cleaned_data = {'name': 'Jan Nowak'}
        form.save()

        # Check that your signal was called.
        self.assertTrue(mock.called)

        # Check that your signal was called only once.
        self.assertEqual(mock.call_count, 1)
