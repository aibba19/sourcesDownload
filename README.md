# YouTube Downloader + Metadata PPTX (MVP)

Tool Python con UI essenziale per:
1. scaricare un video YouTube in MP4 in una cartella scelta;
2. generare un PowerPoint con metadati e link cliccabili a video/canale.

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
- Valida URL YouTube (`youtube.com`, `youtu.be`)
- Estrae metadati via `yt-dlp`
- Scarica MP4 (best <= 1080p)
- Crea/aggiorna `fonti.pptx` con una nuova slide per ogni video:
  - nome file
  - titolo
  - link video
  - nome canale
  - link canale (da `uploader_url` o fallback su `channel_id`)
  - data download UTC

## Note legali
Usa il tool nel rispetto dei termini di YouTube e delle normative sul copyright.
