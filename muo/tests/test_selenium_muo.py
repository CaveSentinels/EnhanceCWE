from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from EnhancedCWE.settings_travis import SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT
from register.tests import RegisterHelper
from cwe.models import CWE
from muo.models import UseCase
from muo.models import MisuseCase
from muo.models import MUOContainer
from muo.models import IssueReport


class MUOTestBase(StaticLiveServerTestCase):

    # The URLs of the CWE-related pages.
    PAGE_URL_MUO_HOME = "/app/muo/muocontainer/"

    def setUp(self):
        # Call the setUp() of parent class.
        super(MUOTestBase, self).setUp()
        # Launch a browser.
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT)
        self.browser.maximize_window()
        # Create test data.
        self._set_up_test_data()
        # Create the user.
        user = RegisterHelper.create_user()
        # Assign user's permissions.
        self._assign_user_permissions(user)

    def tearDown(self):
        # Create test data.
        self._tear_down_test_data()
        # Call tearDown to close the web browser.
        self.browser.quit()

        # Call the tearDown() of parent class.
        super(MUOTestBase, self).tearDown()

    def _set_up_test_data(self):
        # Create some CWEs. These CWEs will be used by all the test methods.
        cwe101 = CWE(code=101, name="101")
        cwe101.save()

    def _tear_down_test_data(self):
        # Reject all the MUO containers before deleting them.
        for muo in MUOContainer.objects.all():
            if muo.status != 'draft' and muo.status != 'rejected':
                muo.action_reject(reject_reason="In order to delete the test data.")
        # Delete all the MUO containers.
        MUOContainer.objects.all().delete()
        # Delete all the misuse cases
        MisuseCase.objects.all().delete()
        # Delete all the CWEs.
        CWE.objects.all().delete()
        # Delete the issue report.
        IssueReport.objects.all().delete()

    def _assign_user_permissions(self, user):
        # Empty.
        pass

    def _create_draft_muo(self, muc_type):
        cwe101 = CWE.objects.get(code=101)

        # Create the misuse case and establish the relationship with the CWEs
        misuse_case = MisuseCase(
            misuse_case_description="Misuse case #1",
            misuse_case_primary_actor="Primary actor #1",
            misuse_case_secondary_actor="Secondary actor #1",
            misuse_case_precondition="Pre-condition #1",
            misuse_case_flow_of_events="Event flow #1",
            misuse_case_postcondition="Post-condition #1",
            misuse_case_assumption="Assumption #1",
            misuse_case_source="Source #1"
        )
        misuse_case.save()
        misuse_case.cwes.add(cwe101)  # Establish the relationship between the misuse case and CWEs

        # Create the MUO container for the misuse case and establish the relationship between the
        # MUO Container and CWEs.
        muo_container = MUOContainer(is_custom=False,
                                     status='draft',
                                     misuse_case=misuse_case,
                                     misuse_case_type=muc_type
                                     )
        muo_container.save()
        muo_container.cwes.add(cwe101)   # Establish the relationship between the muo container and cwes

        # Create some use cases(with OSRs)
        uc = UseCase(
            use_case_description="Use Case #1",
            use_case_primary_actor="Primary actor #1",
            use_case_secondary_actor="Secondary actor #1",
            use_case_precondition="Pre-condition #1",
            use_case_flow_of_events="Event flow #1",
            use_case_postcondition="Post-condition #1",
            use_case_assumption="Assumption #1",
            use_case_source="Source #1",
            osr_pattern_type="ubiquitous",
            osr="Overlooked Security Requirement #1"
        )
        uc.muo_container = muo_container
        uc.misuse_case = misuse_case
        uc.save()

        return muo_container

    def _create_draft_muo_after_rejection(self, muc_type):
        muo1 = self._create_draft_muo(muc_type=muc_type)
        # Submit the MUO
        muo1.action_submit()
        # Reject the MUO
        muo1.action_reject(reject_reason="For testing purpose.")
        # Reopen the MUO
        muo1.action_save_in_draft()

    def _create_in_review_muo(self, muc_type):
        muo1 = self._create_draft_muo(muc_type=muc_type)
        # Submit the MUO
        muo1.action_submit()

    def _create_in_review_muo_after_rejection(self, muc_type):
        muo1 = self._create_draft_muo(muc_type=muc_type)
        # Submit the MUO
        muo1.action_submit()
        # Reject the MUO
        muo1.action_reject(reject_reason="For testing purpose.")
        # Reopen the MUO
        muo1.action_save_in_draft()
        # Submit the MUO again.
        muo1.action_submit()

    def _create_rejected_muo(self, muc_type):
        muo1 = self._create_draft_muo(muc_type=muc_type)
        # Submit the MUO
        muo1.action_submit()
        # Reject the MUO
        muo1.action_reject(reject_reason="For testing purpose.")

    def _create_approved_muo(self, muc_type):
        muo1 = self._create_draft_muo(muc_type=muc_type)
        # Submit the MUO
        muo1.action_submit()
        # Approve the MUO
        muo1.action_approve()

    def _is_editable(self, web_element):
        old_text = web_element.get_attribute("value")
        web_element.send_keys("test")
        new_text = web_element.get_attribute("value")
        web_element.clear()
        web_element.send_keys(old_text)     # Resume to the previous text
        return old_text != new_text

    def _verify_muo_fields_info(self, expected_status):
        fields = self.browser.find_elements_by_xpath("//fieldset[@id='fieldset-1']/div/div/div/div/div/p")
        # Name
        # self.assertEqual(fields[0].get_attribute("textContent"), "MUO/00001")
        # Cwes
        self.assertEqual(fields[1].get_attribute("textContent"), "CWE-101: 101")
        # Misuse Case Type
        self.assertEqual(fields[2].get_attribute("textContent"), "Existing")
        # Misuse case
        # The misuse case name is dependent on its ID. However, when we run the entire test suite
        # or run the test method individually, the database IDs are different, which means the test
        # case may fail when you use different ways to run it. Therefore, for now we do not test it.
        # self.assertEqual(fields[3].get_attribute("textContent"), "MU/00001 - Misuse Case #1...")
        # Brief Description
        self.assertEqual(fields[4].get_attribute("textContent"), "Misuse case #1")
        # Primary actor
        self.assertEqual(fields[5].get_attribute("textContent"), "Primary actor #1")
        # Secondary actor
        self.assertEqual(fields[6].get_attribute("textContent"), "Secondary actor #1")
        # Pre-condition
        self.assertEqual(fields[7].get_attribute("textContent"), "Pre-condition #1")
        # Flow of events
        self.assertEqual(fields[8].get_attribute("textContent"), "Event flow #1")
        # Post-condition
        self.assertEqual(fields[9].get_attribute("textContent"), "Post-condition #1")
        # Assumption
        self.assertEqual(fields[10].get_attribute("textContent"), "Assumption #1")
        # Source
        self.assertEqual(fields[11].get_attribute("textContent"), "Source #1")
        # Status
        self.assertEqual(fields[12].get_attribute("textContent"), expected_status)

    def _verify_use_case_fields_info(self):
        fields = self.browser.find_elements_by_xpath("//fieldset[@id='fieldset-1-1']/div/div/div/div/div/p")
        # Name
        # self.assertEqual(fields[0].get_attribute("textContent"), "UC/00001")
        # Brief description
        self.assertEqual(fields[1].get_attribute("textContent"), "Use Case #1")
        # Primary actor
        self.assertEqual(fields[2].get_attribute("textContent"), "Primary actor #1")
        # Secondary actor
        self.assertEqual(fields[3].get_attribute("textContent"), "Secondary actor #1")
        # Pre-condition
        self.assertEqual(fields[4].get_attribute("textContent"), "Pre-condition #1")
        # Flow of events
        self.assertEqual(fields[5].get_attribute("textContent"), "Event flow #1")
        # Post-condition
        self.assertEqual(fields[6].get_attribute("textContent"), "Post-condition #1")
        # Assumption
        self.assertEqual(fields[7].get_attribute("textContent"), "Assumption #1")
        # Source
        self.assertEqual(fields[8].get_attribute("textContent"), "Source #1")
        # Overlooked security requirements pattern type
        self.assertEqual(fields[9].get_attribute("textContent"), "Ubiquitous")
        # Overlooked security requirements
        self.assertEqual(fields[10].get_attribute("textContent"), "Overlooked Security Requirement #1")

    def _verify_misuse_case_fields_are_editable(self):
        muc_field_id_list = [
            "id_misuse_case_description",
            "id_misuse_case_primary_actor",
            "id_misuse_case_secondary_actor",
            "id_misuse_case_precondition",
            "id_misuse_case_flow_of_events",
            "id_misuse_case_postcondition",
            "id_misuse_case_assumption",
            "id_misuse_case_source"
        ]
        for field_id in muc_field_id_list:
            elm_field = self.browser.find_element_by_id(field_id)
            self.assertTrue(self._is_editable(elm_field), "Field '" + field_id + "' is not editable.")
        # Verify: The "Misuse case" auto-completion box for using existing misuse case is not visible.
        self.assertEqual(self.browser.find_element_by_id("id_misuse_case-wrapper").is_displayed(), False)

    def _verify_misuse_case_fields_are_hidden(self):
        muc_field_id_list = [
            "id_misuse_case_description",
            "id_misuse_case_primary_actor",
            "id_misuse_case_secondary_actor",
            "id_misuse_case_precondition",
            "id_misuse_case_flow_of_events",
            "id_misuse_case_postcondition",
            "id_misuse_case_assumption",
            "id_misuse_case_source"
        ]
        for field_id in muc_field_id_list:
            elm_field = self.browser.find_element_by_id(field_id)
            self.assertEqual(elm_field.is_displayed(), False, "Field '" + field_id + "' is visible.")
        # Verify: The "Misuse case" auto-completion box for using existing misuse case is visible.
        self.assertEqual(self.browser.find_element_by_id("id_misuse_case-wrapper").is_displayed(), True)

    def _verify_use_case_fields_are_editable(self):
        uc_field_id_list = [
            "id_usecase_set-0-use_case_description",
            "id_usecase_set-0-use_case_primary_actor",
            "id_usecase_set-0-use_case_secondary_actor",
            "id_usecase_set-0-use_case_precondition",
            "id_usecase_set-0-use_case_flow_of_events",
            "id_usecase_set-0-use_case_postcondition",
            "id_usecase_set-0-use_case_assumption",
            "id_usecase_set-0-use_case_source",
            "id_usecase_set-0-osr"
        ]
        for field_id in uc_field_id_list:
            elm_field = self.browser.find_element_by_id(field_id)
            self.assertTrue(self._is_editable(elm_field), "Field '" + field_id + "' is not editable.")
        # Verify: Option box works correctly.
        elm_options = self.browser.find_elements_by_xpath("//select[@id='id_usecase_set-0-osr_pattern_type']/option")
        self.assertEqual(elm_options[0].get_attribute("textContent"), "Ubiquitous")
        self.assertEqual(elm_options[1].get_attribute("textContent"), "Event-Driven")
        self.assertEqual(elm_options[2].get_attribute("textContent"), "Unwanted Behavior")
        self.assertEqual(elm_options[3].get_attribute("textContent"), "State-Driven")
        self.assertEqual(elm_options[0].get_attribute("selected"), "true")

    def _test_point_06_ui_approved(self):
        """
        Test Point: Verify that the MUO container page in 'Approved' status works as expected.
        """

        # Create test data
        self._create_approved_muo(muc_type="existing")
        # Open Page: "MUO Containers"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))
        # Click Link: MUO
        self.browser.find_element_by_xpath("id('result_list')/tbody/tr/th/a").click()

        # Verify: The information of the MUO is displayed correctly.
        self._verify_muo_fields_info("Approved")

        # Verify: The information of the Use Cases is displayed correctly.
        self._verify_use_case_fields_info()


