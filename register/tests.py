from django.conf import settings
from django.core import mail
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from allauth.account.models import EmailAddress, EmailConfirmation
from selenium import webdriver
import os

@override_settings(
    ACCOUNT_EMAIL_VERIFICATION='mandatory',
    SET_STAFF_ON_REGISTRATION=True)
class RegisterTest(LiveServerTestCase):
    form_params = {'username': 'myusername',
                   'first_name': 'myfirstname',
                   'last_name': 'mylastname',
                   'password': 'mypassword',
                   'email': 'wdbaruni@yahoo.com',
                   'recaptcha_response_field': 'PASSED'
                   }

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.signup_url = '%s%s' % (self.live_server_url, reverse('account_signup'))
        self.email_verify_sent_url = '%s%s' % (self.live_server_url, reverse('account_email_verification_sent'))

        self.selenium = webdriver.Firefox()
        super(RegisterTest, self).setUp()

    def tearDown(self):
        os.environ['RECAPTCHA_TESTING'] = 'False'
        self.selenium.quit()
        super(RegisterTest, self).tearDown()

    def test_signup_positive(self):
        email_count = len(mail.outbox)
        self.fill_register_form(self.selenium, self.signup_url)
        self.submit_register_form(self.selenium)

        # Verify signup was successful and redirected to the correct page
        self.assertEqual(self.selenium.current_url, self.email_verify_sent_url)

        # Verify email to verify the user's email was sent
        self.assertEqual(len(mail.outbox), email_count + 1)

        # Verify user was created
        user_filter = get_user_model().objects.filter(username=self.form_params.get('username'))
        self.assertTrue(user_filter.exists(), 'User was not created')

        # Verify user is staff
        user = user_filter[0]
        self.assertTrue(user.is_staff, 'User was not assigned as staff')

        # Verify email object was created
        email_filter = EmailAddress.objects.filter(user=user, email=self.form_params.get('email'))
        self.assertTrue(email_filter.exists(), 'EmailAddress was not created')

        email_obj = email_filter[0]

        # Verify email is not verified
        self.assertFalse(email_obj.verified, 'EmailAddress was automatically verified')

        # Verify EmailConfirmation object was created
        confirmation_filter = EmailConfirmation.objects.filter(email_address=email_obj)
        self.assertTrue(confirmation_filter.exists(), 'EmailConfirmation was not created')


        # Verify user email
        self.verify_email(self.live_server_url, self.selenium)
        # Re-reading email object from DB
        email_obj = EmailAddress.objects.filter(email= self.form_params.get('email'))[0]
        self.assertTrue(email_obj.verified, 'EmailAddress was not verified after confirming the verification link')



    @classmethod
    def fill_register_form(cls, selenium, signup_url):
        # Open the signup page.
        selenium.get(signup_url)

        # Fill signup information
        selenium.find_element_by_id("id_username").send_keys(cls.form_params.get('username'))
        selenium.find_element_by_id("id_password1").send_keys(cls.form_params.get('password'))
        selenium.find_element_by_id("id_password2").send_keys(cls.form_params.get('password'))
        selenium.find_element_by_id("id_first_name").send_keys(cls.form_params.get('first_name'))
        selenium.find_element_by_id("id_last_name").send_keys(cls.form_params.get('last_name'))
        selenium.find_element_by_id("id_email").send_keys(cls.form_params.get('email'))
        selenium.find_element_by_id("recaptcha_response_field").send_keys(cls.form_params.get('recaptcha_response_field'))


    @classmethod
    def submit_register_form(cls, selenium):
        # Locate register button and click it
        selenium.find_element_by_xpath('//input[@value="Sign Up"]').click()


    @classmethod
    def verify_email(cls, server_url, selenium, email=form_params['email']):
        email_filter = EmailAddress.objects.filter(email=email)
        assert email_filter.exists(), 'There is no EmailAddress object with email %s' % email

        email_obj = email_filter[0]
        assert email_obj.verified is False, 'The email address %s is already verified' % email

        email_confirm_filter = EmailConfirmation.objects.filter(email_address=email_obj)
        assert email_confirm_filter.exists(), 'There is no EmailConfirmation object with email %s' % email

        email_confirm_obj = email_confirm_filter[0]

        # Open the confirmation page.
        email_confirm_url = '%s%s' % (server_url, reverse('account_confirm_email', args=[email_confirm_obj.key]))
        selenium.get(email_confirm_url)

        # Locate submit button and click it
        selenium.find_element_by_xpath('//input[@value="Confirm"]').click()



