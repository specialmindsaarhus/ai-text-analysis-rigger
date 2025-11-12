# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Tekstanalyse Tool er et Gradio-baseret GUI-værktøj til tekstanalyse med AI. Systemet understøtter både Claude AI og OpenAI og tilbyder to analyse-modes: Standard (single-pass) og Agentic (self-verifying med iterativ forbedring).

**Understøttede dokumentformater:**
- Plain Text (.txt)
- PDF (.pdf)
- Microsoft Word (.docx, .doc)

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env to add CLAUDE_API_KEY or OPENAI_API_KEY

# Run the application
python main.py
```

The GUI opens at `http://127.0.0.1:7860`

## Context Menu Integration (Windows)

The project includes Windows integration for analyzing files directly from File Explorer without starting the GUI:

### Files
- `analyze_cli.py`: CLI wrapper that accepts file paths and runs analysis
- `analyze_file.bat`: Batch wrapper for launching Python CLI
- `INSTALL_SENDTO.bat`: One-click installer for "Send To" menu integration
- `CREATE_DESKTOP_SHORTCUT.bat`: Creates desktop shortcut for drag-and-drop

### Usage Methods

**1. Send To Menu (Recommended):**
- Run `INSTALL_SENDTO.bat` once to install
- Right-click any TXT/PDF/Word file -> Send to -> "AI Text Analyze"
- Corrected file saved with `_corrected` suffix

**2. Desktop Shortcut:**
- Run `CREATE_DESKTOP_SHORTCUT.bat` to create shortcut
- Drag and drop files onto desktop shortcut
- Supports multiple files and folders

**3. Command Line:**
```bash
python analyze_cli.py "path/to/file.txt"
python analyze_cli.py "file1.txt" "file2.pdf" "file3.docx"
```

All methods use the same analysis pipeline as the GUI but run in console mode. See `CONTEXT_MENU_GUIDE.md` for detailed instructions.

## Configuration

All configuration is managed through `config.py` and `.env`:

- `LLM_PROVIDER`: Set to "claude" or "openai"
- `CLAUDE_API_KEY` / `OPENAI_API_KEY`: Required API keys
- `CLAUDE_MODEL` / `OPENAI_MODEL`: LLM model to use
- `GRADIO_SERVER_PORT`: Default 7860

The `Config` class provides `get_api_key()`, `get_model()`, and `validate()` methods to manage configuration programmatically.

## Core Architecture

### Document Reader Utility

**DocumentReader** (`src/document_reader.py`):
- Unified interface for reading multiple document formats
- **Reading capabilities:**
  - TXT: UTF-8 with Latin-1 fallback
  - PDF: Multi-page text extraction using `pypdf.PdfReader`
  - Word: Paragraph and table extraction using `python-docx`
- **Writing capabilities:**
  - TXT: Direct text output
  - Word: Paragraph-based formatting
  - PDF: Converts to TXT (PDF generation not implemented)
- **Key methods:**
  - `read_file(path) -> (text, format)`: Returns content and detected format
  - `write_file(path, content, format)`: Writes content in specified format
  - `get_supported_extensions()`: Returns list of supported file extensions
  - `is_supported(path)`: Checks if file format is supported

### Provider Pattern for LLM Abstraction

The system uses an abstract provider pattern to support multiple LLM backends:

**Base Interface** (`src/llm_providers/base_provider.py`):
- `BaseLLMProvider` defines the contract all providers must implement
- Key method: `analyze_text(text, parameters) -> Dict` returns structured analysis with:
  - `original_text`: Input text
  - `corrected_text`: AI-corrected version
  - `corrections`: List of changes with type, original, correction, explanation
  - `feedback`: General quality feedback

**Provider Implementations**:
- `ClaudeProvider`: Uses Anthropic API with `anthropic.messages.create()`
- `OpenAIProvider`: Uses OpenAI API with `client.chat.completions.create()`

Both providers construct prompts that request JSON-formatted responses and handle JSON parsing (including markdown code block stripping).

### Two Analysis Modes

**1. Standard Mode** (`TextAnalyzer` in `src/text_analyzer.py`):
- Batch processing of all supported document formats in a folder
- Single LLM call per file
- Uses `DocumentReader` for file I/O
- Key methods:
  - `find_files(folder)`: Finds all supported documents (replaces old `find_txt_files()`)
  - `read_file(path) -> (text, format)`: Reads document content
  - `analyze_file()`: Analyzes single file, stores format in result dict
  - `analyze_folder()`: Batch processes all files with progress tracking
  - `save_all_corrections()`: Saves corrections in original format

**2. Agentic Mode** (`AgenticAnalyzer` in `src/agentic_analyzer.py`):
- Implements a self-verifying loop where the LLM acts as an autonomous agent
- Uses `DocumentReader` for multi-format document handling
- **Three-step process per iteration**:
  1. **THINK**: `think_and_analyze()` - LLM analyzes and corrects text
  2. **USE TOOLS**: `read_document()`, `write_document()` - File I/O operations (multi-format)
  3. **VERIFY**: `verify_quality()` - LLM evaluates its own corrections and assigns quality score (0-100)
- **Loop continuation logic**: If quality < threshold OR issues remain, iterate with corrected text as new input
- **Max iterations**: Configurable (default 3) to prevent infinite loops
- **Format preservation**: Stores original file format and uses it when saving results
- **Output structure**: Returns all iterations with their analysis + verification results, plus final corrected text and aggregated corrections

The agentic loop leverages the LLM twice per iteration: once for correction, once for self-assessment. This enables iterative refinement until quality criteria are met.

### Token-Efficient Style Guide Integration (RAG)

To incorporate business-specific terminology and writing styles without high token costs, the system will implement a Retrieval-Augmented Generation (RAG) pipeline.