class MUOReviewerTest(MUOTestBase):

    def setUp(self):
        # Call the setUp() of parent class.
        super(MUOReviewerTest, self).setUp()
        # Log in.
        RegisterHelper.fill_login_form(
            selenium=self.browser,
            login_url="%s%s" % (self.live_server_url, reverse("account_login")),
            admin=False
        )
        RegisterHelper.submit_login_form(selenium=self.browser)

    def _assign_user_permissions(self, user):
        ct_keyword = ContentType.objects.get(app_label="cwe", model="keyword")
        ct_category = ContentType.objects.get(app_label="cwe", model="category")
        ct_cwe = ContentType.objects.get(app_label="cwe", model="cwe")
        ct_misuse_case = ContentType.objects.get(app_label="muo", model="misusecase")
        ct_use_case = ContentType.objects.get(app_label="muo", model="usecase")
        ct_issue_report = ContentType.objects.get(app_label="muo", model="issuereport")
        ct_tag = ContentType.objects.get(app_label="muo", model="tag")
        ct_muo = ContentType.objects.get(app_label="muo", model="muocontainer")

        reviewer_permissions = [
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
            Permission.objects.get(content_type=ct_muo, codename="can_reject"),
            # Permission.objects.get(content_type=ct_muo, codename="delete_muocontainer"),
            # Permission.objects.get(content_type=ct_muo, codename="can_edit_all"),
            Permission.objects.get(content_type=ct_muo, codename="change_muocontainer"),
            Permission.objects.get(content_type=ct_muo, codename="can_approve"),
            # Permission.objects.get(content_type=ct_muo, codename="add_muocontainer"),
        ]
        user.user_permissions.add(*reviewer_permissions)

    def test_point_02_ui_in_review(self):
        """
        Test Point: Verify that the MUO container page in 'In Review' status works as expected.
        """

        # Create test data
        self._create_in_review_muo(muc_type="existing")
        # Open Page: "MUO Containers"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))

        # Click Link: MUO
        self.browser.find_element_by_xpath("id('result_list')/tbody/tr/th/a").click()

        # Verify: The information of the MUO is displayed correctly.
        self._verify_muo_fields_info("In Review")

        # Verify: The information of the Use Cases is displayed correctly.
        self._verify_use_case_fields_info()

    def test_point_05_ui_in_review_after_rejection(self):
        """
        Test Point: Verify that the MUO container page in 'In Review' status but which was
            previously rejected works as expected.
        """

        # Create test data
        self._create_in_review_muo_after_rejection(muc_type="existing")
        # Open Page: "MUO Containers"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))
        # Click Link: MUO
        self.browser.find_element_by_xpath("id('result_list')/tbody/tr/th/a").click()

        # Verify: The "This MUO used to be rejected" message is shown.
        expected_conditions.presence_of_element_located(
            (By.XPATH, "//div[@class='alert alert-warning']")
        )(self.browser)

        # Verify: The information of the MUO is displayed correctly.
        self._verify_muo_fields_info("In Review")

        # Verify: The information of the Use Cases is displayed correctly.
        self._verify_use_case_fields_info()

    def test_point_06_ui_approved(self):
        self._test_point_06_ui_approved()


