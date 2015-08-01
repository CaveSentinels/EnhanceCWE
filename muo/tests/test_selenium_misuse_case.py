from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from allauth.account.models import EmailAddress
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from EnhancedCWE.settings_travis import SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT
from register.tests import RegisterHelper
from cwe.models import CWE
from muo.models import MisuseCase
from muo.models import UseCase
from muo.models import MUOContainer
from muo.models import IssueReport


class MUOManagement(StaticLiveServerTestCase):

    # The URLs of the Misuse case related pages.
    PAGE_URL_MISUSE_CASE_HOME = "/app/muo/misusecase/"
    PAGE_URL_ISSUE_REPORT_HOME = "/app/muo/issuereport/"

    def setUp(self):
        # Create test data.
        self._set_up_test_data()
        # Create the admin.
        RegisterHelper.create_superuser()
        # Launch a browser.
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT)
        self.browser.maximize_window()
        # Log in.
        RegisterHelper.fill_login_form(
            selenium=self.browser,
            login_url="%s%s" % (self.live_server_url, reverse("account_login")),
            admin=True
        )
        RegisterHelper.submit_login_form(selenium=self.browser)

    def tearDown(self):
        # Delete test data.
        self._tear_down_test_data()
        # Call tearDown to close the web browser
        self.browser.quit()
        # Call the tearDown() of parent class.
        super(MUOManagement, self).tearDown()

    def _create_muo_and_misuse_case(self, cwes, muc_desc, custom):
        # Create the misuse case and establish the relationship with the CWEs
        misuse_case = MisuseCase(misuse_case_description=muc_desc)
        misuse_case.save()
        misuse_case.cwes.add(*cwes)  # Establish the relationship between the misuse case and CWEs

        # Create the MUO container for the misuse case and establish the relationship between the
        # MUO Container and CWEs
        muo_container = MUOContainer(is_custom=custom,
                                     status='draft',
                                     misuse_case=misuse_case
                                     )
        muo_container.save()
        muo_container.cwes.add(*cwes)   # Establish the relationship between the muo container and cwes

        return misuse_case, muo_container

    def _create_use_case_and_link_muo(self, index, muc, muo):
        uc = UseCase(use_case_description="Use Case "+str(index),
                     osr="Overlooked Security Requirement "+str(index)
                     )
        uc.muo_container = muo
        uc.misuse_case = muc
        uc.save()
        return uc

    def _approve_muo_container(self, muo_container):
        muo_container.action_submit()
        muo_container.action_approve()

    def _create_issue_report(self, desc, issue_type, uc):
        issue_report = IssueReport(description=desc, type=issue_type, usecase=uc)
        issue_report.save()

    def _set_up_test_data(self):
        # Create some CWEs.
        cwe101 = CWE(code=101)
        cwe101.save()
        # Create the MUO containers and misuse cases.
        muc1, muo1 = self._create_muo_and_misuse_case(
            cwes=[cwe101],
            muc_desc="Misuse Case 1",
            custom=False
        )
        # Create some use cases(with OSRs)
        uc1 = self._create_use_case_and_link_muo(1, muc1, muo1)
        # Approve some of the MUO containers.
        self._approve_muo_container(muo1)

        # Create an issue report.
        self._create_issue_report("Issue Report #1", "spam", uc1)

    def _tear_down_test_data(self):
        # Reject all the MUO containers before deleting them.
        for muo in MUOContainer.objects.all():
            if muo.status == 'approved':
                muo.action_reject(reject_reason="In order to delete the test data.")
        # Delete all the MUO containers.
        MUOContainer.objects.all().delete()
        # Delete all the misuse cases
        MisuseCase.objects.all().delete()
        # Delete all the CWEs.
        CWE.objects.all().delete()

        # Delete the issue report.
        IssueReport.objects.all().delete()

    def test_point_01(self):
        """
        Test Point: Verify that the "Usecase duplicate" input box can be displayed correctly.
            We do not need to go through the entire reporting duplicate process. We only need to
            verify that the input box is displayed.
        """
        # Open Page: "Misuse Case"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MISUSE_CASE_HOME))
        # Click Button: "Report Issue"
        self.browser.find_element_by_xpath("//a[@data-original-title='Report Issue']").click()
        # Select: "Duplicate"
        Select(webelement=self.browser.find_element_by_id("id_type")).select_by_visible_text("Duplicate")
        # Verify: "Usecase duplicate:" input box is shown.
        self.assertTrue(self.browser.find_element_by_id("id_usecase_duplicate-wrapper") is not None)
        # Click Button: "Close"
        self.browser.find_element_by_xpath("//button[@class='btn btn-default pull-left']").click()

    def test_regression_01(self):
        """
        Test Regression: Verify that the "Usecase duplicate" input box can be displayed after an issue
            state is changed.
        Defect ID: Unknown
        """
        # Change the status of the issue report.
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_ISSUE_REPORT_HOME))
        # Click Link: "Issue/00001"
        self.browser.find_element_by_link_text("Issue/00001").click()
        # Click Button: "Investigate"
        self.browser.find_element_by_name("_investigate").click()

        # Now go and verify that the "Usecase duplicate" input box can still be shown correctly.
        # Open Page: "Misuse Case"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MISUSE_CASE_HOME))
        # Click Button: "Report Issue"
        self.browser.find_element_by_xpath("//a[@data-original-title='Report Issue']").click()
        # Select: "Duplicate"
        Select(webelement=self.browser.find_element_by_id("id_type")).select_by_visible_text("Duplicate")
        # Verify: "Usecase duplicate:" input box is shown.
        self.assertTrue(self.browser.find_element_by_id("id_usecase_duplicate-wrapper") is not None)
        # Click Button: "Close"
        self.browser.find_element_by_xpath("//button[@class='btn btn-default pull-left']").click()

    def test_regression_02(self):
        """
        Test Point: Verify that the comment count is updated as a comment is posted.
        Defect ID: Unknown
        """
        # Open Page: "Misuse Case"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MISUSE_CASE_HOME))
        # Verify: 0 comment
        elm_comment_counter = self.browser.find_element_by_xpath(
            "id('content-main')/div/div[2]/div/div/div[3]/div/div[4]/div/a"
        )
        self.assertEqual(elm_comment_counter.get_attribute("textContent").strip(), "0 comments")
        # Enter Text: "Sample comment."
        self.browser.find_element_by_id("id_comment").send_keys("Sample comment.")
        self.browser.find_element_by_id("id_comment").submit()
        # Verify: 1 comment
        self.assertEqual(elm_comment_counter.get_attribute("textContent").strip(), "1 comments")

    def test_regression_03(self):
        """
        Test Point: When there is no misuse case, open the "Misuse Case" page should not
            pop up error message.
        """
        # To test this point, we should not have any misuse cases in the database, so we
        # just delete the test data.
        self._tear_down_test_data()
        # Open Page: "Misuse Case"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MISUSE_CASE_HOME))
        # Verify: No error alert box popped up.
        try:
            err_msg_box = self.browser.switch_to.alert
            err_msg_box.dismiss()
            no_err_msg_box = False
        except NoAlertPresentException:
            no_err_msg_box = True
        self.assertTrue(no_err_msg_box)


