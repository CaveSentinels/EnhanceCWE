from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.select import Select
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
