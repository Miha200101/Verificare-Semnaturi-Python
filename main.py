import os
import logging
import tkinter as tk
from data_loader import incarca_dataset_cedar
from model import construieste_model
from gui import AplicatieSemnaturi
from database import initializeaza_baza_de_date

# Configurare logging
logging.basicConfig(
    filename='aplicatie.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Suprimă mesajele de avertizare TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

if __name__ == "__main__":
    try:
        # Inițializare baza de date
        cale_baza_de_date = "semnaturi.db"
        initializeaza_baza_de_date(cale_baza_de_date)

        # Încărcare dataset
        cale_dataset = "data/signatures"
        imagini, etichete = incarca_dataset_cedar(cale_dataset)

        if imagini.size == 0:
            logging.error("Nu au fost încărcate imagini. Verificați calea dataset-ului.")
            exit()

        # Construire model
        dimensiune_intrare = (32, 128, 1)  # Formatul imaginii: 32x128 pixeli, 1 canal (grayscale)
        model = construieste_model(dimensiune_intrare)
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

        # Antrenare model
        logging.info("Începerea antrenării modelului...")
        model.fit(imagini, etichete, epochs=5, validation_split=0.2)
        logging.info("Antrenarea modelului s-a finalizat cu succes.")

        # Salvare model
        os.makedirs('models', exist_ok=True)
        cale_model = os.path.join('models', 'model_verificare_semnaturi.keras')
        model.save(cale_model)
        logging.info(f"Modelul a fost salvat în {cale_model}.")

        # Rulare interfață grafică
        root = tk.Tk()
        aplicatie = AplicatieSemnaturi(root, model, cale_baza_de_date)
        root.mainloop()
        logging.info("Aplicația a fost închisă.")

    except Exception as e:
        logging.error(f"Eroare în rularea aplicației: {e}")
        raise
