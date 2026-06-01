import unittest

from data.data_loader import load_all_data
from services.project_service import get_project_related_data
from services.risk_service import calculate_project_risk, get_high_risk_projects


class RiskServiceTest(unittest.TestCase):
    def test_project_risk_output(self):
        project = load_all_data()["projects"].iloc[0].to_dict()
        related = get_project_related_data(project["id"])
        result = calculate_project_risk(project, related)
        self.assertIn("risk_score", result)
        self.assertIn(result["risk_level"], ["低", "中", "高", "严重"])

    def test_high_risk_projects(self):
        result = get_high_risk_projects(5)
        self.assertLessEqual(len(result), 5)


if __name__ == "__main__":
    unittest.main()

