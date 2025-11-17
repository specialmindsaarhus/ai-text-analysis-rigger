import anthropic
from typing import Dict, List
from .base_provider import BaseLLMProvider
import json


class ClaudeProvider(BaseLLMProvider):
    """
    Claude AI provider implementation.
    Bruger Anthropic's API til tekstanalyse.
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze_text(self, text: str, parameters: Dict[str, bool], style_guidelines: str = "") -> Dict[str, any]:
        """
        Analyserer tekst med Claude AI.
        """
        # Byg prompt baseret på parametre
        analysis_aspects = []
        if parameters.get("grammatik", True):
            analysis_aspects.append("grammatiske fejl")
        if parameters.get("stavning", True):
            analysis_aspects.append("stavefejl")
        if parameters.get("struktur", True):
            analysis_aspects.append("tekststruktur og sammenhæng")
        if parameters.get("klarhed", True):
            analysis_aspects.append("klarhed og læsbarhed")

        aspects_text = ", ".join(analysis_aspects)

        # Build base prompt
        prompt_parts = [f"Analyser følgende danske tekst for {aspects_text}."]

        # Inject style guidelines if available
        if style_guidelines:
            prompt_parts.append("\n" + "="*80)
            prompt_parts.append("\nSTILRETNINGSLINJER - VIGTIGE REGLER:")
            prompt_parts.append(style_guidelines)
            prompt_parts.append("\n" + "="*80)
            prompt_parts.append("""
KRITISK VIGTIGT om stilretningslinjerne:
1. KEY PHRASES markeret i <key_phrases> skal ALTID bevares - fjern dem ALDRIG
2. Professionel terminologi i <terminology> er BEVIDSTE valg - behold dem
3. Formattering i <formatting_rules> skal følges præcist
4. Ret KUN faktiske fejl (grammatik, stavning) - ikke stilistiske valg
5. Hvis en frase gentages (f.eks. "vi oplever"), behold den MEDMINDRE retningslinjerne specifikt siger at reducere gentagelser

Husk: Disse retningslinjer definerer den ØNSKEDE stil - overhold dem strengt!
""")

        # Add response format instructions
        prompt_parts.append("""
Returner dit svar som JSON med følgende struktur:
{
    "corrected_text": "Den rettede tekst her",
    "corrections": [
        {"type": "grammatik/stavning/struktur/klarhed", "original": "fejl", "correction": "rettelse", "explanation": "forklaring"},
        ...
    ],
    "feedback": "Overordnet feedback om teksten"
}

Tekst til analyse:
""")
        prompt_parts.append(text)
        prompt_parts.append("\nReturner KUN JSON, ingen anden tekst.")

        prompt = "".join(prompt_parts)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = message.content[0].text

            # Fjern eventuelle markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()

            result = json.loads(response_text)
            result["original_text"] = text

            return result

        except Exception as e:
            return {
                "original_text": text,
                "corrected_text": text,
                "corrections": [],
                "feedback": f"Fejl ved analyse: {str(e)}"
            }

    def get_provider_name(self) -> str:
        return f"Claude AI ({self.model})"