class MUOContributorTest(MUOTestBase):

    def setUp(self):
        # Call the setUp() of parent class.
        super(MUOContributorTest, self).setUp()

        # Log in.
        RegisterHelper.fill_login_form(
            selenium=self.browser,
            login_url="%s%s" % (self.live_server_url, reverse("account_login")),
            admin=False
        )
        RegisterHelper.submit_login_form(selenium=self.browser)

    def _assign_user_permissions(self, user):
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

    def test_point_01_ui_draft(self):
        """
        Test Point: Verify that the MUO container page in 'Draft' status works as expected.
        """

        # Create test data
        self._create_draft_muo(muc_type="new")
        # Open Page: "MUO Containers"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))
        # Click Link: MUO
        self.browser.find_element_by_xpath("id('result_list')/tbody/tr/th/a").click()

        # Verify: The UI elements are in the correct states.
        # CWE auto-complete edit box is editable.
        # FIXME: How to verify if an auto-completion edit box is editable or not??
        # elm_cwe_auto_complete = self.browser.find_element_by_id("id_cwes-autocomplete")
        # self.assertTrue(self._is_editable(elm_cwe_auto_complete))
        # "New" option is checked
        elm_muc_type_existing = self.browser.find_element_by_xpath(
            "//select[@id='id_misuse_case_type']/option[position()=1]"
        )
        self.assertEqual(elm_muc_type_existing.get_attribute("selected"), None)
        elm_muc_type_new = self.browser.find_element_by_xpath(
            "//select[@id='id_misuse_case_type']/option[position()=2]"
        )
        self.assertEqual(elm_muc_type_new.get_attribute("selected"), "true")

        # Verify: The misuse case fields are editable.
        self._verify_misuse_case_fields_are_editable()

        # Verify: Status shows "Draft".
        elm_status = self.browser.find_element_by_xpath(
            "//fieldset[@id='fieldset-1']/div/div[position()=13]/div/div/div/p"
        )
        self.assertEqual(elm_status.get_attribute("textContent"), "Draft")

        # Verify: The use case fields are editable.
        self._verify_use_case_fields_are_editable()

        # Now select the "Existing misuse case"
        sel_muc_type = Select(self.browser.find_element_by_id("id_misuse_case_type"))
        sel_muc_type.select_by_visible_text("Existing")

        # Verify: The misuse case fields are now hidden.
        self._verify_misuse_case_fields_are_hidden()

        # Verify: The "Misuse case" auto-completion box for using existing misuse case is visible.
        self.assertTrue(self.browser.find_element_by_id("id_misuse_case-wrapper").is_displayed())

    def test_point_03_ui_rejected(self):
        """
        Test Point: Verify that the MUO container page in 'Rejected' status works as expected.
        """

        # Create test data
        self._create_rejected_muo(muc_type="existing")
        # Open Page: "MUO Containers"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))
        # Click Link: MUO
        self.browser.find_element_by_xpath("id('result_list')/tbody/tr/th/a").click()

        # Verify: The "This MUO has been rejected" message is shown.
        expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='alert alert-error']"))(self.browser)

        # Verify: The information of the MUO is displayed correctly.
        self._verify_muo_fields_info("Rejected")

        # Verify: The information of the Use Cases is displayed correctly.
        self._verify_use_case_fields_info()

    def test_point_04_ui_draft_after_rejection(self):
        """
        Test Point: Verify that the MUO container page in 'Draft' status but which was
            previously rejected works as expected.
        """

        # Create test data
        self._create_draft_muo_after_rejection(muc_type="existing")
        # Open Page: "MUO Containers"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))
        # Click Link: MUO
        self.browser.find_element_by_xpath("id('result_list')/tbody/tr/th/a").click()

        # Verify: The "This MUO used to be rejected" message is shown.
        expected_conditions.presence_of_element_located(
            (By.XPATH, "//div[@class='alert alert-warning']")
        )(self.browser)

        # Verify: The UI elements are in the correct states.
        # CWE auto-complete edit box is editable.
        # FIXME: How to verify if an auto-completion edit box is editable or not??
        # elm_cwe_auto_complete = self.browser.find_element_by_id("id_cwes-autocomplete")
        # self.assertTrue(self._is_editable(elm_cwe_auto_complete))
        # "New" option is checked
        elm_muc_type_existing = self.browser.find_element_by_xpath(
            "//select[@id='id_misuse_case_type']/option[position()=1]"
        )
        self.assertEqual(elm_muc_type_existing.get_attribute("selected"), "true")
        elm_muc_type_new = self.browser.find_element_by_xpath(
            "//select[@id='id_misuse_case_type']/option[position()=2]"
        )
        self.assertEqual(elm_muc_type_new.get_attribute("selected"), None)

        # Verify: The misuse case fields are hidden.
        self._verify_misuse_case_fields_are_hidden()

        # Verify: The "Misuse case" auto-completion box for using existing misuse case is not visible.
        self.assertEqual(self.browser.find_element_by_id("id_misuse_case-wrapper").is_displayed(), False)

        # Verify: Status shows "Draft".
        elm_status = self.browser.find_element_by_xpath(
            "//fieldset[@id='fieldset-1']/div/div[position()=13]/div/div/div/p"
        )
        self.assertEqual(elm_status.get_attribute("textContent"), "Draft")

        # Verify: The use case fields are editable.
        self._verify_use_case_fields_are_editable()

        # Now select the "Existing misuse case"
        sel_muc_type = Select(self.browser.find_element_by_id("id_misuse_case_type"))
        sel_muc_type.select_by_visible_text("New")

        # Verify: The misuse case fields are now displayed and editable.
        self._verify_misuse_case_fields_are_editable()

    def test_point_06_ui_approved(self):
        self._test_point_06_ui_approved()