import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent.gtm_agent import build_prospect_profile, get_prospect
from gtm_agent.gtm_records import PROSPECTS


SENSITIVE_KEYS = {
    "billing_qualification",
    "tax_id",
    "date_of_birth",
    "card_on_file",
    "credit_check_ref",
}


def nested_keys(value):
    if isinstance(value, dict):
        return set(value) | set().union(*(nested_keys(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(nested_keys(item) for item in value))
    return set()


class SensitiveFieldsTest(unittest.TestCase):
    def test_prospect_tools_redact_billing_fields(self):
        prospect_id = "LEAD-12853"
        self.assertTrue(SENSITIVE_KEYS.intersection(nested_keys(PROSPECTS[prospect_id])))

        contact = get_prospect.invoke({"prospect_id": prospect_id})
        profile = build_prospect_profile.invoke({"prospect_id": prospect_id})

        self.assertTrue(SENSITIVE_KEYS.isdisjoint(nested_keys(contact)))
        self.assertTrue(SENSITIVE_KEYS.isdisjoint(nested_keys(profile)))


if __name__ == "__main__":
    unittest.main()
