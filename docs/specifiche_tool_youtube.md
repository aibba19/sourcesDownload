# Specifiche di Progetto — YouTube Source Downloader + Metadata PPTX

## 1) Obiettivo
Realizzare un tool **semplice** in Python con UI essenziale che:
1. riceve in input un link YouTube;
2. scarica il video in **MP4** in una cartella scelta dall'utente;
3. genera automaticamente un file **PowerPoint (.pptx)** con i metadati del video.

Focus iniziale: **MVP locale (desktop), singolo video per volta**.

---

## 2) Caso d’uso iniziale (fornito)
Input utente:
- URL video: `https://www.youtube.com/watch?v=Y2szlFwZhXk`
- Cartella output: (selezionata da UI)

Output atteso (esempio):
- Video: `Costa dos Castros (English version).mp4`
- PPTX metadati contenente almeno:
  - Nome file
  - Titolo video YouTube
  - Link video
  - Nome canale
  - **Link diretto al canale YouTube**

---

## 3) Scope MVP (v1)
### In scope
- UI minimale con:
  - campo URL YouTube
  - selettore cartella output
  - pulsante “Scarica e genera metadata”
  - area log stato (successo/errori)
- Download MP4 con qualità “best <= 1080p” (configurabile)
- Estrazione metadati principali via API/lib di download
- Generazione 1 file `.pptx` per video
- Naming file sicuro (caratteri non validi sostituiti)

### Out of scope (per ora)
- Download playlist/canale multiplo
- Login account YouTube
- Batch processing
- Traduzioni automatiche metadati
- Upload cloud (Drive, S3, ecc.)

---

## 4) Requisiti funzionali
1. L’utente inserisce un URL YouTube valido.
2. L’utente seleziona una cartella di destinazione.
3. Il sistema recupera i metadati video.
4. Il sistema scarica il video in formato MP4.
5. Il sistema salva i metadati in un file PPTX nella stessa cartella.
6. Il PPTX include il link cliccabile al video e al canale.
7. Il sistema notifica chiaramente errori e stato finale.

---

## 5) Requisiti non funzionali
- **Semplicità**: onboarding in meno di 1 minuto.
- **Portabilità**: Python 3.11+ su Windows/macOS/Linux.
- **Affidabilità**: gestione errori rete, URL non valido, permessi filesystem.
- **Manutenibilità**: codice modulare (UI, download, metadata, export separati).
- **Legalità**: reminder in UI su termini YouTube e diritti d’autore.

---

## 6) Stack tecnico consigliato (Python-first)
- **Download + metadata**: `yt-dlp`
- **UI essenziale desktop**:
  - Opzione A (più semplice): `tkinter` (built-in)
  - Opzione B (più moderna): `customtkinter` o `PySide6`
- **PPTX generation**: `python-pptx`
- **Config e path**: `pathlib`, `pydantic` (opzionale)
- **Packaging** (fase 2): `pyinstaller`

Raccomandazione MVP: `tkinter + yt-dlp + python-pptx`.

---

## 7) Architettura proposta
```text
app/
  main.py                # entrypoint
  ui.py                  # schermata e azioni
  services/
    youtube_service.py   # fetch metadata + download
    pptx_service.py      # costruzione slide metadata
  domain/
    models.py            # dataclass VideoMetadata
  utils/
    filename.py          # sanitize filename
    validators.py        # validazione URL
```

### Modello dati base
`VideoMetadata`:
- `video_id: str`
- `title: str`
- `video_url: str`
- `channel_name: str`
- `channel_url: str`
- `duration_seconds: int | None`
- `upload_date: str | None`
- `description: str | None`
- `output_file_name: str`
- `output_file_path: str`

---

## 8) Flusso operativo
1. UI riceve URL + output dir.
2. Validazione URL (solo dominio YouTube supportato v1).
3. `yt-dlp` estrae info (`extract_info`, senza download) per metadati.
4. Costruzione nome file sicuro.
5. Download MP4 in cartella scelta.
6. Generazione PPTX `*_metadata.pptx`.
7. Log finale + percorso file prodotti.

---

