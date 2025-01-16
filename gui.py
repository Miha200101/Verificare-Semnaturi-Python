import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np
import cv2
from database import adauga_semnatura, sterge_semnatura, verifica_existenta_semnatura, obtine_toate_semnaturile
import logging
import os

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AplicatieSemnaturi:
    def __init__(self, root, model, db_path):
        self.root = root
        self.root.title("Sistem de Verificare a Semnăturilor")
        self.model = model
        self.db_path = db_path
        self.signature_path = None
        self.img_tk = None  # Inițializare atribut pentru a păstra referința imaginii

        # Componente GUI
        tk.Label(root, text="Sistem de Verificare a Semnăturilor", font=("Helvetica", 16)).pack(pady=10)
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        culoare_buton = '#ADD8E6'  # Codul hexazecimal pentru albastru deschis

        tk.Button(root, text="Încarcă Imagine", command=self.incarca_imagine, bg=culoare_buton).pack(pady=5)
        tk.Button(root, text="Verifică Semnătura", command=self.verifica_semnatura, bg=culoare_buton).pack(pady=5)
        tk.Button(root, text="Adaugă Semnătura", command=self.adauga_semnatura, bg=culoare_buton).pack(pady=5)
        tk.Button(root, text="Șterge Semnătura", command=self.sterge_semnatura, bg=culoare_buton).pack(pady=5)

    def incarca_imagine(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fișiere Imagine", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.signature_path = file_path
            img = Image.open(file_path).resize((400, 200))
            self.img_tk = ImageTk.PhotoImage(img)  # Păstrează referința la obiectul PhotoImage
            self.image_label.config(image=self.img_tk)
            logging.info(f"Imaginea {file_path} a fost încărcată.")

    def verifica_semnatura(self):
        if not self.signature_path:
            messagebox.showwarning("Avertisment", "Vă rugăm să încărcați mai întâi o imagine cu semnătura.")
            return

        # Preprocesarea imaginii
        image = cv2.imread(self.signature_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (128, 32)) / 255.0
        image = np.expand_dims(np.expand_dims(image, axis=-1), axis=0)

        # Obțineți predicția de probabilitate
        probabilitate = self.model.predict(image)[0][0]
        prag = 0.5
        procent = probabilitate * 100

        # Determinați rezultatul pe baza pragului
        if probabilitate >= prag:
            rezultat = "falsă"
            mesaj = f"Semnătura este considerată FALSĂ cu o probabilitate de {procent:.2f}%."
        else:
            rezultat = "originală"
            mesaj = f"Semnătura este considerată ORIGINALĂ cu o probabilitate de {100 - procent:.2f}%."

        # Afișați rezultatul
        messagebox.showinfo("Rezultat Verificare Semnătură", mesaj)
        logging.info(f"Semnătura {self.signature_path} este {rezultat} cu o probabilitate de {procent:.2f}%.")

    def adauga_semnatura(self):
        if not self.signature_path:
            messagebox.showwarning("Avertisment", "Vă rugăm să încărcați mai întâi o imagine cu semnătura.")
            return

        if verifica_existenta_semnatura(self.db_path, self.signature_path):
            messagebox.showinfo("Informație", "Imaginea există deja în baza de date.")
            logging.info(f"Imaginea {self.signature_path} există deja în baza de date.")
            return

        # Adăugare imagine în baza de date
        id_semnatura = adauga_semnatura(self.db_path, self.signature_path)
        if id_semnatura:
            messagebox.showinfo("Succes", f"Semnătura a fost adăugată cu succes cu ID-ul {id_semnatura}.")
            logging.info(f"Semnătura {self.signature_path} a fost adăugată cu succes cu ID-ul {id_semnatura}.")
        else:
            messagebox.showerror("Eroare", "Eroare la adăugarea semnăturii în baza de date.")

    def sterge_semnatura(self):
        # Afișează semnăturile existente
        semnaturi = obtine_toate_semnaturile(self.db_path)
        if not semnaturi:
            messagebox.showinfo("Informație", "Baza de date este goală.")
            return

        lista_semnaturi = "\n".join([f"ID: {id}, Cale: {path}" for id, path in semnaturi])
        messagebox.showinfo("Semnături existente", f"Semnături disponibile:\n{lista_semnaturi}")

        # Solicită ID pentru ștergere
        id_de_sters = simpledialog.askinteger("Șterge Semnătura", "Introduceți ID-ul semnăturii de șters:")
        if id_de_sters:
            succes = sterge_semnatura(self.db_path, id_de_sters)
            if succes:
                messagebox.showinfo("Succes", f"Semnătura cu ID-ul {id_de_sters} a fost ștearsă.")
                logging.info(f"Semnătura cu ID-ul {id_de_sters} a fost ștearsă.")
            else:
                messagebox.showerror("Eroare", f"Nu s-a putut șterge semnătura cu ID-ul {id_de_sters}.")
                logging.error(f"Eroare la ștergerea semnăturii cu ID-ul {id_de_sters}.")
