# PronounceIt - Uttalsträning med visuell feedback

PronounceIt är en uttalsträningsapplikation byggd med GTK4/Adwaita som ger visuell feedback genom spektrogram och tonhöjdskonturer. Appen stöder uttalsträning för svenska, engelska, tyska och franska.

Designad för **logopeder** och **språkelever**.

## Funktioner

- **Spektrogram-jämförelse** - Se ditt uttal jämfört med referensen sida vid sida
- **Tonhöjdsanalys (F0)** - Visualisering av intonationsmönster i realtid
- **Formantanalys (F1/F2/F3)** - LPC-baserad vokalanalys med fokus på svenska vokaler
- **Uttalspoäng (0-100)** - Kompositpoäng baserad på spektral likhet, tonhöjd och formanter
- **Pedagogisk feedback** - Detaljerad feedback på svenska med artikulationstips
- **Ordlista med IPA** - 60+ ord och fraser med IPA-transkription
- **4 språk** - Svenska, engelska, tyska och franska
- **Framstegsövervakning** - Spåra din förbättring över tid med diagram
- **Svårighetsgrader** - 5 nivåer, från enskilda vokaler till fullständiga meningar
- **Svenska ordaccenter** - Stöd för accent 1 och accent 2

## Skärmdumpsbeskrivning

Appen har tre huvudvyer:
1. **Övning** - Inspelning, spektrogram, tonhöjd och feedback
2. **Ordlista** - Bläddra och filtrera ord per språk och svårighetsgrad
3. **Framsteg** - Diagram över poängutveckling

## Installation

### Systemkrav

- Python 3.10+
- GTK4 och libadwaita
- PortAudio (för PyAudio)

### Ubuntu/Debian

```bash
# Installera systemberoenden
sudo apt install python3-pip python3-gi python3-gi-cairo \
    gir1.2-gtk-4.0 gir1.2-adw-1 portaudio19-dev

# Installera Python-beroenden
pip install -r requirements.txt

# Kör appen
python -m pronounceit
```

### Fedora

```bash
sudo dnf install python3-pip python3-gobject gtk4 libadwaita \
    portaudio-devel

pip install -r requirements.txt
python -m pronounceit
```

### Arch Linux

```bash
sudo pacman -S python-pip python-gobject gtk4 libadwaita portaudio

pip install -r requirements.txt
python -m pronounceit
```

### macOS (med Homebrew)

```bash
brew install gtk4 libadwaita portaudio pygobject3

pip install -r requirements.txt
python -m pronounceit
```

### Installation som paket

```bash
pip install -e .
pronounceit
```

## Användning

1. Starta appen: `python -m pronounceit`
2. Gå till **Ordlista** och välj ett ord
3. Tryck **Spela in** och uttala ordet
4. Granska spektrogram, tonhöjdskontur och poäng
5. Läs feedbacken och försök igen
6. Följ din framsteg i **Framsteg**-fliken

## Projektstruktur

```
pronounceit/
├── application.py          # Gtk.Application
├── window.py               # Huvudfönster med ViewStack
├── audio/
│   ├── recorder.py         # PyAudio mikrofon-inspelning (trådad)
│   ├── analyzer.py         # Spektrogram (scipy.signal)
│   ├── pitch_tracker.py    # F0-extraktion (autokorrelation)
│   ├── formant.py          # Formantanalys (LPC)
│   └── comparator.py       # DTW-jämförelse
├── scoring/
│   ├── scorer.py           # Kompositpoängsättning
│   ├── feedback.py         # Pedagogisk feedback (svenska)
│   └── criteria.py         # Formanttargets per språk
├── ui/
│   ├── recording_view.py   # Inspelningskontroller + vågform
│   ├── spectrogram_view.py # Matplotlib-spektrogram i GTK4
│   ├── pitch_view.py       # Tonhöjdskontur
│   ├── feedback_view.py    # Poäng och feedback
│   ├── word_browser_view.py# Ordlista med filtrering
│   └── progress_view.py    # Framstegsdiagram
├── data/
│   ├── database.py         # SQLite (ord + framsteg)
│   └── models.py           # Dataklasser
├── i18n/                   # Gettext lokalisering
└── utils/
    ├── audio_utils.py      # WAV-hantering
    └── config.py           # JSON-konfiguration
```

## Teknisk arkitektur

### Ljudanalys-pipeline

1. **Inspelning** - PyAudio i bakgrundstråd med `GLib.idle_add()`-brygga
2. **Spektrogram** - `scipy.signal.spectrogram()` med Hann-fönster
3. **Tonhöjd** - Autokorrelationsbaserad F0-detektor (80-400 Hz)
4. **Formanter** - LPC via `scipy.signal.lpc()` → rotanalys
5. **Jämförelse** - Dynamic Time Warping med Sakoe-Chiba-band
6. **Poäng** - Viktad kombination: 40% spektral + 30% tonhöjd + 30% formant

### Lokalisering

Appen använder gettext med svenska som huvudspråk och engelska som fallback.
Översättningsfiler finns i `po/`-katalogen.

## Beroenden

| Paket | Användning |
|-------|-----------|
| PyGObject | GTK4/Adwaita UI |
| PyAudio | Mikrofon-inspelning |
| NumPy | Numerisk beräkning |
| SciPy | FFT, spektrogram, LPC |
| Matplotlib | Visuell feedback (inbäddad i GTK4) |

## Licens

MIT License - se [LICENSE](LICENSE)
