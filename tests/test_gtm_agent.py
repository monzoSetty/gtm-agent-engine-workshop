import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import gtm_agent


class SendProspectEmailTests(unittest.TestCase):
    runtime = SimpleNamespace(config={"metadata": {"user_id": "rep_rgarcia"}})

    def test_disqualified_prospect_is_blocked_before_message_creation(self):
        prospect = {
            "prospect_id": "LEAD-50005",
            "name": "Mei Lin",
            "email": "mei.lin@harborviewretail.com",
        }

        with patch.object(
            gtm_agent.data_service,
            "get_prospect_record",
            return_value={"disqualified": True},
        ) as get_record, patch.object(gtm_agent.uuid, "uuid4") as uuid4:
            result = gtm_agent.send_prospect_email.func(
                prospect,
                "Availability",
                "Hello",
                self.runtime,
            )

        self.assertEqual(
            result,
            {
                "status": "blocked",
                "error": "Prospect is flagged disqualified; send not permitted without rep confirmation.",
                "prospect_id": "LEAD-50005",
            },
        )
        get_record.assert_called_once_with("LEAD-50005")
        uuid4.assert_not_called()

    def test_qualified_prospect_is_sent(self):
        prospect = {
            "prospect_id": "LEAD-60001",
            "name": "Jordan Lee",
            "email": "jordan.lee@example.com",
        }

        with patch.object(
            gtm_agent.data_service,
            "get_prospect_record",
            return_value={"disqualified": False},
        ), patch.object(gtm_agent.uuid, "uuid4", return_value=SimpleNamespace(hex="a" * 12)):
            result = gtm_agent.send_prospect_email.func(
                prospect,
                "Availability",
                "Hello",
                self.runtime,
            )

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["message_id"], "msg-" + "a" * 12)
        self.assertEqual(result["to"], "jordan.lee@example.com")


if __name__ == "__main__":
    unittest.main()
