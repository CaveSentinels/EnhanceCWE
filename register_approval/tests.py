from django.conf import settings
from django.core import mail
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from allauth.account.models import EmailAddress
from selenium import webdriver
import os
from register.tests import RegisterTest, LoginTest

@override_settings(
    LOGIN_REDIRECT_URL='/app/',
    ACCOUNT_EMAIL_VERIFICATION='mandatory',
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION='True',
    SET_STAFF_ON_REGISTRATION=True)
class RegisterApprovalTest(LiveServerTestCase):


    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.signup_url = '%s%s' % (self.live_server_url, reverse('account_signup'))
        self.login_url = '%s%s' % (self.live_server_url, reverse('account_login'))
        self.login_redirect_url = '%s%s' % (self.live_server_url, settings.LOGIN_REDIRECT_URL)

        self.selenium = webdriver.Firefox()
        super(RegisterApprovalTest, self).setUp()

    def tearDown(self):
        os.environ['RECAPTCHA_TESTING'] = 'False'
        self.selenium.quit()
        super(RegisterApprovalTest, self).tearDown()

    def test_login_approval(self):
        RegisterTest.fill_register_form(self.selenium, self.signup_url)
        RegisterTest.submit_register_form(self.selenium)
        RegisterTest.verify_email(self.live_server_url, self.selenium)

        # Test that user is redirected to login page after email confirmation
        self.assertEqual(self.selenium.current_url, self.login_url,
                         'Failed to redirect to login page after email confirmation')

        email_obj = EmailAddress.objects.filter(email=RegisterTest.form_params.get('email'))[0]

        # Verify email is not approved
        self.assertEqual(email_obj.admin_approval, 'pending', 'Registration request is not in pending state by default')


        # Try to login before approving from admin
        LoginTest.fill_login_form(self.selenium, self.login_url)
        LoginTest.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.login_url,
                         'Login succeeded even though admin did not approve registration request!')

        # Approve request
        email_count = len(mail.outbox)
        email_obj.action_approve()
        self.assertEqual(email_obj.admin_approval, 'approved', 'Registration request approval failed')

        # Verify approval email was sent
        self.assertEqual(len(mail.outbox), email_count + 1, 'Registration approval email failed to send')


        # Try to login after approving the request
        LoginTest.fill_login_form(self.selenium, self.login_url)
        LoginTest.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.login_redirect_url,
                         'Login failed even after admin approved registration request!')


    def test_login_pre_approved(self):
        RegisterTest.fill_register_form(self.selenium, self.signup_url)
        RegisterTest.submit_register_form(self.selenium)

        email_obj = EmailAddress.objects.filter(email=RegisterTest.form_params.get('email'))[0]
        email_obj.admin_approval = 'approved'
        email_obj.save()

        RegisterTest.verify_email(self.live_server_url, self.selenium)

        # Test that user is redirected to login page after email confirmation as he is already approved
        self.assertEqual(self.selenium.current_url, self.login_redirect_url,
                         'Failed to redirect to login page after email confirmation of pre-approved user')
