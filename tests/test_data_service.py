import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class UpdateProspectInfoTest(unittest.TestCase):
    def setUp(self):
        self.original_tech_stack = list(data_service.PROSPECTS["LEAD-71001"]["tech_stack"])
        data_service._PROFILES.pop("LEAD-71001", None)

    def tearDown(self):
        data_service.PROSPECTS["LEAD-71001"]["tech_stack"] = self.original_tech_stack
        data_service._PROFILES.pop("LEAD-71001", None)

    def test_update_persists_and_invalidates_cached_profile(self):
        build_prospect_profile.invoke({"prospect_id": "LEAD-71001"})

        result = data_service.update_prospect_info("LEAD-71001", "Kafka")

        self.assertTrue(result["updated"])
        self.assertIn("Kafka", data_service.fetch_tech_stack("LEAD-71001"))
        rebuilt = build_prospect_profile.invoke({"prospect_id": "LEAD-71001"})
        self.assertIn("Kafka", rebuilt["prospect_profile"]["tech_stack"])


if __name__ == "__main__":
    unittest.main()
