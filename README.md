# AI Tekstanalyse Tool

Et simpelt GUI-værktøj til at analysere og rette tekstfiler med AI. Værktøjet bruger Claude AI eller OpenAI til at finde og rette grammatiske fejl, stavefejl og give feedback på tekststruktur og klarhed.

## Features

- **Simpelt GUI**: Minimalt antal klik - vælg mappe, klik analyse, gem
- **Multiple input metoder**:
  - **GUI Mode**: Browser-baseret interface til batch processing
  - **Context Menu**: Højreklik på fil -> "Send to" -> "AI Text Analyze" (Windows)
  - **Desktop Shortcut**: Drag-and-drop filer på skrivebordet
  - **Command Line**: `python analyze_cli.py filnavn.txt`
- **To analyse modes**:
  - **Standard Mode**: Hurtig single-pass analyse
  - **Agentic Mode**: AI agenten verificerer og forbedrer sit eget arbejde i flere iterationer
- **Flere dokumentformater**: TXT, PDF, og Word (DOCX/DOC)
- **Batch processing**: Analyser alle dokumenter i en mappe på én gang
- **Fleksibel AI provider**: Nem switching mellem Claude AI og OpenAI
- **Konfigurerbare parametre**: Vælg hvad der skal analyseres (grammatik, stavning, struktur, klarhed)
- **Detaljeret feedback**: Se alle rettelser med forklaringer
- **Self-verifying AI**: Agentic mode bruger LLM som "thinking brain" til at tjekke kvalitet
- **Sikker lagring**: Vælg mellem at overskrive eller gemme som nye filer

## Installation

### 1. Klon eller download projektet

```bash
cd ai-text-analysis-rigger
```

### 2. Opret virtual environment (anbefalet)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Installer dependencies

```bash
pip install -r requirements.txt
```

### 4. Konfigurer API keys

Kopier `.env.example` til `.env`:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Rediger `.env` og tilføj din API key:

```env
# For Claude AI (anbefalet)
LLM_PROVIDER=claude
CLAUDE_API_KEY=sk-ant-api03-xxx...

# ELLER for OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxx...
```

**Hvordan får jeg en API key?**

- **Claude AI**: Gå til https://console.anthropic.com/ og opret en API key
- **OpenAI**: Gå til https://platform.openai.com/api-keys og opret en API key

## Brug

### Start applikationen

```bash
python main.py
```

Dette åbner et browser-vindue med GUI'en på `http://127.0.0.1:7860`

### Workflow

#### Standard Mode (hurtig analyse)

1. **Vælg "Standard Mode" tab**
2. **Vælg mappe**: Indtast stien til mappen med dine dokumenter (TXT, PDF, Word)
3. **Vælg parametre**: Vælg hvad der skal analyseres (grammatik, stavning, etc.)
4. **Klik "Analyser alle filer"**: Se resultaterne
5. **Gem rettelser**: Klik "Gem alle rettelser" for at gemme de rettede filer (i samme format)

#### Agentic Mode (self-verifying AI)

1. **Vælg "Agentic Mode" tab**
2. **Vælg mappe**: Indtast stien til mappen med dine dokumenter (TXT, PDF, Word)
3. **Vælg parametre**: Vælg hvad der skal analyseres
4. **Sæt max iterationer**: Hvor mange gange AI'en max må forbedre sit arbejde (1-5)
5. **Klik "Analyser med AI Agent"**: AI'en vil nu:
   - Analysere teksten (LLM som "thinking brain")
   - Verificere sit eget arbejde
   - Iterere indtil kvaliteten er god nok eller max iterationer er nået
6. **Gennemse iterationer**: Se hvordan AI'en forbedrede sit arbejde over tid
7. **Gem rettelser**: Klik "Gem alle rettelser"

**Hvornår bruge hvilken mode?**
- **Standard Mode**: Hurtig feedback, mindre kritiske dokumenter
- **Agentic Mode**: Højere kvalitet, vigtige dokumenter der kræver grundig gennemlæsning

### Skift mellem AI providers

Rediger `.env` filen:

```env
# Brug Claude AI
LLM_PROVIDER=claude

# ELLER brug OpenAI
LLM_PROVIDER=openai
```

Genstart applikationen for at anvende ændringen.

## Windows Context Menu Integration

