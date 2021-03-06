from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from register.tests import RegisterHelper
from rest_framework.authtoken.models import Token


@override_settings(
    LOGIN_REDIRECT_URL='/app/')
class UserProfileTest(StaticLiveServerTestCase):


    @classmethod
    def setUpClass(cls):
        """ Set selenium in setUpClass to fire a single browser for all the test cases """
        cls.selenium = webdriver.Firefox()
        super(UserProfileTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(UserProfileTest, cls).tearDownClass()

    def setUp(self):
        self.profile_url = '%s%s' % (self.live_server_url, reverse('user_profile'))
        self.login_url = '%s%s' % (self.live_server_url, reverse('account_login'))
        self.inactive_url = '%s%s' % (self.live_server_url, reverse('account_inactive'))
        self.login_redirect_url = '%s%s' % (self.live_server_url, settings.LOGIN_REDIRECT_URL)

        super(UserProfileTest, self).setUp()

    def tearDown(self):
        RegisterHelper.logout(self.selenium, self.live_server_url)
        super(UserProfileTest, self).tearDown()

    def _save_profile(self):
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()


    def test_authenticate_access_profile(self):
        self.selenium.get(self.profile_url)
        self.assertEqual(self.selenium.current_url, '%s?next=%s' % (self.login_url, reverse('user_profile')),
                         "Not redirected to login page when accessing the profile URL unauthenticated")


    def test_update_personal_information(self):
        user = RegisterHelper.create_user()
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)

        first_name = "new first name"
        last_name = "new last name"

        self.selenium.get(self.profile_url)
        self.selenium.find_element_by_id('id_first_name').send_keys(first_name)
        self.selenium.find_element_by_id('id_last_name').send_keys(last_name)
        self._save_profile()

        # check the if the form was updated correctly or not
        self.assertEqual(self.selenium.current_url, self.profile_url, "Failed to redirect to profile page after submit")
        self.assertEqual(self.selenium.find_element_by_id('id_first_name').get_attribute('value'), first_name, "Failed to update first name in profile form")
        self.assertEqual(self.selenium.find_element_by_id('id_last_name').get_attribute('value'), last_name, "Failed to update last name in profile form")

        # reload user to check updates in the model
        user = get_user_model().objects.get(pk=user.pk)
        self.assertEqual(user.first_name, first_name, "Failed to update first name in user model")
        self.assertEqual(user.last_name, last_name, "Failed to update last name in user model")


    def test_update_notifications(self):
        user = RegisterHelper.create_user()
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)

        # Get the notification profile
        mailer_profile = user.mailer_profile
        mailer_profile.notify_muo_accepted = True
        mailer_profile.save()

        self.selenium.get(self.profile_url)
        self.selenium.find_element_by_id('id_notify_muo_accepted').click()
        self._save_profile()

        # check the if the form was updated correctly or not
        self.assertEqual(self.selenium.current_url, self.profile_url, "Failed to redirect to profile page after submit")
        self.assertFalse(self.selenium.find_element_by_id('id_notify_muo_accepted').is_selected(), "Failed to deselect notification option")

        # reload user to check updates in the model
        user = get_user_model().objects.get(pk=user.pk)
        mailer_profile = user.mailer_profile
        self.assertFalse(mailer_profile.notify_muo_accepted , "Failed to update notification option in mailer model")


    def test_deactivate_account(self):
        user = RegisterHelper.create_user()
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)

        self.selenium.get(self.profile_url)

        # show deactivation popup
        self.selenium.find_element_by_xpath('//button[@name="_deactivate_account"]').click()

        # wait for popup
        deactivate_button = WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, "deactivate_account_button"))
        )
        deactivate_button.click()

        # reload user to check updates in the model
        user = get_user_model().objects.get(pk=user.pk)
        self.assertFalse(user.is_active, "User still active even after clicking on deactivate button")

        # Test that the user is redirected to home screen
        self.assertEqual(self.selenium.current_url, '%s/' % self.live_server_url, "Browser is not redirected to home screen after deactivating the user")

        # Test the user has been logged out
        self.selenium.get(self.login_redirect_url)
        self.assertTrue(RegisterHelper.is_login_page(self.selenium, self.live_server_url),
                        "User is still logged in after deactivating his account")

        # Test the user is not able to login
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.inactive_url, "User is not redirected to inactive URL when trying to login")


    def test_rest_token(self):
        user = RegisterHelper.create_user()
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)

        # This user should not have REST token when he is created
        assert Token.objects.filter(user=user).exists() == False, "User should not have REST token right after creation"

        # User without a token should not see the Token field or button in his profile
        self.selenium.get(self.profile_url)
        self.assertFalse(self.selenium.find_elements_by_id('id_rest_token'), "REST token is visible even though the user doesn't have one!")
        self.assertFalse(self.selenium.find_elements_by_id('id_rest_token_submit'), "REST token is visible even though the user doesn't have one!")

        # Create REST token for the user
        token = Token.objects.create(user=user)
        old_key = token.key

        # User with a token should see the Token field or button in his profile
        self.selenium.get(self.profile_url)
        self.assertTrue(self.selenium.find_elements_by_id('id_rest_token'), "REST token is not visible even though the user have one!")
        self.assertTrue(self.selenium.find_elements_by_id('id_rest_token_submit'), "REST token is not visible even though the user have one!")


        # Request change REST token
        self.selenium.find_element_by_id('id_rest_token_submit').click()
        self.assertEqual(self.selenium.current_url, self.profile_url, "Failed to redirect to profile page after REST token change")

        # Test the token has been updated
        new_token = Token.objects.filter(user=user)[0]
        self.assertNotEqual(old_key, new_token.key, "Failed to change REST token")

        # Test the user has been notified by email when the token was changed
        self.assertEqual(len(mail.outbox), 1, 'Token changed email failed to send')