class MisuseCaseManagement(StaticLiveServerTestCase):

    def _create_user_admin(self):
        user_admin = get_user_model().objects.create(username="admin",
                                                     email="admin@example.com",
                                                     is_staff=True,
                                                     is_active=True,
                                                     is_superuser=True)
        user_admin.set_password("admin")
        user_admin.save()
        email_obj = EmailAddress.objects.create(user=user_admin,
                                                email="admin@example.com",
                                                primary=True,
                                                verified=True)

        if 'register_approval' in settings.INSTALLED_APPS:
            email_obj.admin_approval = 'approved'
        email_obj.save()

        return user_admin

    def _create_user_client(self):
        client = get_user_model().objects.create(username="client",
                                                 email="client@example.com",
                                                 is_staff=True,
                                                 is_active=True)
        client.set_password("client")
        client.save()

        email_obj = EmailAddress.objects.create(user=client,
                                                email="client@example.com",
                                                primary=True,
                                                verified=True)
        if 'register_approval' in settings.INSTALLED_APPS:
            email_obj.admin_approval = 'approved'
        email_obj.save()

        return client

    def _create_user_contributor(self):
        contributor = get_user_model().objects.create(username="contributor",
                                                      email="contributor@example.com",
                                                      is_staff=True,
                                                      is_active=True)
        contributor.set_password("contributor")
        contributor.save()

        email_obj = EmailAddress.objects.create(user=contributor,
                                                email="contributor@example.com",
                                                primary=True,
                                                verified=True)
        if 'register_approval' in settings.INSTALLED_APPS:
            email_obj.admin_approval = 'approved'
        email_obj.save()

        return contributor

    def _assign_permissions_contributor(self, user):
        ct_keyword = ContentType.objects.get(app_label="cwe", model="keyword")
        ct_category = ContentType.objects.get(app_label="cwe", model="category")
        ct_cwe = ContentType.objects.get(app_label="cwe", model="cwe")
        ct_misuse_case = ContentType.objects.get(app_label="muo", model="misusecase")
        ct_use_case = ContentType.objects.get(app_label="muo", model="usecase")
        ct_issue_report = ContentType.objects.get(app_label="muo", model="issuereport")
        ct_tag = ContentType.objects.get(app_label="muo", model="tag")
        ct_muo = ContentType.objects.get(app_label="muo", model="muocontainer")

        contributor_permissions = [
            Permission.objects.get(content_type=ct_keyword, codename="add_keyword"),
            Permission.objects.get(content_type=ct_keyword, codename="change_keyword"),
            Permission.objects.get(content_type=ct_keyword, codename="delete_keyword"),

            Permission.objects.get(content_type=ct_category, codename="view_category"),
            Permission.objects.get(content_type=ct_category, codename="delete_category"),
            Permission.objects.get(content_type=ct_category, codename="change_category"),
            Permission.objects.get(content_type=ct_category, codename="add_category"),

            Permission.objects.get(content_type=ct_cwe, codename="view_cwe"),
            Permission.objects.get(content_type=ct_cwe, codename="delete_cwe"),
            Permission.objects.get(content_type=ct_cwe, codename="change_cwe"),
            Permission.objects.get(content_type=ct_cwe, codename="add_cwe"),

            Permission.objects.get(content_type=ct_tag, codename="change_tag"),
            Permission.objects.get(content_type=ct_tag, codename="view_tag"),
            Permission.objects.get(content_type=ct_tag, codename="delete_tag"),
            Permission.objects.get(content_type=ct_tag, codename="change_tag"),

            Permission.objects.get(content_type=ct_misuse_case, codename="add_misusecase"),
            Permission.objects.get(content_type=ct_misuse_case, codename="change_misusecase"),
            Permission.objects.get(content_type=ct_misuse_case, codename="delete_misusecase"),

            Permission.objects.get(content_type=ct_use_case, codename="add_usecase"),
            Permission.objects.get(content_type=ct_use_case, codename="change_usecase"),
            Permission.objects.get(content_type=ct_use_case, codename="delete_usecase"),

            Permission.objects.get(content_type=ct_issue_report, codename="add_issuereport"),
            Permission.objects.get(content_type=ct_issue_report, codename="change_issuereport"),
            Permission.objects.get(content_type=ct_issue_report, codename="delete_issuereport"),

            Permission.objects.get(content_type=ct_muo, codename="can_view_all"),
            # Permission.objects.get(content_type=ct_muo, codename="can_reject"),
            Permission.objects.get(content_type=ct_muo, codename="delete_muocontainer"),
            Permission.objects.get(content_type=ct_muo, codename="can_edit_all"),
            Permission.objects.get(content_type=ct_muo, codename="change_muocontainer"),
            # Permission.objects.get(content_type=ct_muo, codename="can_approve"),
            Permission.objects.get(content_type=ct_muo, codename="add_muocontainer"),
        ]
        user.user_permissions.add(*contributor_permissions)

    def _set_up_basic_test_data(self):
        # Create two users.
        self.user_admin = self._create_user_admin()
        self.user_client = self._create_user_client()
        self.user_contributor = self._create_user_contributor()
        self._assign_permissions_contributor(self.user_contributor)

        # Create CWEs.
        self.cwe_auth = CWE.objects.create(code=1, name="authentication bypass")
        self.cwe_access = CWE.objects.create(code=2, name="file access denied")

    def _create_multiple_misuse_cases(self):
        # Create the misuse case and establish the relationship with the CWEs
        misuse_case_1 = MisuseCase.objects.create(
            misuse_case_description="Misuse case #1",
            misuse_case_primary_actor="Primary actor #1",
            misuse_case_secondary_actor="Secondary actor #1",
            misuse_case_precondition="Pre-condition #1",
            misuse_case_flow_of_events="Event flow #1",
            misuse_case_postcondition="Post-condition #1",
            misuse_case_assumption="Assumption #1",
            misuse_case_source="Source #1",
            created_by=self.user_admin
        )
        misuse_case_2 = MisuseCase.objects.create(
            misuse_case_description="Misuse case #2",
            misuse_case_primary_actor="Primary actor #2",
            misuse_case_secondary_actor="Secondary actor #2",
            misuse_case_precondition="Pre-condition #2",
            misuse_case_flow_of_events="Event flow #2",
            misuse_case_postcondition="Post-condition #2",
            misuse_case_assumption="Assumption #2",
            misuse_case_source="Source #2",
            created_by=self.user_contributor
        )
        misuse_case_3 = MisuseCase.objects.create(
            misuse_case_description="Misuse case #3",
            misuse_case_primary_actor="Primary actor #3",
            misuse_case_secondary_actor="Secondary actor #3",
            misuse_case_precondition="Pre-condition #3",
            misuse_case_flow_of_events="Event flow #3",
            misuse_case_postcondition="Post-condition #3",
            misuse_case_assumption="Assumption #3",
            misuse_case_source="Source #3",
            created_by=self.user_client
        )
        # Establish the relationship between the misuse case and CWEs
        misuse_case_1.cwes.add(self.cwe_auth)
        misuse_case_2.cwes.add(self.cwe_access)
        misuse_case_3.cwes.add(self.cwe_auth)

        # Create MUO containers.
        muo1 = MUOContainer.objects.create(is_custom=False,
                                           status='draft',
                                           misuse_case=misuse_case_1,
                                           misuse_case_type="existing"
                                           )
        muo2 = MUOContainer.objects.create(is_custom=False,
                                           status='draft',
                                           misuse_case=misuse_case_2,
                                           misuse_case_type="existing"
                                           )
        muo3 = MUOContainer.objects.create(is_custom=False,
                                           status='draft',
                                           misuse_case=misuse_case_3,
                                           misuse_case_type="existing"
                                           )

        # Create some use cases(with OSRs)
        uc_1_1 = UseCase.objects.create(
            use_case_description="Use Case #1-1",
            use_case_primary_actor="Primary actor #1-1",
            use_case_secondary_actor="Secondary actor #1-1",
            use_case_precondition="Pre-condition #1-1",
            use_case_flow_of_events="Event flow #1-1",
            use_case_postcondition="Post-condition #1-1",
            use_case_assumption="Assumption #1-1",
            use_case_source="Source #1-1",
            osr_pattern_type="ubiquitous",
            osr="Overlooked Security Requirement #1-1",
            muo_container=muo1,
            misuse_case=misuse_case_1
        )

        uc_1_2 = UseCase.objects.create(
            use_case_description="Use Case #1-2",
            use_case_primary_actor="Primary actor #1-2",
            use_case_secondary_actor="Secondary actor #1-2",
            use_case_precondition="Pre-condition #1-2",
            use_case_flow_of_events="Event flow #1-2",
            use_case_postcondition="Post-condition #1-2",
            use_case_assumption="Assumption #1-2",
            use_case_source="Source #1-2",
            osr_pattern_type="ubiquitous",
            osr="Overlooked Security Requirement #1-2",
            muo_container=muo1,
            misuse_case=misuse_case_1
        )

        uc2 = UseCase.objects.create(
            use_case_description="Use Case #2",
            use_case_primary_actor="Primary actor #2",
            use_case_secondary_actor="Secondary actor #2",
            use_case_precondition="Pre-condition #2",
            use_case_flow_of_events="Event flow #2",
            use_case_postcondition="Post-condition #2",
            use_case_assumption="Assumption #2",
            use_case_source="Source #2",
            osr_pattern_type="ubiquitous",
            osr="Overlooked Security Requirement #2",
            muo_container=muo2,
            misuse_case=misuse_case_2
        )

        uc3 = UseCase.objects.create(
            use_case_description="Use Case #3",
            use_case_primary_actor="Primary actor #3",
            use_case_secondary_actor="Secondary actor #3",
            use_case_precondition="Pre-condition #3",
            use_case_flow_of_events="Event flow #3",
            use_case_postcondition="Post-condition #3",
            use_case_assumption="Assumption #3",
            use_case_source="Source #3",
            osr_pattern_type="ubiquitous",
            osr="Overlooked Security Requirement #3",
            muo_container=muo3,
            misuse_case=misuse_case_3
        )

        # Approve the MUOs
        muo1.action_submit()
        muo1.action_approve()
        muo2.action_submit()
        muo2.action_approve()
        # muo3 is left not approved intentionally.

    def _is_element_present(self, by, value):
        try:
            expected_conditions.presence_of_element_located((by, value))(self.browser)
            return True
        except NoSuchElementException:
            return False

    def _are_elements_present(self, by, value):
        try:
            elements = self.browser.find_elements(by, value)
            return len(elements) > 0
        except NoSuchElementException:
            return False

    def _is_element_not_present(self, by, value):
        try:
            expected_conditions.presence_of_element_located((by, value))(self.browser)
            return False
        except NoSuchElementException:
            return True

    def _are_elements_not_present(self, by, value):
        try:
            elements = self.browser.find_elements(by, value)
            return len(elements) == 0
        except NoSuchElementException:
            return True

    def setUp(self):
        # Call the setUp() in parent class.
        super(MisuseCaseManagement, self).setUp()
        # Launch a browser.
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT)
        self.browser.maximize_window()
        # Create test data.
        self._set_up_basic_test_data()

    def tearDown(self):
        # Call tearDown to close the web browser
        self.browser.quit()
        # Call the tearDown() in parent class.
        super(MisuseCaseManagement, self).tearDown()

    def _log_in_as_admin(self):
        # Open the login page.
        login_url = "%s%s" % (self.live_server_url, reverse('account_login'))
        self.browser.get(login_url)

        # Fill login information
        self.browser.find_element_by_id("id_login").send_keys("admin")
        self.browser.find_element_by_id("id_password").send_keys("admin")
        # Log in
        self.browser.find_element_by_xpath('//button[@type="submit"][contains(text(), "Sign In")]').click()

    def _log_in_as_contributor(self):
        # Open the login page.
        login_url = "%s%s" % (self.live_server_url, reverse('account_login'))
        self.browser.get(login_url)

        # Fill login information
        self.browser.find_element_by_id("id_login").send_keys("contributor")
        self.browser.find_element_by_id("id_password").send_keys("contributor")
        # Log in
        self.browser.find_element_by_xpath('//button[@type="submit"][contains(text(), "Sign In")]').click()

    def _log_out(self):
        logout_url = "%s%s" % (self.live_server_url, reverse('account_logout'))
        self.browser.get(logout_url)
        self.browser.find_element_by_xpath("//input[@type='submit']").click()

    def test_without_log_in(self):
        """
        Test Point:
            1). The misuse case column shows all the misuse cases(approved) for all the users
            according to the selected CWEs.
            2). The misuse case information is displayed correctly.
            3). The use case column shows all the use cases associated with the currently
            selected misuse case.
            4). The comment-related and "Report Isuse" are not displayed.
        """
        # Create test data.
        self._create_multiple_misuse_cases()
        # Open the home page.
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Verify: The misuse case column shows all the misuse cases(approved) for all the users
        # according to the selected CWEs.
        misuse_cases = self.browser.find_elements_by_xpath("//div[@class='slim-scroll-div']/div")
        self.assertEqual(len(misuse_cases), 2)
        # Verify: The use case column shows all the use cases associated with the currently
        # selected misuse case.
        use_cases = self.browser.find_elements_by_xpath("//div[@class='fat-scroll-div']/div")
        self.assertEqual(len(use_cases), 2)
        # Verify: Comment-related controls are not displayed.
        self.assertTrue(self._is_element_not_present(By.XPATH, "//a[@href='#comments-block-1']"))
        self.assertTrue(self._is_element_not_present(By.ID, "id_comment"))
        self.assertTrue(self._are_elements_not_present(By.XPATH, "//div[@class='comment-item']"))
        # Verify: "Report Issue" is not displayed.
        self.assertTrue(self._are_elements_not_present(By.XPATH, "//a[@href='#muo-modal']"))

    def test_with_admin(self):
        """
        Test Point:
            1). The misuse case column shows all the misuse cases(approved) for all the users
            according to the selected CWEs.
            2). The misuse case information is displayed correctly.
            3). The use case column shows all the use cases associated with the currently
            selected misuse case.
            4). The comment-related and "Report Isuse" are displayed.
        """
        # Create test data.
        self._create_multiple_misuse_cases()
        # Log in as admin.
        self._log_in_as_admin()
        # Open the home page.
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Verify: The misuse case column shows all the misuse cases for all the users
        # according to the selected CWEs.
        misuse_cases = self.browser.find_elements_by_xpath("//div[@class='slim-scroll-div']/div")
        self.assertEqual(len(misuse_cases), 2)
        # Verify: The use case column shows all the use cases associated with the currently
        # selected misuse case.
        use_cases = self.browser.find_elements_by_xpath("//div[@class='fat-scroll-div']/div")
        self.assertEqual(len(use_cases), 2)
        # Verify: Comment-related controls are displayed.
        self.assertTrue(self._is_element_present(By.XPATH, "//a[@href='#comments-block-1']"))
        self.assertTrue(self._is_element_present(By.ID, "id_comment"))
        # Verify: "Report Issue" is displayed.
        self.assertTrue(self._are_elements_present(By.XPATH, "//a[@href='#muo-modal']"))

    def test_comments(self):
        """
        Test Point:
            1). One user cannot delete the commnets by another user.
            2). Admin can delete everyone's comment.
        """
        import time
        # Create test data.
        self._create_multiple_misuse_cases()
        # Log in as contributor.
        self._log_in_as_admin()
        # Open the home page.
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Verify: The misuse case column shows all the misuse cases for all the users
        # according to the selected CWEs.
        misuse_cases = self.browser.find_elements_by_xpath("//div[@class='slim-scroll-div']/div")
        self.assertEqual(len(misuse_cases), 2)
        # Verify: The use case column shows all the use cases associated with the currently
        # selected misuse case.
        use_cases = self.browser.find_elements_by_xpath("//div[@class='fat-scroll-div']/div")
        self.assertEqual(len(use_cases), 2)
        # Verify: Comments can be added.
        # Append comments.
        comment_area = self.browser.find_element_by_xpath(
            "//div[@class='fat-scroll-div']/div[position()=1]/div[@class='comments-container']/div/form/textarea"
        )
        comment_area.send_keys("comment-1\n")
        comment_area.submit()
        time.sleep(5)   # Need to wait for a while to make sure the comments really go in.
        comment_area.send_keys("comment-2\n")
        comment_area.submit()
        # Check the comments.
        time.sleep(5)   # Need to wait for a while to make sure the comments really go in.
        comment_items = self.browser.find_elements_by_xpath("//div[@class='comment-item']")
        self.assertEqual(len(comment_items), 2)
        self.assertTrue(self._is_element_present(By.ID, "id_comment"))
        # Verify: "Report Issue" is displayed.
        self.assertTrue(self._are_elements_present(By.XPATH, "//a[@href='#muo-modal']"))

        # Log out.
        self._log_out()
        time.sleep(5)

        # Log in as contributor
        self._log_in_as_contributor()
        time.sleep(5)
        # Open the home page.
        self.browser.get(self.live_server_url)
        time.sleep(5)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()
        # The contributor can see admin's comments, but cannot delete them.
        comment_items = self.browser.find_elements_by_xpath("//div[@class='comment-item']")
        self.assertEqual(len(comment_items), 2)
        # There should be no "Delete".
        self._are_elements_not_present(By.XPATH, "//a[@class='delete-comment']")

        # Log out
        # TODO: Fix the test cases.