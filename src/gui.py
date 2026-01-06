import tkinter as tk
from tkinter import ttk, messagebox
import threading
import numpy as np
from recorder import Recorder
from transcriber import Transcriber


class AudioRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Recorder")
        self.root.geometry("500x400")
        self.root.configure(bg="#f5f5f5")

        self.transcriber = Transcriber()
        self.recorder = Recorder(self.transcriber.get_sample_rate())
        self.is_recording = False

        self.setup_ui()
        self.update_model_dropdown()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="white", relief=tk.RAISED, borderwidth=2)
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        title_label = tk.Label(main_frame, text="Audio Recorder", font=("Arial", 18, "bold"), bg="white")
        title_label.pack(pady=20)

        model_frame = tk.Frame(main_frame, bg="white")
        model_frame.pack(pady=10)

        tk.Label(model_frame, text="Model:", font=("Arial", 12), bg="white").pack(side=tk.LEFT, padx=5)

        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, state="readonly", width=15)
        self.model_dropdown.pack(side=tk.LEFT, padx=5)

        self.load_model_btn = tk.Button(model_frame, text="Load Model", command=self.load_model,
                                      bg="#007bff", fg="white", font=("Arial", 10),
                                      relief=tk.RAISED, borderwidth=1)
        self.load_model_btn.pack(side=tk.LEFT, padx=5)

        self.status_frame = tk.Frame(main_frame, bg="#e9ecef", relief=tk.SUNKEN, borderwidth=1)
        self.status_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(self.status_frame, text="Ready to record",
                                    font=("Arial", 11), bg="#e9ecef", wraplength=450)
        self.status_label.pack(pady=10, padx=10)

        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=20)

        self.record_btn = tk.Button(button_frame, text="🎤 Record", command=self.toggle_recording,
                                   bg="#007bff", fg="white", font=("Arial", 12, "bold"),
                                   width=15, height=2, relief=tk.RAISED, borderwidth=2)
        self.record_btn.pack(side=tk.LEFT, padx=10)

        self.copy_btn = tk.Button(button_frame, text="📋 Copy", command=self.copy_text,
                                 bg="#28a745", fg="white", font=("Arial", 12, "bold"),
                                 width=15, height=2, relief=tk.RAISED, borderwidth=2,
                                 state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=10)

        self.current_text = ""

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
            self.update_status("Loading model...")
            self.root.update()

            self.transcriber.load_model(model_name)
            self.update_status(f"Model '{model_name}' loaded successfully")
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
            self.record_btn.config(text="⏹️ Stop", bg="#dc3545")
            self.copy_btn.config(state=tk.DISABLED)
            self.update_status("Recording...")

            self.recorder.start()

        except Exception as e:
            self.is_recording = False
            self.record_btn.config(text="🎤 Record", bg="#007bff")
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
            self.update_status(f"Error: {str(e)}")

    def stop_recording(self):
        try:
            self.is_recording = False
            self.record_btn.config(text="🎤 Record", bg="#007bff")
            self.update_status("Processing audio...")

            self.recorder.stop()

            threading.Thread(target=self.transcribe_audio, daemon=True).start()

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
        self.update_status(text)
        self.copy_btn.config(state=tk.NORMAL)

    def on_transcription_error(self, error):
        self.update_status(f"Error: {error}")
        messagebox.showerror("Transcription Error", error)

    def copy_text(self):
        if self.current_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_text)

            original_text = self.copy_btn.cget("text")
            self.copy_btn.config(text="✅ Copied!")
            self.root.after(2000, lambda: self.copy_btn.config(text=original_text))

    def update_status(self, message):
        self.status_label.config(text=message)
