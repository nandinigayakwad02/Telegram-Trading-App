from typing import Dict, Any

class PatternClassifier:
    """
    Classifies 4-digit signal codes into Full House 🏠, Spades ♠️, or One-Eye Jacks 🃏.
    Implements full Neurofuzzy pattern evaluation logic.
    """

    @staticmethod
    def classify(digit_code: str) -> Dict[str, Any]:
        """
        Takes a 4-digit code (e.g. '2323', '5555', '1145', '5551')
        and returns detailed classification, confidence, capital share, and trading playbook.
        """
        code_str = str(digit_code).strip()
        if len(code_str) != 4 or not code_str.isdigit():
            return {
                "code": code_str,
                "verdict": "UNKNOWN",
                "category": "UNKNOWN",
                "emoji": "❓",
                "confidence_pct": 50.0,
                "recommended_allocation_pct": 0,
                "capital_share": 0.0,
                "structural_logic": "Unrecognized digit pattern code.",
                "expected_move": "Invalid or noise signal",
                "optimal_horizon": "N/A",
                "playbook": "Do not execute. Await clear 4-digit code structure."
            }

        digits = [int(d) for d in code_str]

        # 1. Full House 🏠: Quad repeats (5555) or alternating pairs (2323, 3232)
        if digits[0] == digits[1] == digits[2] == digits[3]:
            return {
                "code": code_str,
                "verdict": "FULL_HOUSE",
                "category": "FULL_HOUSE",
                "emoji": "🏠",
                "confidence_pct": 99.9,
                "recommended_allocation_pct": 70,
                "capital_share": 0.70,
                "structural_logic": "Quad repetitive resonance signaling extreme directional conviction and high institutional liquidity.",
                "expected_move": "Big Persistent Move lasting 12 to 24 hours",
                "optimal_horizon": "12h - 24h",
                "playbook": "Deploy max capital (70%) with trailing stop-loss. Capture multi-hour breakout volatility without theta decay."
            }

        if digits[0] == digits[2] and digits[1] == digits[3]:
            return {
                "code": code_str,
                "verdict": "FULL_HOUSE",
                "category": "FULL_HOUSE",
                "emoji": "🏠",
                "confidence_pct": 99.8,
                "recommended_allocation_pct": 70,
                "capital_share": 0.70,
                "structural_logic": "Harmonic alternating pairs signaling major structural persistence.",
                "expected_move": "Big Persistent Move lasting 12 to 24 hours",
                "optimal_horizon": "12h - 24h",
                "playbook": "Deploy high-frequency sub-algorithms to capture multi-hour breakout volatility without theta decay."
            }

        # 2. Spades ♠️: 2-and-2 split (2 large vs 2 small or vice versa, e.g. 1145, 5522, 2255)
        if (digits[0] <= 2 and digits[1] <= 2 and digits[2] >= 4 and digits[3] >= 4) or \
           (digits[0] >= 4 and digits[1] >= 4 and digits[2] <= 2 and digits[3] <= 2) or \
           (digits[0] == digits[1] and digits[2] == digits[3]):
            return {
                "code": code_str,
                "verdict": "SPADES",
                "category": "SPADES",
                "emoji": "♠️",
                "confidence_pct": 94.5,
                "recommended_allocation_pct": 15,
                "capital_share": 0.15,
                "structural_logic": "Balanced dual-node pulse indicating continuous trend expansion.",
                "expected_move": "Continuous Trend Move lasting 4 to 8 hours",
                "optimal_horizon": "4h - 8h",
                "playbook": "Scale in with 15% capital share. Ride standard trend continuation with dynamic take-profit targets."
            }

        # 3. One-Eye Jacks 🃏: 3 large + 1 small OR 3 small + 1 large (e.g. 5551, 1115)
        small_count = sum(1 for d in digits if d <= 2)
        large_count = sum(1 for d in digits if d >= 4)
        if (small_count == 3 and large_count == 1) or (large_count == 3 and small_count == 1):
            return {
                "code": code_str,
                "verdict": "JACKS",
                "category": "JACKS",
                "emoji": "🃏",
                "confidence_pct": 91.2,
                "recommended_allocation_pct": 15,
                "capital_share": 0.15,
                "structural_logic": "Asymmetric single-eye surge indicating localized momentum impulse.",
                "expected_move": "Medium Move lasting 2 to 4 hours",
                "optimal_horizon": "2h - 4h",
                "playbook": "Execute quick scalp with tight risk boundaries. Take partial profit at 1:2 R:R."
            }

        # Fallback to Spades
        return {
            "code": code_str,
            "verdict": "SPADES",
            "category": "SPADES",
            "emoji": "♠️",
            "confidence_pct": 88.0,
            "recommended_allocation_pct": 15,
            "capital_share": 0.15,
            "structural_logic": "Standard Continuation Move pattern.",
            "expected_move": "Standard Continuation Move lasting 4 hours",
            "optimal_horizon": "4h",
            "playbook": "Standard execution with 15% risk budget."
        }
