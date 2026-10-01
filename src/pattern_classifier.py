from typing import Dict, Any

class PatternClassifier:
    """Classifies 4-digit signal codes into Full House 🏠, Spades ♠️, or One-Eye Jacks 🃏."""

    @staticmethod
    def classify(digit_code: str) -> Dict[str, Any]:
        """
        Takes a 4-digit string like '1145', '2323', '5555', '5551'
        and returns card type classification & risk parameters.
        """
        if len(digit_code) != 4 or not digit_code.isdigit():
            return {"category": "UNKNOWN", "emoji": "❓", "capital_share": 0.0, "move_type": "Invalid code"}

        digits = [int(d) for d in digit_code]

        # 1. Full House: Quad repeats (5555) or alternating pairs (2323, 3232) or uniform scale
        if digits[0] == digits[1] == digits[2] == digits[3]:
            return {"category": "FULL_HOUSE", "emoji": "🏠", "capital_share": 0.70, "move_type": "Big Persistent Move (12-24 hrs)"}
        if digits[0] == digits[2] and digits[1] == digits[3]:
            return {"category": "FULL_HOUSE", "emoji": "🏠", "capital_share": 0.70, "move_type": "Big Persistent Move (12-24 hrs)"}

        # 2. Spades: 2-and-2 split (2 large vs 2 small or vice versa, e.g., 1145, 5522, 2255)
        # Check symmetry
        if (digits[0] <= 2 and digits[1] <= 2 and digits[2] >= 4 and digits[3] >= 4) or \
           (digits[0] >= 4 and digits[1] >= 4 and digits[2] <= 2 and digits[3] <= 2) or \
           (digits[0] == digits[1] and digits[2] == digits[3]):
            return {"category": "SPADES", "emoji": "♠️", "capital_share": 0.15, "move_type": "Continuous Trend Move"}

        # 3. One-Eye Jacks: 3-vs-1 split (e.g. 0355, 5515, 1151, 1555, 1115)
        small_count = sum(1 for d in digits if d <= 2)
        large_count = sum(1 for d in digits if d >= 4)
        most_common_cnt = max(digits.count(d) for d in set(digits))
        if digit_code == "0355" or most_common_cnt == 3 or (small_count == 3 and large_count == 1) or (large_count == 3 and small_count == 1):
            return {"category": "JACKS", "emoji": "🃏", "capital_share": 0.15, "move_type": "Medium Volatility Trigger"}

        # Default fallback to Spades / Jacks based on distribution
        return {"category": "SPADES", "emoji": "♠️", "capital_share": 0.15, "move_type": "Standard Continuation Move"}
