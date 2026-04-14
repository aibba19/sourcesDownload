import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.services.pptx_service import PptxService
from app.services.youtube_service import YouTubeService
from app.utils.validators import is_supported_youtube_url


class AppUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("YouTube Downloader + Metadata PPTX")
        self.root.geometry("760x420")

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.cwd()))

        self._build_layout()

    def _build_layout(self):
        padding = {"padx": 12, "pady": 8}

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Link YouTube").grid(row=0, column=0, sticky="w", **padding)
        ttk.Entry(frame, textvariable=self.url_var, width=80).grid(row=1, column=0, columnspan=2, sticky="ew", **padding)

        ttk.Label(frame, text="Cartella di output").grid(row=2, column=0, sticky="w", **padding)
        ttk.Entry(frame, textvariable=self.output_dir_var, width=65).grid(row=3, column=0, sticky="ew", **padding)
        ttk.Button(frame, text="Sfoglia", command=self.pick_output_dir).grid(row=3, column=1, sticky="ew", **padding)

        self.start_btn = ttk.Button(frame, text="Scarica e genera metadata", command=self.start_process)
        self.start_btn.grid(row=4, column=0, columnspan=2, sticky="ew", **padding)

        ttk.Label(
            frame,
            text="Nota: usa questo tool nel rispetto dei termini YouTube e dei diritti d'autore.",
            foreground="#7a5800",
        ).grid(row=5, column=0, columnspan=2, sticky="w", **padding)

        ttk.Label(frame, text="Log").grid(row=6, column=0, sticky="w", **padding)
        self.log = tk.Text(frame, height=10, state="disabled")
        self.log.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.rowconfigure(7, weight=1)

    def pick_output_dir(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get() or str(Path.cwd()))
        if selected:
            self.output_dir_var.set(selected)

    def start_process(self):
        url = self.url_var.get().strip()
        output_dir = self.output_dir_var.get().strip()

        if not is_supported_youtube_url(url):
            messagebox.showerror("URL non valido", "Inserisci un link YouTube valido (youtube.com o youtu.be).")
            return

        if not output_dir:
            messagebox.showerror("Cartella mancante", "Seleziona una cartella di output.")
            return

        self.start_btn.config(state="disabled")
        self._append_log("Avvio processamento...\n")

        worker = threading.Thread(target=self._run_pipeline, args=(url, Path(output_dir)), daemon=True)
        worker.start()

    def _run_pipeline(self, url: str, output_dir: Path):
        try:
            youtube_service = YouTubeService(output_dir=output_dir)
            pptx_service = PptxService()

            self._append_log("Estrazione metadati...\n")
            metadata = youtube_service.extract_metadata(url)

            self._append_log(f"Download video: {metadata.title}\n")
            video_path = youtube_service.download_mp4(metadata)
            metadata.output_file_path = video_path
            metadata.output_file_name = video_path.name

            self._append_log("Generazione PowerPoint metadati...\n")
            pptx_path = pptx_service.build_metadata_pptx(metadata, output_dir)

            self._append_log(f"Completato.\nVideo: {video_path}\nPPTX: {pptx_path}\n")
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
