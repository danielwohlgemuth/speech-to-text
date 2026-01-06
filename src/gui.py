import tkinter as tk
from tkinter import ttk, messagebox
import threading
import numpy as np
from recorder import Recorder
from transcriber import Transcriber


class AudioRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcriber")
        self.root.geometry("500x400")

        self.transcriber = Transcriber()
        self.recorder = Recorder(self.transcriber.get_sample_rate())
        self.is_recording = False

        self.setup_ui()
        self.update_model_dropdown()

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.record_btn = tk.Button(button_frame, text="🎤 Record", command=self.toggle_recording,
                                   font=("Arial", 12, "bold"),
                                   width=15, height=2, relief=tk.RAISED, borderwidth=2)
        self.record_btn.pack(side=tk.LEFT, padx=10)

        self.copy_btn = tk.Button(button_frame, text="📋 Copy", command=self.copy_text,
                                 font=("Arial", 12, "bold"),
                                 width=15, height=2, relief=tk.RAISED, borderwidth=2,
                                 state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=10)

        self.transcription_frame = tk.Frame(main_frame)
        self.transcription_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.transcription_text = tk.Text(self.transcription_frame, font=("Arial", 16), wrap=tk.WORD,
                                          height=8, relief=tk.FLAT, borderwidth=0, pady=10, padx=10)
        self.transcription_text.pack(fill=tk.BOTH, expand=True)
        self.transcription_text.insert("1.0", "")
        self.transcription_text.config(state=tk.DISABLED)

        self.current_text = ""

        model_frame = tk.Frame(main_frame)
        model_frame.pack(pady=10)

        tk.Label(model_frame, text="Model:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, state="readonly", width=15)
        self.model_dropdown.pack(side=tk.LEFT, padx=5)
        self.model_dropdown.bind('<<ComboboxSelected>>', lambda event: self.load_model())

        self.status_label = tk.Label(main_frame, text="Ready to record", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def update_model_dropdown(self):
        try:
            models = self.transcriber.available_models()
            self.model_dropdown['values'] = models
            if models:
                current_model = self.transcriber.get_current_model_name()
                if current_model in models:
                    self.model_var.set(current_model)
                else:
                    self.model_var.set(models[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")

    def load_model(self):
        model_name = self.model_var.get()
        if not model_name:
            messagebox.showwarning("Warning", "Please select a model")
            return

        try:
            self.root.update()

            self.update_status('Loading model')
            self.transcriber.load_model(model_name)
            self.update_status('Model loaded')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.update_status(f"Error loading model: {str(e)}")

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        try:
            self.is_recording = True
            self.record_btn.config(text="⏹️ Stop")
            self.copy_btn.config(state=tk.DISABLED)
            self.update_status("Recording")

            self.recorder.start()

        except Exception as e:
            self.is_recording = False
            self.record_btn.config(text="🎤 Record")
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
            self.update_status(f"Error: {str(e)}")

    def stop_recording(self):
        try:
            self.is_recording = False
            self.record_btn.config(text="🎤 Record")
            self.update_status("Processing audio")

            self.recorder.stop()

            threading.Thread(target=self.transcribe_audio, daemon=True).start()

            self.update_status("Ready to record")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")
            self.update_status(f"Error: {str(e)}")

    def transcribe_audio(self):
        try:
            audio_data = self.recorder.get_audio_data()

            if len(audio_data) == 0:
                self.root.after(0, lambda: self.update_status("No audio recorded"))
                return

            transcription = self.transcriber.transcribe(audio_data)

            self.root.after(0, lambda: self.on_transcription_complete(transcription))

        except Exception as e:
            self.root.after(0, lambda: self.on_transcription_error(str(e)))

    def on_transcription_complete(self, text):
        self.current_text = text
        self.update_transcription(text)
        self.copy_btn.config(state=tk.NORMAL)

    def on_transcription_error(self, error):
        self.update_status(f"Error: {error}")
        messagebox.showerror("Transcription Error", error)

    def update_transcription(self, text):
        self.transcription_text.config(state=tk.NORMAL)
        self.transcription_text.delete("1.0", tk.END)
        self.transcription_text.insert("1.0", text)
        self.transcription_text.config(state=tk.DISABLED)

    def copy_text(self):
        if self.current_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_text)

            original_text = self.copy_btn.cget("text")
            self.copy_btn.config(text="✅ Copied!")
            self.root.after(2000, lambda: self.copy_btn.config(text=original_text))

    def update_status(self, message):
        self.status_label.config(text=message)