## 9) Dettaglio metadati minimi nel PPTX
Slide 1: “Video Metadata”
- Nome file locale
- Titolo YouTube
- Link video (cliccabile)
- Canale YouTube (nome)
- Link canale YouTube (cliccabile)
- Data download locale

### Nota importante (link canale)
Per ottenere il link corretto del canale usare, in ordine:
1. `uploader_url` (se presente)
2. fallback costruito da `channel_id` => `https://www.youtube.com/channel/{channel_id}`

---

## 10) Esempio output atteso (dal tuo caso)
- Nome file: `Costa dos Castros (English version).mp4`
- Titolo: `Costa dos Castros (English version)`
- Link video: `https://www.youtube.com/watch?v=Y2szlFwZhXk`
- Canale: `Costa dos Castros`
- Link canale: (estratto automaticamente via metadata)

---

## 11) Gestione errori da progettare bene (punti da mettere in discussione)
1. **Video non disponibile / privato / geobloccato**
   - Mostrare messaggio esplicito e non creare file vuoti.
2. **Formato MP4 non disponibile nativo**
   - Strategia: download bestvideo+bestaudio e merge via ffmpeg.
3. **ffmpeg assente**
   - Alert guidato con link installazione.
4. **Titoli con caratteri invalidi su Windows**
   - Sanitize robusto (`<>:"/\\|?*`).
5. **Conflitto file esistente**
   - Strategia: suffisso timestamp o richiesta overwrite.
6. **URL shorts / youtu.be / mobile**
   - Normalizzazione URL prima del processing.

---

## 12) Questioni progettuali da validare prima di sviluppare
- Vuoi **solo 1080p** o sempre “migliore disponibile”?
- Se il video supera 1GB, vuoi warning in UI?
- Se esiste già file con stesso nome: overwrite o versione incrementale?
- Nel PPTX vuoi **solo 1 slide** o template con cover + dettagli?
- Ti serve anche export `.json` dei metadati oltre al PPTX?
- Vuoi gestione coda (più URL) già nella v1.1?

---

## 13) Piano implementazione suggerito
### Milestone 1 — Core CLI (rapida)
- Implementare servizio metadata/download da terminale.
- Verificare output MP4 + metadata dict.

### Milestone 2 — UI base
- Form URL + folder picker + log.
- Pulsante unico start.

### Milestone 3 — PPTX export
- Layout slide minimo professionale.
- Link cliccabili video/canale.

### Milestone 4 — Harden
- Error handling completo.
- Test manuali su 5 URL diversi.

---

## 14) Checklist qualità MVP
- [ ] URL valido gestito
- [ ] Download MP4 riuscito
- [ ] Nome file coerente e sicuro
- [ ] PPTX creato con metadati corretti
- [ ] Link canale cliccabile presente
- [ ] Errori mostrati in UI con testo utile

---

## 15) Consigli pratici (molto concreti)
1. Parti da **CLI funzionante** prima della UI: dimezza i bug.
2. Mantieni `yt-dlp` aggiornato: YouTube cambia spesso.
3. Isola la logica di estrazione metadata dalla UI.
4. Logga sempre:
   - URL input
   - titolo estratto
   - path output
   - eccezione raw (in debug)
5. Prepara da subito un template PPTX base riusabile.
6. Aggiungi in UI una nota su uso lecito dei contenuti scaricati.

---

## 16) Rischi e trade-off (mettiamoli in discussione)
- **Rischio manutenzione**: dipendenza da provider YouTube → possibile rottura periodica.
- **Rischio UX**: UI troppo minima può non chiarire errori tecnici (ffmpeg/network).
- **Trade-off semplicità vs potenza**:
  - MVP semplice = 1 URL alla volta, meno complessità.
  - Batch/playlist subito = più valore ma più superficie bug.
- **Formato output**:
  - Solo PPTX: ottimo per presentazioni.
  - PPTX + JSON: migliore per automazioni future.

---

## 17) Prossimo passo operativo
Se vuoi, nel prossimo step preparo:
1. struttura repo Python completa;
2. MVP funzionante (`tkinter + yt-dlp + python-pptx`);
3. template PPTX minimale con i tuoi campi;
4. script di avvio e README d’uso in italiano.
