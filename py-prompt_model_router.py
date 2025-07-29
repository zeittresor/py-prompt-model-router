#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Router Helper (Tkinter)
-----------------------------
A small GUI that suggests an OpenAI ChatGPT model based on a user prompt.
It does not call any APIs; it uses lightweight heuristics to pick one of:
- o3 (reasoning)
- o4-mini (fast iterations)
- GPT-4o (voice/multimodal)
- GPT-4.1 (coding executor/assistant)

Author: ChatGPT
Sourcecode: https://github.com/zeittresor/py-prompt-model-router
License: MIT
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_any(text: str, keywords) -> bool:
    return any(k in text for k in keywords)


def recommend_model(user_text: str):
    """
    Return a dict with keys: model, reason, alternatives.
    Heuristic rules only, no API calls.
    """
    t = normalize(user_text)
    length = len(t)

    audio_kw = [
        "voice", "audio", "sprache", "mikrofon", "aufnehmen", "aufnahme",
        "sprachnachricht", "transkrib", "diktat"
    ]
    image_kw = [
        "bild", "screenshot", "photo", "foto", "diagram", "image",
        "grafik", "ocr", "erkenne im bild", "beschreibe das bild"
    ]
    code_kw = [
        "code", "funktion", "refactor", "refaktor", "bug", "exception",
        "stack trace", "stacktrace", "kompilier", "buildfehler",
        "unit test", "unittest", "pytest", "gradle", "maven",
        ".py", ".js", ".ts", ".java", ".kt", ".cs", ".cpp", ".c", ".rb",
        ".go", ".rs", "dockerfile", "requirements.txt", "package.json"
    ]
    reasoning_kw = [
        "architektur", "strategie", "begründ", "warum", "ableitung",
        "beweise", "beweis", "argumentiere", "schritte", "plan",
        "roadmap", "trade-off", "tradeoff", "konzept", "threat model",
        "modelliere", "analyse", "algorithm", "komplexität", "optimier",
        "logik", "puzzle", "rätsel", "fehlerursache", "ursachenanalyse",
        "entscheid", "abwegung"
    ]
    quick_kw = [
        "kurz", "zusammenfassung", "tl;dr", "stichpunkte", "bullet points",
        "umformulieren", "paraphras", "kürzen", "rewrite", "übersetz",
        "translate", "emoji", "titelvorschläge", "slogan"
    ]

    # 1) Modalities first
    if contains_any(t, audio_kw) or contains_any(t, image_kw):
        return {
            "model": "GPT-4o",
            "reason": "Audio/Bild/Multimodalität erkannt – 4o ist für Voice/Bilder optimiert.",
            "alternatives": "Falls nach der Transkription/Analyse tieferes Denken nötig ist: o3. Für viele kurze Folge-Edits: o4-mini."
        }

    # 2) Coding vs. reasoning
    if contains_any(t, code_kw):
        if contains_any(t, reasoning_kw) or "algorithm" in t or "architektur" in t:
            return {
                "model": "o3",
                "reason": "Coding mit konzeptueller/algorithmischer Begründung – o3 priorisiert tiefes Reasoning.",
                "alternatives": "Für unmittelbares Implementieren/Refactoren: GPT-4.1. Für schnelle Iterationen: o4-mini."
            }
        else:
            return {
                "model": "GPT-4.1",
                "reason": "Konkrete Coding-Aufgabe erkannt – 4.1 befolgt Anweisungen stabil und ist stark im Refactoring/Implementieren.",
                "alternatives": "Wenn Analyse/Entscheidungen verlangt sind: o3. Für viele kleine Schleifen: o4-mini."
            }

    # 3) Pure reasoning / planning
    if contains_any(t, reasoning_kw):
        return {
            "model": "o3",
            "reason": "Begriffe deuten auf Planung/Analyse/Entscheidung hin – o3 ist das Reasoning-Modell.",
            "alternatives": "Wenn du viele kurze Iterationen brauchst: o4-mini. Wenn Bilder/Voice dazukommen: GPT-4o."
        }

    # 4) Quick edits / summarization
    if contains_any(t, quick_kw):
        return {
            "model": "o4-mini",
            "reason": "Kurzarbeit/Umformulieren/Zusammenfassen – o4-mini ist schnell & kosteneffizient.",
            "alternatives": "Für besonders knifflige Passagen: o3. Für Voice/Bilder: GPT-4o."
        }

    # 5) Fallback by size/ambiguity
    if length > 700:
        return {
            "model": "o3",
            "reason": "Langer/unklarer Prompt – o3 als sichere Wahl für gründliches Denken.",
            "alternatives": "Wenn es primär um schnelle Oberflächenarbeit geht: o4-mini."
        }
    else:
        return {
            "model": "o4-mini",
            "reason": "Kein spezielles Muster erkannt, eher kurze Aufgabe – o4-mini für schnelle Iterationen.",
            "alternatives": "Wenn tiefere Analyse nötig wird: o3. Für Voice/Bild: GPT-4o."
        }


class RouterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Model Router Helper (heuristisch)")
        self.geometry("980x600")
        self.minsize(900, 520)

        # --- Styles ---
        try:
            self.style = ttk.Style(self)
            if "clam" in self.style.theme_names():
                self.style.theme_use("clam")
        except Exception:
            pass

        # --- Layout ---
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")
        self.rowconfigure(1, weight=1)

        header = ttk.Label(self, text="Heuristische Modell-Empfehlung für ChatGPT", font=("Segoe UI", 14, "bold"))
        header.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6))

        # Left: Input
        left_frame = ttk.Frame(self, padding=(8, 6, 8, 8))
        left_frame.grid(row=1, column=0, sticky="nsew")
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        ttk.Label(left_frame, text="Eingabe (Prompt):").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.input_txt = scrolledtext.ScrolledText(left_frame, wrap="word", height=16, undo=True)
        self.input_txt.grid(row=1, column=0, sticky="nsew")

        # Buttons under input
        btns = ttk.Frame(left_frame)
        btns.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        for i in range(4):
            btns.columnconfigure(i, weight=1)

        self.check_btn = ttk.Button(btns, text="Prüfen (Modell wählen)", command=self.on_check)
        self.check_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.copy_input_btn = ttk.Button(btns, text="Eingabetext kopieren", command=self.copy_input)
        self.copy_input_btn.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        self.copy_result_btn = ttk.Button(btns, text="Ergebnis kopieren", command=self.copy_result)
        self.copy_result_btn.grid(row=0, column=2, sticky="ew", padx=(0, 6))

        self.clear_btn = ttk.Button(btns, text="Löschen", command=self.clear_all)
        self.clear_btn.grid(row=0, column=3, sticky="ew")

        # Right: Result
        right_frame = ttk.Frame(self, padding=(8, 6, 8, 8))
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        ttk.Label(right_frame, text="Empfehlung:").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.result_txt = scrolledtext.ScrolledText(right_frame, wrap="word", height=16, state="normal")
        self.result_txt.grid(row=1, column=0, sticky="nsew")

        hint = ttk.Label(
            right_frame,
            text=(
                "Hinweis: Das ist eine heuristische Empfehlung (kein automatisches Routing). "
                "Wähle das Modell in ChatGPT manuell und füge deinen Text ein."
            ),
            wraplength=480,
            foreground="#555"
        )
        hint.grid(row=2, column=0, sticky="w", pady=(6, 0))

        # Footer
        footer = ttk.Label(
            self,
            text="Empfohlene Typen: o3 (Reasoning), o4-mini (schnell), GPT-4o (Voice/Bild), GPT-4.1 (Coding).",
            foreground="#444"
        )
        footer.grid(row=3, column=0, columnspan=2, sticky="w", padx=12, pady=(6, 10))

        # Shortcuts
        self.bind("<Control-Return>", lambda e: self.on_check())
        self.bind("<Command-Return>", lambda e: self.on_check())  # macOS

    def on_check(self):
        text = self.input_txt.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Hinweis", "Bitte gib zuerst einen Prompt ein.")
            return
        rec = recommend_model(text)
        output = (
            f"Empfohlenes Modell: {rec['model']}\n\n"
            f"Begründung:\n{rec['reason']}\n\n"
            f"Alternativen:\n{rec['alternatives']}\n"
        )
        self.result_txt.configure(state="normal")
        self.result_txt.delete("1.0", "end")
        self.result_txt.insert("1.0", output)
        self.result_txt.see("1.0")

    def copy_input(self):
        text = self.input_txt.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Hinweis", "Kein Eingabetext vorhanden.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        messagebox.showinfo("Kopiert", "Eingabetext wurde in die Zwischenablage kopiert.")

    def copy_result(self):
        text = self.result_txt.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Hinweis", "Kein Ergebnis zum Kopieren vorhanden.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        messagebox.showinfo("Kopiert", "Ergebnis wurde in die Zwischenablage kopiert.")

    def clear_all(self):
        self.input_txt.delete("1.0", "end")
        self.result_txt.configure(state="normal")
        self.result_txt.delete("1.0", "end")


def main():
    app = RouterGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
