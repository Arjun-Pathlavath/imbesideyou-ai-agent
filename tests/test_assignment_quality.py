
import sys
import unittest
from pathlib import Path

ASSIGNMENT_SRC = Path(
    r"C:\Users\pathl\Desktop\imbesideyou-assignment\src"
)
sys.path.insert(0, str(ASSIGNMENT_SRC))

from expense_review import review_comment
from tools.assignment_inspector import is_valid_iso_date
from agent.core import build_assignment_audit


class AssignmentQualityTests(unittest.TestCase):

    def assert_human_review(self, result):
        self.assertTrue(result["human_confirmation_required"])
        self.assertFalse(result["automatic_approval"])

    def test_malformed_invoice_id_is_flagged(self):
        result = review_comment(
            "請求書照合完了。INV-ABC 金額：455,128円。差異あり要確認。"
        )
        self.assertEqual(result["workflow"], "invoice_review")
        self.assertIn("Invoice ID missing", result["flags"])
        self.assert_human_review(result)

    def test_missing_invoice_amount_is_flagged(self):
        result = review_comment(
            "請求書照合完了。INV-2026-7345。差異あり要確認。"
        )
        self.assertEqual(result["workflow"], "invoice_review")
        self.assertIn("Invoice amount missing", result["flags"])

    def test_missing_purchase_order_fields_are_flagged(self):
        result = review_comment(
            "発注管理処理。注文内容を確認してください。"
        )
        self.assertEqual(result["workflow"], "purchase_order")
        self.assertIn("Order total missing", result["flags"])
        self.assertIn("Quantity missing", result["flags"])
        self.assertIn("Order type missing", result["flags"])

    def test_missing_contract_details_are_flagged(self):
        result = review_comment(
            "契約管理処理。詳細を確認してください。"
        )
        self.assertEqual(result["workflow"], "contract_management")
        self.assertIn("Contract type missing", result["flags"])
        self.assertIn("Contract due date missing", result["flags"])

    def test_missing_payroll_details_are_flagged(self):
        result = review_comment(
            "給与変更登録。内容を確認してください。"
        )
        self.assertEqual(result["workflow"], "hr_payroll_change")
        self.assertIn("Payroll change type missing", result["flags"])
        self.assertIn("Effective date missing", result["flags"])

    def test_missing_expense_details_are_flagged(self):
        result = review_comment(
            "経費精算確認済み。内容を確認してください。"
        )
        self.assertEqual(result["workflow"], "expense_claim_review")
        self.assertIn("Expense amount not detected", result["flags"])
        self.assertIn("Expense category missing", result["flags"])

    def test_missing_management_expense_details_are_flagged(self):
        result = review_comment(
            "経費承認（管理職）。内容を確認してください。"
        )
        self.assertEqual(
            result["workflow"], "management_expense_approval"
        )
        self.assertTrue(result["flags"])
        self.assert_human_review(result)

    def test_missing_inventory_fields_are_flagged(self):
        result = review_comment(
            "在庫調整登録。品名：部品。"
        )
        self.assertEqual(result["workflow"], "inventory_adjustment")
        self.assertIn("Item code missing", result["flags"])
        self.assertIn("Adjustment quantity missing", result["flags"])

    def test_missing_leave_details_are_flagged(self):
        result = review_comment(
            "勤怠申請確認。内容を確認してください。"
        )
        self.assertEqual(
            result["workflow"], "attendance_leave_review"
        )
        self.assertIn("Leave type missing", result["flags"])
        self.assertIn("Leave date missing", result["flags"])

    def test_unknown_comment_is_flagged(self):
        result = review_comment("Please review this request.")
        self.assertEqual(result["workflow"], "unknown")
        self.assertIn("Workflow not recognized", result["flags"])
        self.assert_human_review(result)

    def test_all_eight_workflows_require_human_review(self):
        comments = [
            "請求書照合完了。INV-2026-7345 金額：455,128円。差異あり要確認。",
            "発注管理処理。緊急発注：測定機器 数量 40 合計 149,920円 緊急。",
            "契約管理処理。種別：秘密保持契約。期日：2026-07-14。",
            "給与変更登録。変更種別：扶養控除変更。適用日：2026-07-02。",
            "経費精算確認済み。費目：交通費精算 金額：21,542円。",
            "在庫調整登録。品番：BATCH-W2 品名：電源モジュールB 調整数：+155個。",
            "経費承認（管理職）。費目：研修費 金額：57,180円。",
            "勤怠申請確認。種別：半日有給申請。取得日：2026-07-23。",
        ]

        for comment in comments:
            with self.subTest(comment=comment):
                self.assert_human_review(review_comment(comment))

    def test_original_prototype_invalid_date_limitation_is_documented(self):
        result = review_comment(
            "契約管理処理。種別：秘密保持契約。期日：2026-99-99。"
        )

        # This test documents the observed limitation; it does not
        # claim that the original prototype validates the date.
        self.assertEqual(
            result["fields"]["due_or_effective_date"], "2026-99-99"
        )
        self.assertEqual(result["flags"], [])
        self.assert_human_review(result)

    def test_date_validator_accepts_real_date(self):
        self.assertTrue(is_valid_iso_date("2026-07-14"))

    def test_date_validator_rejects_impossible_date(self):
        self.assertFalse(is_valid_iso_date("2026-99-99"))

    def test_date_validator_rejects_nonexistent_calendar_date(self):
        self.assertFalse(is_valid_iso_date("2026-02-30"))

    def test_date_validator_rejects_wrong_format(self):
        self.assertFalse(is_valid_iso_date("not-a-date"))

    def test_agent_audit_detects_missing_date_validation(self):
        audit = build_assignment_audit()
        titles = [finding["title"] for finding in audit["findings"]]

        self.assertIn(
            "Extracted dates lack calendar-aware validation",
            titles,
        )

    def test_agent_date_validator_self_checks(self):
        audit = build_assignment_audit()
        checks = audit["date_validator_checks"]

        self.assertTrue(checks["valid_date"])
        self.assertFalse(checks["impossible_month_day"])
        self.assertFalse(checks["nonexistent_calendar_date"])
        self.assertFalse(checks["malformed_date"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
