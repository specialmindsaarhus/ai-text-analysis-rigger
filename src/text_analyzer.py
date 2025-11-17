import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .llm_providers import BaseLLMProvider
from .document_reader import DocumentReader

try:
    from .knowledge_base import KnowledgeBase
except ImportError:
    KnowledgeBase = None


class TextAnalyzer:
    """
    Håndterer batch analyse af tekstfiler.
    """

    def __init__(self, llm_provider: BaseLLMProvider, knowledge_base: Optional['KnowledgeBase'] = None):
        self.llm_provider = llm_provider
        self.doc_reader = DocumentReader()
        self.knowledge_base = knowledge_base

    def find_files(self, folder_path: str) -> List[Path]:
        """
        Finder alle understøttede dokumentfiler i en given mappe (inkl. undermapper).
        Understøtter: .txt, .pdf, .docx, .doc
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Mappen '{folder_path}' findes ikke")

        files = []
        supported_extensions = DocumentReader.get_supported_extensions()

        for ext in supported_extensions:
            files.extend(list(folder.rglob(f"*{ext}")))

        return sorted(files)

    def find_txt_files(self, folder_path: str) -> List[Path]:
        """
        Finder alle .txt filer i en given mappe (inkl. undermapper).
        Deprecated: Brug find_files() i stedet.
        """
        return self.find_files(folder_path)

    def read_file(self, file_path: Path) -> Tuple[str, str]:
        """
        Læser indhold fra en fil (understøtter TXT, PDF, Word).

        Returns:
            Tuple af (text, format)
        """
        return self.doc_reader.read_file(file_path)

    def save_corrected_file(self, file_path: Path, corrected_text: str,
                           file_format: str = 'txt', overwrite: bool = False):
        """
        Gemmer rettet tekst til fil.
        Hvis overwrite=False, gemmes til ny fil med _corrected suffix.
        """
        if overwrite:
            output_path = file_path
        else:
            output_path = file_path.parent / f"{file_path.stem}_corrected{file_path.suffix}"

        self.doc_reader.write_file(output_path, corrected_text, file_format)

        return output_path

    def analyze_file(self, file_path: Path, parameters: Dict[str, bool]) -> Dict:
        """
        Analyserer en enkelt fil.
        """
        text, file_format = self.read_file(file_path)

        # Get relevant style guidelines if RAG is enabled
        style_guidelines = ""
        if self.knowledge_base:
            style_guidelines = self.knowledge_base.get_relevant_guidelines(text)

        result = self.llm_provider.analyze_text(text, parameters, style_guidelines)
        result["file_path"] = str(file_path)
        result["file_name"] = file_path.name
        result["file_format"] = file_format
        return result

    def analyze_folder(self, folder_path: str, parameters: Dict[str, bool],
                      progress_callback=None) -> List[Dict]:
        """
        Analyserer alle understøttede dokumentfiler i en mappe.

        Args:
            folder_path: Sti til mappen
            parameters: Analyse parametre
            progress_callback: Optional callback funktion der kaldes med (current, total, filename)

        Returns:
            Liste af analyse resultater
        """
        txt_files = self.find_files(folder_path)

        if not txt_files:
            return []

        results = []
        total = len(txt_files)

        for i, file_path in enumerate(txt_files, 1):
            if progress_callback:
                progress_callback(i, total, file_path.name)

            result = self.analyze_file(file_path, parameters)
            results.append(result)

        return results

    def save_all_corrections(self, results: List[Dict], overwrite: bool = False) -> List[str]:
        """
        Gemmer alle rettelser til filer.

        Returns:
            Liste af gemte fil-stier
        """
        saved_paths = []

        for result in results:
            if result.get("corrected_text"):
                file_path = Path(result["file_path"])
                file_format = result.get("file_format", "txt")
                output_path = self.save_corrected_file(
                    file_path,
                    result["corrected_text"],
                    file_format,
                    overwrite
                )
                saved_paths.append(str(output_path))

        return saved_paths
