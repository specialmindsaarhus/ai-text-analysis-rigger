import gradio as gr
from pathlib import Path
from typing import Dict, List, Optional
from .text_analyzer import TextAnalyzer
from .agentic_analyzer import AgenticAnalyzer
from .llm_providers import ClaudeProvider, OpenAIProvider

try:
    from .knowledge_base import KnowledgeBase
except ImportError:
    KnowledgeBase = None


class TextAnalysisGUI:
    """
    Gradio-baseret GUI for tekstanalyse.
    """

    def __init__(self, llm_provider, knowledge_base: Optional['KnowledgeBase'] = None):
        self.llm_provider = llm_provider
        self.knowledge_base = knowledge_base
        self.analyzer = TextAnalyzer(llm_provider, knowledge_base)
        self.agentic_analyzer = AgenticAnalyzer(llm_provider, max_iterations=3, knowledge_base=knowledge_base)
        self.current_results = []
        self.current_mode = "standard"

    def analyze_folder_handler(self, folder_path: str, grammatik: bool, stavning: bool,
                               struktur: bool, klarhed: bool, progress=gr.Progress()):
        """
        Handler for folder analyse.
        """
        if not folder_path:
            return "❌ Vælg venligst en mappe først", "", ""

        try:
            parameters = {
                "grammatik": grammatik,
                "stavning": stavning,
                "struktur": struktur,
                "klarhed": klarhed
            }

            # Find filer
            files = self.analyzer.find_files(folder_path)

            if not files:
                return "❌ Ingen understøttede dokumenter fundet i mappen (TXT, PDF, Word)", "", ""

            progress(0, desc="Starter analyse...")

            # Analyse med progress
            def progress_callback(current, total, filename):
                progress(current / total, desc=f"Analyserer {filename} ({current}/{total})")

            self.current_results = self.analyzer.analyze_folder(
                folder_path,
                parameters,
                progress_callback
            )

            # Generer resultat rapport
            report = self.generate_report(self.current_results)
            details = self.generate_details(self.current_results)

            status = f"✅ Analyseret {len(self.current_results)} filer"

            return status, report, details

        except Exception as e:
            return f"❌ Fejl: {str(e)}", "", ""

    def analyze_folder_agentic_handler(self, folder_path: str, grammatik: bool, stavning: bool,
                                      struktur: bool, klarhed: bool, max_iterations: int,
                                      progress=gr.Progress()):
        """
        Handler for agentic folder analyse med self-verification loop.
        """
        if not folder_path:
            return "❌ Vælg venligst en mappe først", "", ""

        try:
            parameters = {
                "grammatik": grammatik,
                "stavning": stavning,
                "struktur": struktur,
                "klarhed": klarhed
            }

            # Find filer
            files = self.analyzer.find_files(folder_path)

            if not files:
                return "❌ Ingen understøttede dokumenter fundet i mappen (TXT, PDF, Word)", "", ""

            progress(0, desc="Starter agentic analyse...")

            # Opdater max iterations
            self.agentic_analyzer.max_iterations = max_iterations

            # Analyser hver fil med agentic loop
            self.current_results = []
            total = len(files)

            for i, file_path in enumerate(files, 1):
                progress(i / total, desc=f"Analyserer {file_path.name} med AI agent ({i}/{total})")

                # Iteration callback
                def iteration_callback(iteration, max_iter, is_done, reasoning):
                    progress(
                        (i - 1 + iteration / max_iter) / total,
                        desc=f"{file_path.name} - Iteration {iteration}/{max_iter}"
                    )

                result = self.agentic_analyzer.analyze_with_iterations(
                    file_path,
                    parameters,
                    iteration_callback
                )
                self.current_results.append(result)

            # Generer rapport
            report = self.generate_agentic_report(self.current_results)
            details = self.generate_agentic_details(self.current_results)

            total_iterations = sum(r["total_iterations"] for r in self.current_results)
            avg_quality = sum(r["final_quality_score"] for r in self.current_results) / len(self.current_results)

            status = f"✅ Analyseret {len(self.current_results)} filer med {total_iterations} total iterationer (Gns. kvalitet: {avg_quality:.0f}%)"

            return status, report, details

        except Exception as e:
            return f"❌ Fejl: {str(e)}", "", ""

    def generate_report(self, results: List[Dict]) -> str:
        """
        Genererer en kort rapport.
        """
        if not results:
            return ""

        total_files = len(results)
        total_corrections = sum(len(r.get("corrections", [])) for r in results)

        report = f"## Analyse Rapport\n\n"
        report += f"**Antal filer:** {total_files}  \n"
        report += f"**Total rettelser:** {total_corrections}  \n\n"
        report += f"### Filer:\n\n"

        for r in results:
            corrections_count = len(r.get("corrections", []))
            report += f"- **{r['file_name']}**: {corrections_count} rettelser\n"

        return report

    def generate_details(self, results: List[Dict]) -> str:
        """
        Genererer detaljeret visning af rettelser.
        """
        if not results:
            return ""

        details = ""

        for r in results:
            details += f"## 📄 {r['file_name']}\n\n"

            # Feedback
            if r.get("feedback"):
                details += f"**Feedback:** {r['feedback']}\n\n"

            # Rettelser
            corrections = r.get("corrections", [])
            if corrections:
                details += f"**Rettelser ({len(corrections)}):**\n\n"
                for i, correction in enumerate(corrections, 1):
                    details += f"{i}. **{correction.get('type', 'N/A')}**\n"
                    details += f"   - Original: `{correction.get('original', 'N/A')}`\n"
                    details += f"   - Rettelse: `{correction.get('correction', 'N/A')}`\n"
                    details += f"   - Forklaring: {correction.get('explanation', 'N/A')}\n\n"
            else:
                details += "✅ Ingen rettelser nødvendige\n\n"

            details += "---\n\n"

        return details

    def generate_agentic_report(self, results: List[Dict]) -> str:
        """
        Genererer rapport for agentic analyse.
        """
        if not results:
            return ""

        total_files = len(results)
        total_iterations = sum(r["total_iterations"] for r in results)
        avg_quality = sum(r["final_quality_score"] for r in results) / total_files
        total_corrections = sum(len(r.get("all_corrections", [])) for r in results)

        report = f"## Agentic Analyse Rapport\n\n"
        report += f"**Antal filer:** {total_files}  \n"
        report += f"**Total iterationer:** {total_iterations}  \n"
        report += f"**Gennemsnitlig kvalitet:** {avg_quality:.0f}%  \n"
        report += f"**Total rettelser:** {total_corrections}  \n\n"
        report += f"### Filer:\n\n"

        for r in results:
            iterations = r["total_iterations"]
            quality = r["final_quality_score"]
            corrections_count = len(r.get("all_corrections", []))
            report += f"- **{r['file_name']}**: {iterations} iterationer, {quality}% kvalitet, {corrections_count} rettelser\n"

        return report

    def generate_agentic_details(self, results: List[Dict]) -> str:
        """
        Genererer detaljeret visning for agentic analyse.
        """
        if not results:
            return ""

        details = ""

        for r in results:
            details += f"## 📄 {r['file_name']}\n\n"
            details += f"**Total iterationer:** {r['total_iterations']}  \n"
            details += f"**Final kvalitet:** {r['final_quality_score']}%  \n\n"

            # Feedback
            if r.get("final_feedback"):
                details += f"**Final feedback:** {r['final_feedback']}\n\n"

            # Vis hver iteration
            details += "### 🔄 Iterationer:\n\n"
            for iteration in r.get("iterations", []):
                iter_num = iteration["iteration"]
                is_done = "✅ Done" if iteration["is_done"] else "🔄 Fortsætter"
                quality = iteration["verification"].get("quality_score", "N/A")
                corrections = len(iteration["analysis"].get("corrections", []))

                details += f"**Iteration {iter_num}** ({is_done}, Kvalitet: {quality}%)  \n"
                details += f"- Rettelser: {corrections}  \n"
                details += f"- Reasoning: {iteration['reasoning']}  \n\n"

                # Vis remaining issues hvis der er nogen
                remaining = iteration["verification"].get("remaining_issues", [])
                if remaining:
                    details += f"- Resterende problemer: {', '.join(remaining)}  \n\n"

            # Alle rettelser
            all_corrections = r.get("all_corrections", [])
            if all_corrections:
                details += f"### ✏️ Alle rettelser ({len(all_corrections)}):\n\n"
                for i, correction in enumerate(all_corrections, 1):
                    iter_num = correction.get("iteration", "?")
                    details += f"{i}. **{correction.get('type', 'N/A')}** (Iteration {iter_num})\n"
                    details += f"   - Original: `{correction.get('original', 'N/A')}`\n"
                    details += f"   - Rettelse: `{correction.get('correction', 'N/A')}`\n"
                    details += f"   - Forklaring: {correction.get('explanation', 'N/A')}\n\n"

            details += "---\n\n"

        return details

    def save_corrections_handler(self, overwrite: bool):
        """
        Handler for at gemme rettelser (både standard og agentic).
        """
        if not self.current_results:
            return "❌ Ingen resultater at gemme. Kør analyse først."

        try:
            saved_paths = []

            for result in self.current_results:
                file_path = Path(result["file_path"])

                # Tjek om det er agentic eller standard result
                if "final_corrected_text" in result:
                    # Agentic result
                    corrected_text = result["final_corrected_text"]
                else:
                    # Standard result
                    corrected_text = result.get("corrected_text", "")

                if not corrected_text:
                    continue

                # Gem fil
                if overwrite:
                    output_path = file_path
                else:
                    output_path = file_path.parent / f"{file_path.stem}_corrected{file_path.suffix}"

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(corrected_text)

                saved_paths.append(str(output_path))

            if overwrite:
                return f"✅ Gemt {len(saved_paths)} filer (overskrevet originaler)"
            else:
                return f"✅ Gemt {len(saved_paths)} filer med '_corrected' suffix"

        except Exception as e:
            return f"❌ Fejl ved gemning: {str(e)}"

    def create_interface(self):
        """
        Opretter Gradio interface med både standard og agentic mode.
        """
        with gr.Blocks(title="AI Tekstanalyse", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🤖 AI Tekstanalyse")
            gr.Markdown(f"*Provider: {self.llm_provider.get_provider_name()}*")

            with gr.Tabs() as tabs:
                # Standard Mode Tab
                with gr.Tab("📝 Standard Mode"):
                    gr.Markdown("*Hurtig single-pass analyse*")

                    with gr.Row():
                        with gr.Column(scale=2):
                            folder_input_std = gr.Textbox(
                                label="📁 Mappe sti",
                                placeholder="C:\\sti\\til\\dine\\filer",
                                info="Sti til mappen med dokumenter (TXT, PDF, Word)"
                            )

                            with gr.Row():
                                grammatik_check_std = gr.Checkbox(label="Grammatik", value=True)
                                stavning_check_std = gr.Checkbox(label="Stavning", value=True)
                                struktur_check_std = gr.Checkbox(label="Struktur", value=True)
                                klarhed_check_std = gr.Checkbox(label="Klarhed", value=True)

                            analyze_btn_std = gr.Button("🔍 Analyser alle filer", variant="primary", size="lg")
                            status_output_std = gr.Textbox(label="Status", interactive=False)

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 📊 Rapport")
                            report_output_std = gr.Markdown()

                        with gr.Column():
                            gr.Markdown("### 📝 Detaljer")
                            details_output_std = gr.Markdown()

                    with gr.Row():
                        overwrite_check_std = gr.Checkbox(
                            label="Overskriv originale filer (⚠️ ADVARSEL)",
                            value=False,
                            info="Hvis ikke valgt, gemmes med _corrected suffix i samme format"
                        )
                        save_btn_std = gr.Button("💾 Gem alle rettelser", variant="secondary")
                        save_status_std = gr.Textbox(label="Gem status", interactive=False)

                # Agentic Mode Tab
                with gr.Tab("🤖 Agentic Mode (Self-Verifying)"):
                    gr.Markdown("*AI agenten tjekker og forbedrer sit eget arbejde i flere iterationer*")

                    with gr.Row():
                        with gr.Column(scale=2):
                            folder_input_agent = gr.Textbox(
                                label="📁 Mappe sti",
                                placeholder="C:\\sti\\til\\dine\\filer",
                                info="Sti til mappen med dokumenter (TXT, PDF, Word)"
                            )

                            with gr.Row():
                                grammatik_check_agent = gr.Checkbox(label="Grammatik", value=True)
                                stavning_check_agent = gr.Checkbox(label="Stavning", value=True)
                                struktur_check_agent = gr.Checkbox(label="Struktur", value=True)
                                klarhed_check_agent = gr.Checkbox(label="Klarhed", value=True)

                            max_iterations_slider = gr.Slider(
                                minimum=1,
                                maximum=5,
                                value=3,
                                step=1,
                                label="Max iterationer",
                                info="Hvor mange gange AI'en max må forbedre sit arbejde"
                            )

                            analyze_btn_agent = gr.Button("🤖 Analyser med AI Agent", variant="primary", size="lg")
                            status_output_agent = gr.Textbox(label="Status", interactive=False)

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 📊 Rapport")
                            report_output_agent = gr.Markdown()

                        with gr.Column():
                            gr.Markdown("### 📝 Detaljer (med iterationer)")
                            details_output_agent = gr.Markdown()

                    with gr.Row():
                        overwrite_check_agent = gr.Checkbox(
                            label="Overskriv originale filer (⚠️ ADVARSEL)",
                            value=False,
                            info="Hvis ikke valgt, gemmes med _corrected suffix i samme format"
                        )
                        save_btn_agent = gr.Button("💾 Gem alle rettelser", variant="secondary")
                        save_status_agent = gr.Textbox(label="Gem status", interactive=False)

            # Event handlers - Standard Mode
            analyze_btn_std.click(
                fn=self.analyze_folder_handler,
                inputs=[folder_input_std, grammatik_check_std, stavning_check_std,
                       struktur_check_std, klarhed_check_std],
                outputs=[status_output_std, report_output_std, details_output_std]
            )

            save_btn_std.click(
                fn=self.save_corrections_handler,
                inputs=[overwrite_check_std],
                outputs=[save_status_std]
            )

            # Event handlers - Agentic Mode
            analyze_btn_agent.click(
                fn=self.analyze_folder_agentic_handler,
                inputs=[folder_input_agent, grammatik_check_agent, stavning_check_agent,
                       struktur_check_agent, klarhed_check_agent, max_iterations_slider],
                outputs=[status_output_agent, report_output_agent, details_output_agent]
            )

            save_btn_agent.click(
                fn=self.save_corrections_handler,
                inputs=[overwrite_check_agent],
                outputs=[save_status_agent]
            )

        return interface


def create_gui(provider_type: str = "claude", api_key: str = None, model: str = None,
               use_rag: bool = True, style_guide_path: str = "style_guide.md",
               rag_min_guidelines: int = 5, rag_max_guidelines: int = 15):
    """
    Opretter og starter GUI.

    Args:
        provider_type: "claude" eller "openai"
        api_key: API nøgle
        model: Model navn (optional)
        use_rag: Enable RAG system for style guide integration
        style_guide_path: Path to style guide file
        rag_min_guidelines: Minimum number of guidelines to retrieve
        rag_max_guidelines: Maximum number of guidelines to retrieve
    """
    if not api_key:
        raise ValueError("API nøgle er påkrævet")

    # Opret provider
    if provider_type.lower() == "claude":
        provider = ClaudeProvider(api_key, model or "claude-3-5-sonnet-20241022")
    elif provider_type.lower() == "openai":
        provider = OpenAIProvider(api_key, model or "gpt-4o")
    else:
        raise ValueError(f"Ukendt provider type: {provider_type}")

    # Initialize RAG knowledge base if enabled
    knowledge_base = None
    if use_rag and KnowledgeBase:
        try:
            knowledge_base = KnowledgeBase(
                style_guide_path=style_guide_path,
                min_guidelines=rag_min_guidelines,
                max_guidelines=rag_max_guidelines
            )
            print(f"✓ RAG knowledge base initialized: {knowledge_base.get_stats()}")
        except Exception as e:
            print(f"⚠ Warning: Could not initialize RAG system: {e}")
            print("  Continuing without style guide integration...")

    # Opret GUI
    gui = TextAnalysisGUI(provider, knowledge_base)
    interface = gui.create_interface()

    return interface
