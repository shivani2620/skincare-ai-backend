from anthropic import Anthropic
import json
from typing import Dict, List
import os

from .profile_agent import ProfileIntelligenceAgent
from .analysis_agent import AnalysisAgent
from .recommendation_agent import RecommendationAgent


class OrchestratorAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

        self.client = Anthropic(api_key=api_key)
        self.profile_agent = ProfileIntelligenceAgent()
        self.analysis_agent = AnalysisAgent()
        self.recommendation_agent = RecommendationAgent()

    async def route_request(
        self,
        user_message: str,
        user_profile: Dict,
        conversation_history: List[Dict] = None,
    ) -> Dict:
        """
        Intelligently route user requests to appropriate agents
        """

        if conversation_history is None:
            conversation_history = []

        system_prompt = """You are an intelligent orchestrator for a skincare AI system.

Available agents:
1. PROFILE - Profile analysis, update preferences, skin type understanding
2. ANALYSIS - Analyze products, ingredients, safety checks
3. RECOMMENDATION - Suggest products, routines, alternatives
4. CHAT - General conversation and education

Return ONLY valid JSON:

{
    "agent": "PROFILE|ANALYSIS|RECOMMENDATION|CHAT",
    "action": "specific_action_name",
    "parameters": {},
    "confidence": 0.95
}
"""

        try:
            # Build conversation context safely
            context = "\n".join(
                [
                    f"{msg.get('role')}: {msg.get('content')}"
                    for msg in conversation_history[-5:]
                ]
            )

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""User profile:
{json.dumps(user_profile)}

Conversation context:
{context}

New message:
{user_message}

Route this request."""
                    }
                ],
            )

            response_text = message.content[0].text.strip()

            # Clean markdown if Claude wraps JSON
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            routing = json.loads(response_text)

            result = await self._execute_agent_action(
                routing, user_message, user_profile
            )

            return {
                "agent_used": routing.get("agent", "CHAT"),
                "response": result,
                "confidence": routing.get("confidence", 0.8),
            }

        except Exception as e:
            print(f"Orchestrator error: {e}")
            return {
                "agent_used": "CHAT",
                "response": "I'm here to help! Could you rephrase that?",
                "confidence": 0.5,
            }

    async def _execute_agent_action(
        self, routing: Dict, message: str, profile: Dict
    ) -> str:
        """
        Execute the appropriate agent action
        """

        agent = routing.get("agent", "CHAT")
        action = routing.get("action", "").lower()
        parameters = routing.get("parameters", {})

        try:
            # ---------------- PROFILE ----------------
            if agent == "PROFILE":

                if "analyze" in action:
                    result = await self.profile_agent.analyze_description(message)
                    return self._format_profile_response(result)

                elif "questions" in action:
                    questions = await self.profile_agent.generate_questions(profile)
                    return questions[0] if questions else "Tell me more about your skin!"

                return "I'd love to understand your skin better. Could you tell me more?"

            # ---------------- ANALYSIS ----------------
            elif agent == "ANALYSIS":

                product = parameters.get("product")

                if not product:
                    return "Please provide the product details or ingredient list."

                analysis = await self.analysis_agent.analyze_product(
                    product, profile
                )

                return analysis.get("summary", "Product analyzed successfully.")

            # ---------------- RECOMMENDATION ----------------
            elif agent == "RECOMMENDATION":

                recommendations = await self.recommendation_agent.generate_recommendations(
                    profile
                )

                return recommendations

            # ---------------- CHAT ----------------
            else:
                return await self._general_chat(message, profile)

        except Exception as e:
            print(f"Execution error: {e}")
            return "Something went wrong while processing your request."

    async def _general_chat(self, message: str, profile: Dict) -> str:
        """
        General conversational AI
        """

        system_prompt = """You are a friendly skincare advisor AI.

Provide accurate, helpful skincare information.
Be empathetic and conversational.
Keep responses concise (2-3 short paragraphs).
"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""User profile:
{json.dumps(profile)}

Message:
{message}"""
                    }
                ],
            )

            return response.content[0].text.strip()

        except Exception:
            return "I'm here to help with your skincare questions!"

    def _format_profile_response(self, analysis: Dict) -> str:
        """
        Format profile analysis into friendly message
        """

        skin_type = analysis.get("skin_type", "normal")
        concerns = ", ".join(analysis.get("concerns", []))

        response = f"Got it! I see you have {skin_type} skin"

        if concerns:
            response += f" and you're concerned about {concerns}"

        response += "."

        questions = analysis.get("follow_up_questions", [])

        if questions:
            response += f"\n\n{questions[0]}"

        return response