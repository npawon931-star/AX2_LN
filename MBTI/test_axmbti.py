import unittest
import math
from logic import QUESTIONS, PERSONAS, cosine_similarity, calculate_scores, find_best_matching_persona

class TestTradeMBTILogic(unittest.TestCase):

    def test_questions_count_and_structure(self):
        """질문 목록이 총 20개이고, 각 질문이 올바른 형태를 지녔는지 검증합니다."""
        self.assertEqual(len(QUESTIONS), 20)
        for i, q in enumerate(QUESTIONS):
            self.assertIn("part", q)
            self.assertIn("part_title", q)
            self.assertIn("id", q)
            self.assertEqual(q["id"], i + 1)
            self.assertIn("text", q)
            self.assertIn("options", q)
            self.assertEqual(len(q["options"]), 2)
            for opt in q["options"]:
                self.assertIn("text", opt)
                self.assertIn("scores", opt)
                # 각 옵션이 최소 하나의 역량 점수를 주는지 확인
                self.assertTrue(len(opt["scores"]) >= 1)

    def test_mathematical_balance(self):
        """
        각 역량별 최대 획득 가능 점수가 정확히 24점인지 완벽한 밸런스를 확인합니다.
        (Part 1: 1점, Part 2: 3점, Part 3: 3점, Part 4: 5점 가중치 총합 검증)
        """
        max_scores = {
            "communication": 0.0,
            "strategy": 0.0,
            "coordination": 0.0,
            "sourcing": 0.0,
            "compliance": 0.0
        }

        # 각 질문에서 해당 역량을 최대로 얻을 수 있는 옵션 값을 집계
        for q in QUESTIONS:
            q_max = {}
            for opt in q["options"]:
                for axis, val in opt["scores"].items():
                    q_max[axis] = max(q_max.get(axis, 0.0), val)
            
            for axis, val in q_max.items():
                max_scores[axis] += val

        # 모든 5대 축의 최대 점수가 정확히 24.0인지 단언합니다.
        for axis, total in max_scores.items():
            self.assertEqual(total, 24.0, f"역량 '{axis}'의 최대 점수가 {total}점입니다. 24.0이어야 합니다.")

    def test_cosine_similarity(self):
        """코사인 유사도 함수가 정확히 계산되고 분모 0인 엣지 케이스를 안전하게 처리하는지 검증합니다."""
        # 1. 동일 벡터 유사도는 1.0 (float 부동소수점 오차 감안)
        v1 = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(cosine_similarity(v1, v1), 1.0)

        # 2. 직교 벡터 유사도는 0.0
        v2 = [1, 0, 0, 0, 0]
        v3 = [0, 1, 0, 0, 0]
        self.assertAlmostEqual(cosine_similarity(v2, v3), 0.0)

        # 3. 영 벡터(Zero Vector) 입력 시 안전하게 0.0을 처리하는지 확인 (ZeroDivisionError 방지)
        v_zero = [0, 0, 0, 0, 0]
        self.assertEqual(cosine_similarity(v1, v_zero), 0.0)
        self.assertEqual(cosine_similarity(v_zero, v_zero), 0.0)

    def test_calculate_scores(self):
        """모든 답변이 0(A안) 또는 1(B안)일 때 점수가 비정상적으로 누락되거나 오류나지 않는지 검증합니다."""
        # 모두 A를 선택한 경우
        all_a_answers = [0] * 20
        scores_a = calculate_scores(all_a_answers)
        self.assertEqual(len(scores_a), 5)
        self.assertTrue(all(val >= 0 for val in scores_a.values()))

        # 모두 B를 선택한 경우
        all_b_answers = [1] * 20
        scores_b = calculate_scores(all_b_answers)
        self.assertEqual(len(scores_b), 5)
        self.assertTrue(all(val >= 0 for val in scores_b.values()))

        # 일부 비어있는 응답이 있어도 예외 없이 안전하게 작동하는지 검증
        partial_answers = [0] * 10 + [None] * 10
        scores_partial = calculate_scores(partial_answers)
        self.assertEqual(len(scores_partial), 5)

    def test_find_best_matching_persona(self):
        """특정 역량이 높을 때 의도된 무역 직무 페르소나와 매칭되는지 확인합니다."""
        # 소통(communication)과 전략(strategy)이 압도적으로 높은 유저 점수 세팅
        mock_scores = {
            "communication": 20.0,
            "strategy": 20.0,
            "coordination": 2.0,
            "sourcing": 2.0,
            "compliance": 1.0
        }
        best_key, best_sim, similarities = find_best_matching_persona(mock_scores)
        # 해외영업 프론티어 (sales_frontier) 또는 종합상사 비즈니스 디벨로퍼 (business_developer)가 매칭되어야 함
        self.assertIn(best_key, ["sales_frontier", "business_developer"])
        self.assertTrue(best_sim > 0.8)

        # 법규(compliance)와 분석(sourcing)이 압도적으로 높은 유저 세팅
        mock_scores_comp = {
            "communication": 1.0,
            "strategy": 2.0,
            "coordination": 2.0,
            "sourcing": 18.0,
            "compliance": 20.0
        }
        best_key_comp, _, _ = find_best_matching_persona(mock_scores_comp)
        # 수출입 리스크 컨트롤러 (compliance_controller)와 매칭되어야 함
        self.assertEqual(best_key_comp, "compliance_controller")

if __name__ == '__main__':
    unittest.main()