For at bruge AI Text Analysis direkte fra File Explorer (uden at starte GUI'en):

### Installation af "Send To" menu (Anbefalet)

1. Dobbeltklik på `INSTALL_SENDTO.bat`
2. Vent på installationen er færdig (2-3 sekunder)

**Brug:**
- Højreklik på en fil (TXT, PDF, eller Word)
- Vælg **Send to** > **AI Text Analyze**
- Se resultater i console vinduet
- Rettet fil gemmes med `_corrected` suffix

### Installation af Desktop Shortcut

1. Dobbeltklik på `CREATE_DESKTOP_SHORTCUT.bat`
2. En genvej "AI Text Analyze" oprettes på skrivebordet

**Brug:**
- Træk en eller flere filer til genvejen på skrivebordet
- Se resultater i console vinduet
- Rettede filer gemmes med `_corrected` suffix

### Command Line Brug

```bash
# Analyser en enkelt fil
python analyze_cli.py "sti\til\fil.txt"

# Analyser flere filer
python analyze_cli.py "fil1.txt" "fil2.pdf" "fil3.docx"
```

**Note:** Context menu integration bruger Standard Mode med alle parametre aktiveret. For Agentic Mode eller custom parametre, brug GUI'en (`python main.py`).

Se `CONTEXT_MENU_GUIDE.md` for detaljeret guide og troubleshooting.

## Projekt struktur

```
ai-text-analysis-rigger/
├── src/
│   ├── llm_providers/
│   │   ├── __init__.py
│   │   ├── base_provider.py      # Abstrakt interface
│   │   ├── claude_provider.py    # Claude implementation
│   │   └── openai_provider.py    # OpenAI implementation
│   ├── text_analyzer.py          # Standard tekstanalyse logik
│   ├── agentic_analyzer.py       # Agentic self-verifying analyzer
│   ├── document_reader.py        # Multi-format dokument læsning (TXT/PDF/Word)
│   └── gui.py                    # Gradio GUI
├── config.py                     # Konfiguration
├── main.py                       # Entry point (GUI)
├── analyze_cli.py                # CLI entry point (context menu)
├── analyze_file.bat              # Batch wrapper til CLI
├── INSTALL_SENDTO.bat            # Installer til "Send To" menu
├── CREATE_DESKTOP_SHORTCUT.bat   # Installer til desktop shortcut
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variabler eksempel
├── README.md                     # Denne fil
├── CONTEXT_MENU_GUIDE.md         # Guide til context menu integration
├── CLAUDE.md                     # Teknisk dokumentation
└── GIT_SNAPSHOTS.md              # Git version control guide
```

## Tilføj ny AI provider

Systemet er designet til at være let at udvide. For at tilføje en ny AI provider:

1. Opret ny fil i `src/llm_providers/`, f.eks. `gemini_provider.py`
2. Implementer `BaseLLMProvider` interfacet
3. Tilføj provider til `config.py`
4. Opdater GUI til at understøtte den nye provider

Eksempel:

```python
from .base_provider import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # Initialize Gemini client

    def analyze_text(self, text: str, parameters: Dict[str, bool]) -> Dict:
        # Implement analysis logic
        pass

    def get_provider_name(self) -> str:
        return "Google Gemini"
```

## Hvordan virker Agentic Mode?

Agentic Mode implementerer et intelligent loop-system hvor AI'en fungerer som en autonom agent:

### Agentic Loop (3-trins proces)

```
┌─────────────────────────────────────┐
│ 1. THINK (LLM som "thinking brain") │
│    - Analyser teksten               │
│    - Lav rettelser                  │
│    - Generer feedback               │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ 2. USE TOOLS                        │
│    - Læs dokument (read tool)       │
│    - Skriv rettelser (write tool)   │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ 3. VERIFY (Self-check)              │
│    - Er alle fejl rettet?           │
│    - Er kvaliteten god nok?         │
│    - Giv kvalitets-score (0-100%)   │
└─────────────────────────────────────┘
                 ↓
         ┌───────────────┐
         │ Done? (>80%)  │
         └───────────────┘
            /          \
          Ja            Nej
           │             │
         STOP      Loop tilbage til 1
                   (med feedback)
```

### Fordele ved Agentic Mode

- **Højere kvalitet**: AI'en tjekker og forbedrer sit eget arbejde
- **Selvstændig**: Fortsætter indtil kvalitetsmålet er nået
- **Transparent**: Se alle iterationer og AI'ens "tankeproces"
- **Adaptiv**: Lærer af sine egne fejl mellem iterationer

### Eksempel på Agentic Loop

**Iteration 1:**
- AI finder 5 grammatiske fejl
- Verificering: Kvalitet 60% - "Stadig 2 stavefejl tilbage"
- → Fortsætter til iteration 2

**Iteration 2:**
- AI retter de 2 stavefejl
- Verificering: Kvalitet 85% - "Teksten er nu god"
- → Done! ✅

## Troubleshooting

### "API nøgle ikke sat" fejl
- Tjek at `.env` filen eksisterer
- Tjek at API key'en er korrekt indtastet
- Tjek at `LLM_PROVIDER` matcher den provider du har en key til

### "Ingen understøttede dokumenter fundet"
- Tjek at mappen indeholder TXT, PDF eller Word filer
- Tjek at stien er korrekt (absolut sti anbefales)
- Understøttede formater: .txt, .pdf, .docx, .doc

### Import errors
- Sørg for at virtual environment er aktiveret
- Kør `pip install -r requirements.txt` igen

## Licens

MIT

## Support

For spørgsmål eller problemer, opret et issue i projektet.
