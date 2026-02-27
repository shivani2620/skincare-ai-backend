from anthropic import Anthropic
import json
from typing import Dict, List
import os


class AnalysisAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

        self.client = Anthropic(api_key=api_key)

    async def analyze_product(self, product: Dict, user_profile: Dict) -> Dict:
        """
        Deep product analysis for specific user
        """

        system_prompt = """You are a cosmetic chemist analyzing a product for a specific user.

Return ONLY valid JSON with this structure:

{
    "overall_score": 75,
    "recommendation": "recommended|caution|not_recommended",
    "summary": "Brief assessment",
    "ingredient_analyses": [],
    "warnings": [],
    "benefits": [],
    "interactions": [],
    "usage_tips": []
}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2500,
                temperature=0.2,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Product: {json.dumps(product)}

User Profile: {json.dumps(user_profile)}

Analyze this product for THIS specific user."""
                    }
                ],
            )

            response_text = message.content[0].text.strip()

            # Clean markdown if present
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            response_text = response_text.strip()

            return json.loads(response_text)

        except Exception as e:
            print(f"AI Analysis error: {e}")
            return self._fallback_analysis(product, user_profile)

    def _fallback_analysis(self, product: Dict, user_profile: Dict) -> Dict:
        """
        Rule-based fallback if AI fails
        """

        score = 70
        warnings = []
        benefits = []

        ingredients = [i.lower() for i in product.get("ingredients", [])]
        allergies = [a.lower() for a in user_profile.get("allergies", [])]
        skin_type = user_profile.get("skin_type", "normal")

        # Allergy check
        for allergy in allergies:
            if allergy in ingredients:
                warnings.append(f"⚠️ Contains {allergy} - you're allergic!")
                score -= 30

        # Skin type matching
        if skin_type == "dry":
            if any(a in ingredients for a in ["alcohol", "alcohol denat"]):
                warnings.append("❌ Contains alcohol - drying for dry skin")
                score -= 20
            if "hyaluronic acid" in ingredients:
                benefits.append("✅ Hyaluronic acid - great for hydration")
                score += 10

        if skin_type == "sensitive":
            if "fragrance" in ingredients or "parfum" in ingredients:
                warnings.append("⚠️ Contains fragrance - may irritate sensitive skin")
                score -= 15

        score = max(0, min(100, score))

        return {
            "overall_score": score,
            "recommendation": (
                "recommended"
                if score >= 70
                else "caution"
                if score >= 50
                else "not_recommended"
            ),
            "summary": f"Fallback analysis score: {score}/100",
            "ingredient_analyses": [],
            "warnings": warnings,
            "benefits": benefits,
            "interactions": [],
            "usage_tips": [],
        }

    async def check_ingredient_interactions(self, ingredients: List[str]) -> List[str]:
        """
        Check for dangerous ingredient combinations
        """

        system_prompt = """Check for known skincare ingredient interactions.

Return ONLY a JSON array of warnings:
["Warning 1", "Warning 2"]

If none, return empty array: []
"""

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Ingredients: {json.dumps(ingredients)}"
                    }
                ],
            )

            response_text = message.content[0].text.strip()

            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            response_text = response_text.strip()

            return json.loads(response_text)

        except Exception as e:
            print(f"Interaction check error: {e}")
            return []