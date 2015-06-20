from django.core import mail
from django.test import TestCase


class EmailTest(TestCase):
    # This is to test if the email sending functionality(SMTP Server is correctly configured)

    def test_send_email(self):
        # Send message.
        mail.send_mail('Subject here', 'Here is the message.',
            'enhancedcwe@gmail.com', ['example@gmail.com'],
            fail_silently=False)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')








