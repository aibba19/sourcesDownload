# YouTube Downloader + Metadata PPTX (MVP)

Tool Python con UI essenziale per:
1. scaricare uno o più video YouTube in MP4 in una cartella scelta;
2. generare/aggiornare un PowerPoint con metadati e link cliccabili a video/canale.

## Requisiti
- Python 3.11+
- `ffmpeg` installato e disponibile nel PATH (necessario in alcuni casi per merge audio/video)

## Installazione
```bash
python -m venv .venv
source .venv/bin/activate  # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Avvio
```bash
python -m app.main
```

## Cosa fa il tool
- Accetta in input:
  - un link YouTube dalla UI
  - **oppure** un file Word `.docx` con tabella, dove la seconda colonna può contenere link YouTube
  - (puoi anche usarli entrambi nella stessa esecuzione)
- Per i file Word:
  - cerca i link YouTube nella seconda colonna di tutte le tabelle
  - per ogni link trovato crea una slide con titolo `Slide X` dove `X` è il numero di riga nella tabella
  - puoi trascinare il file `.docx` direttamente nell'area drag&drop della UI
- Estrae metadati via `yt-dlp`
- Scarica MP4 (best <= 1080p)
- Crea/aggiorna un PPTX con una nuova slide per ogni video:
  - se usi un file Word: `fonti-<nomefileword>.pptx`
  - se usi solo URL manuale: `fonti.pptx`
  - nome file
  - titolo
  - link video
  - nome canale
  - link canale (da `uploader_url` o fallback su `channel_id`)
  - data download UTC

## Note legali
Usa il tool nel rispetto dei termini di YouTube e delle normative sul copyright.