@override_settings(
    LOGIN_REDIRECT_URL='/app/',
    NUMBER_OF_FAILED_LOGINS_BEFORE_CAPTCHA=3)
class LoginTest(LiveServerTestCase):

    form_params = {'username': 'myusername',
                   'password': 'mypassword',
                   'email': 'wdbaruni@yahoo.com',
                   'recaptcha_response_field': 'PASSED'
                   }

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.login_url = '%s%s' % (self.live_server_url, reverse('account_login'))

        user = get_user_model().objects.create(username=self.form_params['username'],
                                               email=self.form_params['email'],
                                               is_staff=True,
                                               is_active=True)
        user.set_password(self.form_params['password'])
        user.save()

        email_obj = EmailAddress.objects.create(user=user,
                                                email=self.form_params['email'],
                                                primary=True,
                                                verified=True)

        if 'register_approval' in settings.INSTALLED_APPS:
            email_obj.admin_approval = 'approved'
        email_obj.save()

        self.user = user
        self.login_redirect_url = '%s%s' % (self.live_server_url, settings.LOGIN_REDIRECT_URL)
        self.selenium = webdriver.Firefox()
        super(LoginTest, self).setUp()

    def tearDown(self):
        os.environ['RECAPTCHA_TESTING'] = 'False'
        self.selenium.quit()
        super(LoginTest, self).tearDown()


    def test_login_positive(self):
        self.fill_login_form(self.selenium, self.login_url)
        self.submit_login_form(self.selenium)

        self.assertEqual(self.selenium.current_url, self.login_redirect_url, 'Login Failed!')


    def test_login_captcha_after_n_failed_attempts(self):

        # Test the captcha won't show before N failed attempts
        for n in range(0, settings.NUMBER_OF_FAILED_LOGINS_BEFORE_CAPTCHA):
            self.fill_login_form(self.selenium, self.login_url)
            self.assertFalse(self.selenium.find_elements_by_id("recaptcha_response_field"), # note the element(s)
                             "Captcha appeard in login form before N failed attempts")

            # pass wrong password to fail the login attemmpt
            self.selenium.find_element_by_id("id_password").send_keys('wrong_password')
            self.submit_login_form(self.selenium)

            self.assertEqual(self.selenium.current_url, self.login_url, "Logged in even though the password is wrong")


        # Test the captcha will show after N failed attempts and that login will fail without correct captcha
        self.fill_login_form(self.selenium, self.login_url)
        self.assertTrue(self.selenium.find_elements_by_id("recaptcha_response_field"),
                        "Captcha did not appear in login after N failed attmpts")
        self.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.login_url, "Logged in even though the captcha is not entered")

        # Test that login will succeed with capthca
        self.fill_login_form(self.selenium, self.login_url)
        self.selenium.find_element_by_id("recaptcha_response_field").send_keys(self.form_params.get('recaptcha_response_field'))
        self.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.login_redirect_url, 'Login Failed with correct captcha!')



    @classmethod
    def fill_login_form(cls, selenium, login_url):
        # Open the signup page.
        selenium.get(login_url)

        # Fill signup information
        selenium.find_element_by_id("id_login").send_keys(cls.form_params.get('username'))
        selenium.find_element_by_id("id_password").send_keys(cls.form_params.get('password'))


    @classmethod
    def submit_login_form(cls, selenium):
        # Locate Login button and click it
        selenium.find_element_by_xpath('//button[@type="submit"][contains(text(), "Sign In")]').click()



