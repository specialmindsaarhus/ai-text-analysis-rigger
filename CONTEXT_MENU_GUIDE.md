# Kontekstmenu Integration Guide

Denne guide viser hvordan du kan bruge AI Text Analysis direkte fra Windows Stifinder uden at starte GUI'en.

## Metode 1: "Send To" Menu (Anbefalet)

### Installation
1. Dobbeltklik på `INSTALL_SENDTO.bat`
2. Vent på installationen er færdig (tager 2-3 sekunder)
3. Du vil nu se "AI Text Analyze" i din "Send to" menu

### Brug
1. Højreklik på en fil (TXT, PDF, eller Word dokument)
2. Vælg **Send to** > **AI Text Analyze**
3. Et console vindue åbner og viser analyse progress
4. Når analysen er færdig, tryk Enter for at lukke vinduet
5. Den rettede fil gemmes med `_corrected` suffix i samme mappe

### Afinstallation
- Gå til `%APPDATA%\Microsoft\Windows\SendTo`
- Slet genvejen "AI Text Analyze.lnk"

---

## Metode 2: Desktop Shortcut (Drag-and-Drop)

### Installation
1. Dobbeltklik på `CREATE_DESKTOP_SHORTCUT.bat`
2. En genvej "AI Text Analyze" oprettes på dit skrivebord

### Brug
1. Træk en eller flere filer fra File Explorer
2. Slip dem på "AI Text Analyze" genvejen på skrivebordet
3. Console vindue åbner og analyserer alle filer
4. Rettede filer gemmes med `_corrected` suffix

### Afinstallation
- Slet genvejen fra dit skrivebord

---

## Metode 3: Kommandolinje (Avanceret)

### Brug
Åbn Command Prompt eller PowerShell i projekt mappen:

```bash
# Analyser en enkelt fil
python analyze_cli.py "sti\til\fil.txt"

# Analyser flere filer
python analyze_cli.py "fil1.txt" "fil2.pdf" "fil3.docx"

# Eller brug batch wrapperen
analyze_file.bat "fil1.txt" "fil2.txt"
```

### Output
- Console output viser antal rettelser og de første 3 rettelser for hver fil
- Rettede filer gemmes automatisk med `_corrected` suffix
- Originale filer bliver IKKE overskrevet

---

## Understøttede Filformater

- **TXT**: Plain text filer (UTF-8, Latin-1)
- **PDF**: PDF dokumenter (kun tekst, ingen scannede billeder)
- **Word**: DOCX og DOC filer

---

## Analyse Parametre

Alle rettelser er aktiveret som standard:
- ✅ **Grammatik**: Korrigerer grammatiske fejl
- ✅ **Stavning**: Retter stavefejl
- ✅ **Struktur**: Forbedrer tekststruktur
- ✅ **Klarhed**: Forbedrer læsbarhed og klarhed

(For at ændre disse parametre skal du bruge GUI'en med `python main.py`)

---

## Fejlfinding

### "Python er ikke installeret eller ikke i PATH"
- Installer Python fra https://www.python.org/downloads/
- Husk at vælge "Add Python to PATH" under installation
- Genstart computeren efter installation

### "API key fejl" eller "Authentication error"
- Tjek at din `.env` fil indeholder en valid API key
- Sørg for at `LLM_PROVIDER` er sat korrekt (`claude` eller `openai`)
- Tjek at din API key har tilstrækkelig kredit

### "Quota exceeded"
- Din OpenAI eller Claude konto har ikke mere kredit
- Tilføj kredit til din konto eller brug en anden provider

### "Filformat ikke understøttet"
- Kun TXT, PDF, og Word (DOCX/DOC) filer understøttes
- For andre formater, konverter først til et understøttet format

---

## Tips og Tricks

1. **Batch Processing**: Du kan sende flere filer på samme tid til "Send To" menuen ved at markere dem alle og derefter bruge "Send to"

2. **Desktop Shortcut**: Genvejen på skrivebordet accepterer også mapper - slip en hel mappe på genvejen for at analysere alle filer i mappen

3. **Backup**: Originale filer bliver aldrig overskrevet - de rettede filer får `_corrected` suffix

4. **Git Snapshots**: Brug `git commit` regelmæssigt for at gemme snapshots af dit arbejde (se `GIT_SNAPSHOTS.md`)

---

## Se også

- `README.md` - Hovedprojekt dokumentation
- `CLAUDE.md` - Teknisk dokumentation
- `GIT_SNAPSHOTS.md` - Guide til Git version control
- `main.py` - Start GUI for batch analyse af hele mapper