**Problem**: Naively injecting a full style guide into every LLM prompt is inefficient and costly, especially as the guide grows.

**Solution**: A RAG-based approach that retrieves only the most relevant style rules for a given text and injects them into the prompt. This is more scalable, token-efficient, and provides targeted context to the AI.

**Architecture**:
- **Knowledge Source**: A `style_guide.md` file in the project root will store all custom rules, terminology, and style preferences.
- **New Dependencies**:
  - `sentence-transformers`: To generate vector embeddings for the style guide rules.
  - `faiss-cpu`: A library for efficient similarity search that will serve as the local vector database.
- **New Module (`src/knowledge_base.py`)**:
  - A `KnowledgeBase` class will be responsible for the RAG pipeline.
  - **On Startup**: It will load `style_guide.md`, split it into logical chunks (e.g., by rule or paragraph), and create a searchable FAISS vector index stored in memory.
  - **On-Demand Retrieval**: It will provide a method `get_relevant_rules(text, top_k=3)` that takes the document text, searches the index for the most similar rules, and returns them.
- **Integration**:
  - The `KnowledgeBase` instance will be created at application startup.
  - Before analysis, both `TextAnalyzer` and `AgenticAnalyzer` will call `get_relevant_rules()` with the document's content.
  - The retrieved rules will be dynamically formatted and inserted into the LLM prompt, ensuring the AI has the precise, relevant context needed for its task.

This design provides a powerful way to customize the AI's behavior without the high overhead of a full client-server architecture, making it ideal for a desktop application.

### GUI Implementation

**Dual-Tab Interface** (`src/gui.py`):
- Built with Gradio Blocks API
- Two tabs: "Standard Mode" and "Agentic Mode (Self-Verifying)"
- Both share common parameters (grammatik, stavning, struktur, klarhed checkboxes)
- Agentic tab adds `max_iterations` slider (1-5)

**Key GUI Methods**:
- `analyze_folder_handler()`: Standard mode batch processing
- `analyze_folder_agentic_handler()`: Agentic mode with iteration tracking
- `generate_report()` / `generate_agentic_report()`: Summary statistics
- `generate_details()` / `generate_agentic_details()`: Detailed correction listings
  - Agentic details show per-iteration progress with quality scores and reasoning
- `save_corrections_handler()`: Unified save logic for both modes (detects result format)

Progress callbacks use Gradio's `gr.Progress()` to show real-time status during analysis.

## Adding a New LLM Provider

1. Create new provider class in `src/llm_providers/` inheriting from `BaseLLMProvider`
2. Implement `analyze_text()` and `get_provider_name()` methods
3. Ensure `analyze_text()` returns dict with: `original_text`, `corrected_text`, `corrections`, `feedback`
4. Add provider initialization logic to `config.py` `get_api_key()` and `get_model()`
5. Update `src/gui.py` `create_gui()` function to instantiate new provider
6. Add API key environment variable to `.env.example`

## Important Implementation Details

### JSON Response Handling

Both Claude and OpenAI providers strip markdown code fences from LLM responses:
```python
if response_text.startswith("```json"):
    response_text = response_text.replace("```json", "").replace("```", "").strip()
```

This is critical as LLMs often wrap JSON in ```json blocks.

### Agentic Mode Quality Threshold

The `verify_quality()` method asks the LLM to score quality 0-100 and provide:
- `is_done`: Boolean termination signal
- `quality_score`: Numeric assessment
- `reasoning`: Explanation of decision
- `remaining_issues`: Problems still present
- `suggestions`: Potential improvements

The loop terminates when `is_done=true` OR `max_iterations` is reached.

### File Format Handling

**Multiple Format Support:**
- **TXT files**: UTF-8 with Latin-1 fallback on `UnicodeDecodeError`
- **PDF files**: Uses `pypdf.PdfReader` to extract text from all pages
- **Word files**: Uses `python-docx` to extract paragraphs and tables

**Format Detection:**
The `DocumentReader.read_file()` method returns both content and detected format as a tuple: `(text, format)`. This format is stored in analysis results and used during save operations.

### Save Behavior

Files can be saved with overwrite or `_corrected` suffix, **preserving original format**:
- `overwrite=True`: Replaces original file in same format
- `overwrite=False`: Creates `filename_corrected.ext` (where ext = original extension)
- Format preservation: TXT→TXT, PDF→TXT (PDF generation not supported), DOCX→DOCX

## Dependencies

**Core Dependencies:**
- `gradio>=5.49.1`: Web UI framework
- `anthropic>=0.72.1`: Claude AI API client
- `openai>=2.7.2`: OpenAI AI API client
- `python-dotenv==1.0.0`: Environment variable management

**Document Processing:**
- `pypdf>=6.2.0`: PDF text extraction
- `python-docx>=1.2.0`: Word document handling

**RAG / Vector Search:**
- `sentence-transformers>=2.2.2`: For generating vector embeddings.
- `faiss-cpu>=1.7.4`: For efficient local vector similarity search.

**Python 3.13 Compatibility:**
- `audioop-lts>=0.2.2`: Required for Python 3.13+ (audioop module removed from stdlib)

All dependencies are listed in `requirements.txt`. Install with:
```bash
pip install -r requirements.txt
```

## Testing

Test files are located in `test_files/`:
- `test1_grammatik.txt`: Danish grammar errors
- `test2_stavning.txt`: Spelling mistakes
- `test3_struktur.txt`: Poor text structure

To test the system:
1. Ensure `.env` is configured with valid API key
2. Run `python main.py`
3. Point folder input to `test_files/` directory
4. Test with multiple document formats (TXT, PDF, Word)
5. Compare Standard vs Agentic mode results
