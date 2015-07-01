from django.test import TestCase
from django.core.exceptions import ValidationError
from muo.models import MUOContainer, MisuseCase, UseCase, IssueReport
from django.contrib.auth.models import User

class TestIssueReport(TestCase):

    def setUp(self):
        """
        This method does the general setup needed for the test methods.
        For now it just creates a MUOContainer object and an issue report on that MUO Container
        """
        self.reviewer = User(username='reviewer')
        self.reviewer.save()
        misuse_case = MisuseCase()
        misuse_case.save()
        muo_container = MUOContainer.objects.create(misuse_case = misuse_case)
        muo_container.save()
        muo_container.status = 'in_review'
        muo_container.save()
        muo_container.action_approve()
        use_case = UseCase(muo_container=muo_container)
        use_case.save()  # save in the database
        issue_report = IssueReport.objects.create(name="issue001", description="this is the issue", type="spam",
                                                  status="open", usecase=use_case)
        self.current_id = issue_report.id
        issue_report.save()

    def get_issue_report(self, status):
        """
        This method sets the status of the Issue Report object with the one
        received in arguments.
        """
        issue_report = IssueReport.objects.get(pk=self.current_id)
        issue_report.status = status
        issue_report.save()
        return issue_report

    def test_action_investigate(self):
        """
        This method checks if the state gets changed to investigating or not
        """
        issue_report = self.get_issue_report("open")
        issue_report.action_investigate(reviewer=self.reviewer)
        self.assertEqual(issue_report.status, 'investigating')

    def test_action_resolve(self):
        """
        This method checks if the state gets changed to resolved
        """
        resolve_reason = "This issue is resolved"
        issue_report = self.get_issue_report("investigating")
        issue_report.action_resolve(reviewer = self.reviewer, resolve_reason=resolve_reason)
        self.assertEqual(issue_report.status,'resolved')

    def test_action_reopen(self):
        """
        This method checks if the state gets changed to re-open or not
        """
        issue_report = self.get_issue_report("investigating")
        issue_report.action_open(reviewer=self.reviewer)
        self.assertEqual(issue_report.status,'open')
        issue_report = self.get_issue_report("resolved")
        issue_report.action_reopen(reviewer=self.reviewer)
        self.assertEqual(issue_report.status,'reopen')

    def test_action_investigate_negative(self):
        """
        This is a negative test case which tries to see if action_investigate method is called when the state is investigate
        It should throw an error
        """

        issue_report = self.get_issue_report("investigating")
        self.assertRaises(ValueError, issue_report.action_investigate)

    def test_action_resolve_negative(self):
        """
        This is a negative test case which tries to see if action_resolve method is called when the state is open
        It should throw an error
        """
        issue_report = self.get_issue_report("open")
        resolve_reason = "This is an issue"
        self.assertRaises(ValueError, issue_report.action_resolve,resolve_reason)

    def test_action_reopen_negative(self):
        """
        This is a negative test case which tries to see if action_reopen method is called when the state is open
        It should throw an error
        """
        issue_report = self.get_issue_report("open")
        self.assertRaises(ValueError, issue_report.action_reopen)

















