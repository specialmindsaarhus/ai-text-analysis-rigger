"""
CLI wrapper for analyzing files from context menu or command line.
Usage: python analyze_cli.py <file_path> [file_path2] [...]
"""

import sys
from pathlib import Path
from config import Config
from src.llm_providers import ClaudeProvider, OpenAIProvider
from src.text_analyzer import TextAnalyzer


def main():
    # Check if files provided
    if len(sys.argv) < 2:
        print("Fejl: Ingen filer specificeret")
        print("Brug: python analyze_cli.py <fil_sti> [fil_sti2] [...]")
        input("\nTryk Enter for at lukke...")
        sys.exit(1)

    # Load config
    try:
        config = Config()
        config.validate()
    except ValueError as e:
        print(f"Konfigurationsfejl: {e}")
        print("\nTjek din .env fil og sikr at API nogler er sat korrekt.")
        input("\nTryk Enter for at lukke...")
        sys.exit(1)

    # Create LLM provider
    try:
        if config.LLM_PROVIDER.lower() == "claude":
            provider = ClaudeProvider(config.CLAUDE_API_KEY, config.CLAUDE_MODEL)
        elif config.LLM_PROVIDER.lower() == "openai":
            provider = OpenAIProvider(config.OPENAI_API_KEY, config.OPENAI_MODEL)
        else:
            raise ValueError(f"Ukendt LLM provider: {config.LLM_PROVIDER}")

        print(f"Bruger: {provider.get_provider_name()}")
        print("-" * 50)
    except Exception as e:
        print(f"Fejl ved oprettelse af LLM provider: {e}")
        input("\nTryk Enter for at lukke...")
        sys.exit(1)

    # Create analyzer
    analyzer = TextAnalyzer(provider)

    # Default parameters (analyze everything)
    parameters = {
        "grammatik": True,
        "stavning": True,
        "struktur": True,
        "klarhed": True
    }

    # Process each file
    file_paths = [Path(arg) for arg in sys.argv[1:]]
    total_files = len(file_paths)

    print(f"\nAnalyserer {total_files} fil(er)...\n")

    results = []
    for i, file_path in enumerate(file_paths, 1):
        print(f"[{i}/{total_files}] Analyserer: {file_path.name}")

        if not file_path.exists():
            print(f"  FEJL: Filen findes ikke!")
            continue

        if file_path.suffix.lower() not in ['.txt', '.pdf', '.docx', '.doc']:
            print(f"  FEJL: Filformat ikke understoettet (kun TXT, PDF, DOCX)")
            continue

        try:
            # Analyze file
            result = analyzer.analyze_file(file_path, parameters)
            results.append(result)

            # Display results
            corrections = result.get("corrections", [])
            print(f"  Fundet: {len(corrections)} rettelser")

            if corrections:
                print(f"  Forste 3 rettelser:")
                for j, corr in enumerate(corrections[:3], 1):
                    print(f"    {j}. {corr.get('type', 'N/A')}: '{corr.get('original', 'N/A')}' -> '{corr.get('correction', 'N/A')}'")

            # Save corrected file
            if result.get("corrected_text"):
                output_path = analyzer.save_corrected_file(
                    file_path,
                    result["corrected_text"],
                    result.get("file_format", "txt"),
                    overwrite=False
                )
                print(f"  Gemt til: {output_path.name}")

        except Exception as e:
            print(f"  FEJL: {str(e)}")
            continue

        print()

    # Summary
    print("-" * 50)
    print(f"\nFaerdig! Analyseret {len(results)} af {total_files} filer.")
    total_corrections = sum(len(r.get("corrections", [])) for r in results)
    print(f"Total rettelser: {total_corrections}")

    input("\nTryk Enter for at lukke...")


if __name__ == "__main__":
    main()
