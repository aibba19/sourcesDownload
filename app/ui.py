import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.services.pptx_service import PptxService
from app.services.word_service import WordService
from app.services.youtube_service import YouTubeService
from app.utils.filename import sanitize_filename
from app.utils.validators import is_supported_youtube_url

try:
    from tkinterdnd2 import DND_FILES

    DND_ENABLED = True
except Exception:
    DND_FILES = None
    DND_ENABLED = False


class AppUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("YouTube Downloader + Metadata PPTX")
        self.root.geometry("860x560")

        self.url_var = tk.StringVar()
        self.word_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.cwd()))

        self._build_layout()

    def _build_layout(self):
        padding = {"padx": 12, "pady": 8}

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Link YouTube (opzionale)").grid(row=0, column=0, sticky="w", **padding)
        ttk.Entry(frame, textvariable=self.url_var, width=80).grid(row=1, column=0, columnspan=2, sticky="ew", **padding)

        ttk.Label(frame, text="File Word .docx (opzionale)").grid(row=2, column=0, sticky="w", **padding)
        self.word_entry = ttk.Entry(frame, textvariable=self.word_file_var, width=65)
        self.word_entry.grid(row=3, column=0, sticky="ew", **padding)
        ttk.Button(frame, text="Sfoglia", command=self.pick_word_file).grid(row=3, column=1, sticky="ew", **padding)

        self.drop_label = tk.Label(
            frame,
            text="Trascina qui il file Word (.docx)",
            relief="groove",
            bd=1,
            padx=10,
            pady=12,
            bg="#f2f4f7",
        )
        self.drop_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        self._setup_drag_and_drop()

        ttk.Label(frame, text="Cartella di output").grid(row=5, column=0, sticky="w", **padding)
        ttk.Entry(frame, textvariable=self.output_dir_var, width=65).grid(row=6, column=0, sticky="ew", **padding)
        ttk.Button(frame, text="Sfoglia", command=self.pick_output_dir).grid(row=6, column=1, sticky="ew", **padding)

        self.start_btn = ttk.Button(frame, text="Scarica e genera metadata", command=self.start_process)
        self.start_btn.grid(row=7, column=0, columnspan=2, sticky="ew", **padding)

        ttk.Label(
            frame,
            text="Nota: usa questo tool nel rispetto dei termini YouTube e dei diritti d'autore.",
            foreground="#7a5800",
        ).grid(row=8, column=0, columnspan=2, sticky="w", **padding)

        ttk.Label(frame, text="Log").grid(row=9, column=0, sticky="w", **padding)
        self.log = tk.Text(frame, height=12, state="disabled")
        self.log.grid(row=10, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.rowconfigure(10, weight=1)

    def _setup_drag_and_drop(self):
        if not DND_ENABLED:
            self.drop_label.config(text="Drag & drop non disponibile (installa/abilita tkinterdnd2)")
            return

        for widget in (self.drop_label, self.word_entry):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop_word_file)

    def _on_drop_word_file(self, event):
        dropped = self.root.tk.splitlist(event.data)
        if not dropped:
            return

        dropped_path = Path(dropped[0])
        if dropped_path.suffix.lower() != ".docx":
            messagebox.showerror("Formato non valido", "Trascina un file Word con estensione .docx")
            return

        self.word_file_var.set(str(dropped_path))
        self._append_log(f"File Word selezionato via drag&drop: {dropped_path}\n")

    def pick_word_file(self):
        selected = filedialog.askopenfilename(
            title="Seleziona file Word",
            filetypes=[("Word files", "*.docx")],
            initialdir=str(Path.cwd()),
        )
        if selected:
            self.word_file_var.set(selected)

    def pick_output_dir(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get() or str(Path.cwd()))
        if selected:
            self.output_dir_var.set(selected)

    def start_process(self):
        url = self.url_var.get().strip()
        word_file = self.word_file_var.get().strip()
        output_dir = self.output_dir_var.get().strip()

        if not url and not word_file:
            messagebox.showerror("Input mancante", "Inserisci un link YouTube oppure seleziona un file Word .docx.")
            return

        if url and not is_supported_youtube_url(url):
            messagebox.showerror("URL non valido", "Inserisci un link YouTube valido (youtube.com o youtu.be).")
            return

        if word_file and not Path(word_file).exists():
            messagebox.showerror("File mancante", "Il file Word selezionato non esiste.")
            return

        if word_file and Path(word_file).suffix.lower() != ".docx":
            messagebox.showerror("Formato non valido", "Seleziona un file Word con estensione .docx.")
            return

        if not output_dir:
            messagebox.showerror("Cartella mancante", "Seleziona una cartella di output.")
            return

        self.start_btn.config(state="disabled")
        self._append_log("Avvio processamento...\n")

        worker = threading.Thread(
            target=self._run_pipeline,
            args=(url, Path(word_file) if word_file else None, Path(output_dir)),
            daemon=True,
        )
        worker.start()

    def _run_pipeline(self, url: str, word_path: Path | None, output_dir: Path):
        try:
            youtube_service = YouTubeService(output_dir=output_dir)
            word_service = WordService()
            pptx_service = PptxService()

            items_to_process: list[tuple[str, str]] = []
            pptx_name = "fonti.pptx"

            if word_path:
                pptx_name = f"fonti-{sanitize_filename(word_path.stem)}.pptx"

            if url:
                items_to_process.append((url, "Video Metadata"))

            if word_path:
                self._append_log(f"Analisi Word: {word_path}\n")
                links = word_service.extract_youtube_links(word_path)
                if not links:
                    self._append_log("Nessun link YouTube trovato nella seconda colonna delle tabelle.\n")
                for row_number, link in links:
                    items_to_process.append((link, f"Slide {row_number}"))

            if not items_to_process:
                raise ValueError("Nessun link YouTube valido da processare.")

            for index, (current_url, slide_title) in enumerate(items_to_process, start=1):
                self._append_log(f"[{index}/{len(items_to_process)}] Estrazione metadati... {current_url}\n")
                metadata = youtube_service.extract_metadata(current_url)

                self._append_log(f"[{index}/{len(items_to_process)}] Download video: {metadata.title}\n")
                video_path = youtube_service.download_mp4(metadata)
                metadata.output_file_path = video_path
                metadata.output_file_name = video_path.name

                self._append_log(
                    f"[{index}/{len(items_to_process)}] Aggiornamento PowerPoint ({slide_title}) su {pptx_name}...\n"
                )
                pptx_path = pptx_service.build_metadata_pptx(
                    metadata,
                    output_dir,
                    slide_title=slide_title,
                    pptx_name=pptx_name,
                )

            self._append_log(f"Completato.\nPPTX: {pptx_path}\n")
            self.root.after(0, lambda: messagebox.showinfo("Successo", "Download e generazione metadata completati."))
        except Exception as exc:
            self._append_log(f"Errore: {exc}\n")
            self.root.after(0, lambda: messagebox.showerror("Errore", str(exc)))
        finally:
            self.root.after(0, lambda: self.start_btn.config(state="normal"))

    def _append_log(self, message: str):
        def update_text():
            self.log.config(state="normal")
            self.log.insert("end", message)
            self.log.see("end")
            self.log.config(state="disabled")

        self.root.after(0, update_text)
