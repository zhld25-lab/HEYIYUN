import unittest

from data.data_loader import load_all_data
from services.project_service import calculate_project_health_score, get_project_related_data, get_project_summary


class ProjectServiceTest(unittest.TestCase):
    def test_project_summary_counts(self):
        summary = get_project_summary()
        self.assertGreaterEqual(summary["project_count"], 20)
        self.assertGreater(summary["contract_amount"], 0)

    def test_health_score_range(self):
        project = load_all_data()["projects"].iloc[0].to_dict()
        related = get_project_related_data(project["id"])
        result = calculate_project_health_score(project, related)
        self.assertGreaterEqual(result["health_score"], 0)
        self.assertLessEqual(result["health_score"], 100)


if __name__ == "__main__":
    unittest.main()

