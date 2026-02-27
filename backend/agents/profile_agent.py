from anthropic import Anthropic
import json
from typing import Dict, List
import os


class ProfileIntelligenceAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

        self.client = Anthropic(api_key=api_key)

    async def analyze_description(self, description: str) -> Dict:
        """
        Extract structured profile from natural language
        """

        system_prompt = """You are a dermatology expert analyzing a user's skin description.

Extract structured information and return ONLY valid JSON (no markdown, no backticks):

{
    "skin_type": "oily|dry|combination|sensitive|normal",
    "concerns": ["acne", "wrinkles", "dark_spots", "redness"],
    "severity": {
        "acne": "mild|moderate|severe"
    },
    "triggers": ["stress", "diet", "weather", "hormones"],
    "current_routine": ["cleanser", "moisturizer"],
    "goals": ["clear_skin", "anti_aging", "hydration"],
    "confidence": 0.85,
    "follow_up_questions": ["Question 1?", "Question 2?"]
}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"User describes their skin: {description}",
                    }
                ],
            )

            response_text = message.content[0].text.strip()

            # Remove markdown formatting safely
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            response_text = response_text.strip()

            analysis = json.loads(response_text)
            return analysis

        except Exception as e:
            print(f"Profile analysis error: {e}")
            return {
                "error": str(e),
                "skin_type": "normal",
                "concerns": [],
                "confidence": 0.0,
            }

    async def generate_questions(self, current_profile: Dict) -> List[str]:
        """
        Generate contextual follow-up questions
        """

        system_prompt = """Generate 3 conversational follow-up questions 
to better understand the user's skin.

Return ONLY a JSON array of strings:
["Question 1?", "Question 2?", "Question 3?"]
"""

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Current profile: {json.dumps(current_profile)}",
                    }
                ],
            )

            response_text = message.content[0].text.strip()

            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            response_text = response_text.strip()

            questions = json.loads(response_text)
            return questions

        except Exception as e:
            print(f"Question generation error: {e}")
            return [
                "How does your skin feel by midday?",
                "Do you have any specific product preferences?",
                "What’s your main skin goal right now?",
            ]