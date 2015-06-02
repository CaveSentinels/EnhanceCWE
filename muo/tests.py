from django.test import TestCase

from muo.models import MUOContainer, MisuseCase, UseCase, OSR
from cwe.models import CWE

# Create your tests here.

class TestMUOContainer(TestCase):

    def test_positive_approve_muo(self):
        muoc = MUOContainer()
        muoc.status = "in_review"
        muoc.published_status = "unpublished"
        muoc.save()

        muoc.action_approve()
        muoc = MUOContainer.objects.first()
        self.assertEqual(muoc.status, "approved")
        self.assertEqual(muoc.published_status, "published")

    def test_negative_approve_muo(self):
        muoc = MUOContainer()
        muoc.status = "draft"
        muoc.published_status = "published"
        muoc.save()

        self.assertRaises(ValueError, muoc.action_approve)

    def test_positive_reject_muo(self):
        muoc = MUOContainer()
        muoc.status = "approved"
        muoc.save()

        muoc.action_reject()
        muoc = MUOContainer.objects.first()
        self.assertEqual(muoc.status, "rejected")

    def test_negative_reject_muo(self):
        muoc = MUOContainer()
        muoc.status = "draft"
        muoc.published_status = "published"
        muoc.save()

        self.assertRaises(ValueError, muoc.action_reject)

    def test_positive_submit_muo(self):
        muoc = MUOContainer()
        muoc.status = "draft"
        muoc.save()

        muoc.action_submit()
        self.assertEqual(muoc.status, "in_review")

    def test_negative_submit_muo(self):
        muoc = MUOContainer()
        muoc.status = "approved"
        muoc.save()

        self.assertRaises(ValueError, muoc.action_submit)

    def test_positive_save_in_draft_muo(self):
        muoc = MUOContainer()
        muoc.status = "rejected"
        muoc.save()

        muoc.action_save_in_draft()
        self.assertEqual(muoc.status, "draft")

    def test_negative_save_in_draft_muo(self):
        muoc = MUOContainer()
        muoc.status = "draft"
        muoc.save()

        self.assertRaises(ValueError, muoc.action_save_in_draft)

    def test_positive_publish_muo(self):
        muoc = MUOContainer()
        muoc.status = "approved"
        muoc.published_status = "unpublished"
        muoc.save()

        muoc.action_publish()
        self.assertEqual(muoc.published_status, "published")

    def test_negative_publish_muo(self):
        muoc = MUOContainer()
        muoc.status = "draft"
        muoc.published_status = "published"
        muoc.save()

        self.assertRaises(ValueError, muoc.action_publish)

    def test_positive_unpublish_muo(self):
        muoc = MUOContainer()
        muoc.published_status = "published"
        muoc.save()

        muoc.action_unpublish()
        self.assertEqual(muoc.published_status, "unpublished")

    def test_negative_unpublish_muo(self):
        muoc = MUOContainer()
        muoc.published_status = "unpublished"
        muoc.save()

        self.assertRaises(ValueError, muoc.action_unpublish)