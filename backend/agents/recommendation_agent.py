from anthropic import Anthropic
import json
from typing import Dict, List
import os


class RecommendationAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

        self.client = Anthropic(api_key=api_key)

    # -------------------------------------------------------
    # FIND ALTERNATIVE PRODUCTS
    # -------------------------------------------------------
    async def find_alternatives(
        self,
        product: Dict,
        user_profile: Dict,
        reason: str = "better_match",
    ) -> List[Dict]:

        system_prompt = """You are a skincare product expert.

Find 3 alternative products that are:
- Better suited to the user's skin type
- Safer ingredient profile
- Popular and widely available
- Appropriate for their budget

Return ONLY valid JSON array:
[
  {
    "name": "Product Name",
    "brand": "Brand",
    "why_better": "Reason",
    "price_range": "$10-20",
    "match_score": 90,
    "where_to_buy": "Amazon, Target"
  }
]
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.4,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Current product:
{json.dumps(product)}

User profile:
{json.dumps(user_profile)}

Reason:
{reason}

Find 3 better alternatives."""
                    }
                ],
            )

            response_text = message.content[0].text.strip()

            # Clean markdown if wrapped
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            response_text = response_text.strip()

            alternatives = json.loads(response_text)

            # Ensure list return
            if isinstance(alternatives, list):
                return alternatives
            else:
                return []

        except Exception as e:
            print(f"Recommendation error: {e}")
            return []

    # -------------------------------------------------------
    # BUILD COMPLETE ROUTINE
    # -------------------------------------------------------
    async def build_routine(
        self,
        user_profile: Dict,
        budget: str = "mid-range",
    ) -> Dict:

        system_prompt = """Create a personalized skincare routine.

Include:
- Morning routine (4-6 steps)
- Night routine (5-7 steps)
- 2-3 weekly treatments
- Order of application matters

Return ONLY valid JSON:
{
  "morning": [],
  "night": [],
  "weekly": [],
  "total_monthly_cost": "$50-100",
  "expected_results": "Timeline",
  "tips": []
}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.4,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""User profile:
{json.dumps(user_profile)}

Budget:
{budget}

Create a complete routine."""
                    }
                ],
            )

            response_text = message.content[0].text.strip()

            # Clean markdown if wrapped
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            response_text = response_text.strip()

            routine = json.loads(response_text)

            if isinstance(routine, dict):
                return routine
            else:
                return self._fallback_routine(user_profile)

        except Exception as e:
            print(f"Routine generation error: {e}")
            return self._fallback_routine(user_profile)

    # -------------------------------------------------------
    # FALLBACK ROUTINE (if AI fails)
    # -------------------------------------------------------
    def _fallback_routine(self, user_profile: Dict) -> Dict:
        """
        Safe minimal routine if AI fails
        """

        skin_type = user_profile.get("skin_type", "normal")

        return {
            "morning": [
                {
                    "step": 1,
                    "product_type": "Gentle Cleanser",
                    "recommendation": "Hydrating cleanser",
                    "why": f"Suitable for {skin_type} skin",
                    "price": "$10-15",
                },
                {
                    "step": 2,
                    "product_type": "Moisturizer",
                    "recommendation": "Barrier-repair moisturizer",
                    "why": "Maintains skin hydration",
                    "price": "$15-25",
                },
                {
                    "step": 3,
                    "product_type": "Sunscreen",
                    "recommendation": "SPF 30+ broad spectrum",
                    "why": "Protects from UV damage",
                    "price": "$10-20",
                },
            ],
            "night": [
                {
                    "step": 1,
                    "product_type": "Cleanser",
                    "recommendation": "Gentle cleanser",
                    "why": "Removes dirt and oil",
                    "price": "$10-15",
                },
                {
                    "step": 2,
                    "product_type": "Moisturizer",
                    "recommendation": "Hydrating moisturizer",
                    "why": "Supports skin repair overnight",
                    "price": "$15-25",
                },
            ],
            "weekly": [],
            "total_monthly_cost": "$40-70",
            "expected_results": "Improved hydration in 2-4 weeks",
            "tips": [
                "Patch test new products",
                "Introduce actives slowly",
                "Always wear sunscreen in the morning",
            ],
        }