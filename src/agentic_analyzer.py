"""
Agentic Text Analyzer
En selvstændig AI agent der kan iterere over sin egen analyse indtil den er tilfreds.
"""

from typing import Dict, List, Tuple, Optional
from pathlib import Path
from .llm_providers import BaseLLMProvider
from .document_reader import DocumentReader
import json

try:
    from .knowledge_base import KnowledgeBase
except ImportError:
    KnowledgeBase = None


class AgenticAnalyzer:
    """
    En AI agent der kan:
    1. Bruge LLM som "thinking brain" til at planlægge og udføre analyse
    2. Læse og skrive til dokumenter
    3. Verificere sit eget arbejde og iterere indtil kvaliteten er god nok
    """

    def __init__(self, llm_provider: BaseLLMProvider, max_iterations: int = 3,
                 knowledge_base: Optional['KnowledgeBase'] = None):
        """
        Args:
            llm_provider: LLM provider til at udføre analyse
            max_iterations: Max antal iterationer (for at undgå uendelige loops)
            knowledge_base: Optional RAG knowledge base for style guidelines
        """
        self.llm_provider = llm_provider
        self.max_iterations = max_iterations
        self.doc_reader = DocumentReader()
        self.knowledge_base = knowledge_base

    def read_document(self, file_path: Path) -> Tuple[str, str]:
        """
        Tool: Læs dokument fra fil (understøtter TXT, PDF, Word).

        Returns:
            Tuple af (text, format)
        """
        return self.doc_reader.read_file(file_path)

    def write_document(self, file_path: Path, content: str, file_format: str = 'txt'):
        """
        Tool: Skriv dokument til fil.

        Args:
            file_path: Sti til output fil
            content: Indhold der skal skrives
            file_format: Format ('txt', 'pdf', 'docx')
        """
        self.doc_reader.write_file(file_path, content, file_format)

    def think_and_analyze(self, text: str, parameters: Dict[str, bool]) -> Dict:
        """
        Step 1: LLM "tænker" og analyserer teksten.
        """
        # Get relevant style guidelines if RAG is enabled
        style_guidelines = ""
        if self.knowledge_base:
            style_guidelines = self.knowledge_base.get_relevant_guidelines(text)

        return self.llm_provider.analyze_text(text, parameters, style_guidelines)

    def verify_quality(self, original_text: str, corrected_text: str,
                      corrections: List[Dict]) -> Tuple[bool, str, Dict]:
        """
        Step 2: LLM verificerer kvaliteten af sin egen analyse.

        Returns:
            (is_done, reasoning, verification_result)
        """
        verification_prompt = f"""Du er en kvalitetskontrollør. Vurder om følgende tekstrettelser er gode nok.

Original tekst:
{original_text}

Rettet tekst:
{corrected_text}

Antal rettelser: {len(corrections)}

Analyser følgende:
1. Er alle grammatiske fejl rettet?
2. Er stavningen korrekt?
3. Er teksten klar og læsbar?
4. Er der stadig åbenlyse fejl?

Returner JSON:
{{
    "is_done": true/false,
    "quality_score": 0-100,
    "reasoning": "Forklaring på beslutningen",
    "remaining_issues": ["liste af eventuelle problemer der stadig findes"],
    "suggestions": ["forslag til yderligere forbedringer"]
}}

Returner KUN JSON."""

        try:
            # Brug LLM til at verificere
            if hasattr(self.llm_provider, 'client'):
                # For Claude
                if hasattr(self.llm_provider.client, 'messages'):
                    message = self.llm_provider.client.messages.create(
                        model=self.llm_provider.model,
                        max_tokens=2048,
                        messages=[{"role": "user", "content": verification_prompt}]
                    )
                    response_text = message.content[0].text
                # For OpenAI
                else:
                    response = self.llm_provider.client.chat.completions.create(
                        model=self.llm_provider.model,
                        messages=[
                            {"role": "system", "content": "Du er en kvalitetskontrollør. Returner altid valid JSON."},
                            {"role": "user", "content": verification_prompt}
                        ],
                        temperature=0.3
                    )
                    response_text = response.choices[0].message.content

                # Parse JSON
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                elif response_text.startswith("```"):
                    response_text = response_text.replace("```", "").strip()

                result = json.loads(response_text)

                is_done = result.get("is_done", False)
                reasoning = result.get("reasoning", "Ingen forklaring")

                return is_done, reasoning, result

        except Exception as e:
            # Hvis verifikation fejler, antag vi er done
            return True, f"Verifikation fejlede: {str(e)}", {"quality_score": 50}

    def analyze_with_iterations(self, file_path: Path, parameters: Dict[str, bool],
                                iteration_callback=None) -> Dict:
        """
        Hovedfunktion: Analyserer dokument med agentic loop.

        Loop:
        1. LLM analyserer teksten (thinking brain)
        2. LLM verificerer kvaliteten
        3. Hvis ikke done, loop tilbage til step 1 med feedback

        Args:
            file_path: Sti til fil der skal analyseres
            parameters: Analyse parametre
            iteration_callback: Callback der kaldes efter hver iteration

        Returns:
            Dict med resultater inkl. alle iterationer
        """
        # Læs dokument (Tool)
        current_text, file_format = self.read_document(file_path)
        original_text = current_text

        iterations = []
        is_done = False
        iteration_count = 0

        while not is_done and iteration_count < self.max_iterations:
            iteration_count += 1

            # Step 1: Think and analyze (LLM som thinking brain)
            analysis_result = self.think_and_analyze(current_text, parameters)

            # Step 2: Verify quality (LLM verificerer sit eget arbejde)
            is_done, reasoning, verification = self.verify_quality(
                current_text,
                analysis_result.get("corrected_text", current_text),
                analysis_result.get("corrections", [])
            )

            # Gem iteration info
            iteration_info = {
                "iteration": iteration_count,
                "analysis": analysis_result,
                "verification": verification,
                "is_done": is_done,
                "reasoning": reasoning
            }
            iterations.append(iteration_info)

            # Callback for progress tracking
            if iteration_callback:
                iteration_callback(iteration_count, self.max_iterations, is_done, reasoning)

            # Hvis ikke done, brug den rettede tekst som input til næste iteration
            if not is_done:
                current_text = analysis_result.get("corrected_text", current_text)

        # Saml final result
        final_result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_format": file_format,
            "original_text": original_text,
            "final_corrected_text": iterations[-1]["analysis"]["corrected_text"],
            "total_iterations": iteration_count,
            "iterations": iterations,
            "final_quality_score": iterations[-1]["verification"].get("quality_score", 0),
            "all_corrections": [],
            "final_feedback": iterations[-1]["verification"].get("reasoning", "")
        }

        # Saml alle rettelser fra alle iterationer
        for iteration in iterations:
            for correction in iteration["analysis"].get("corrections", []):
                correction["iteration"] = iteration["iteration"]
                final_result["all_corrections"].append(correction)

        return final_result

    def save_result(self, result: Dict, output_path: Path):
        """Gem det endelige resultat"""
        file_format = result.get("file_format", "txt")
        self.write_document(output_path, result["final_corrected_text"], file_format)
