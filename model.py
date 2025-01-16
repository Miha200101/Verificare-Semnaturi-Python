import tensorflow as tf  # type: ignore
from tensorflow.keras import layers, models # type: ignore
import logging  # Import pentru logging

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def construieste_model(dimensiune_intrare):
    """
    Construiește un model de rețea neuronală convoluțională pentru verificarea semnăturilor.
    """
    try:
        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=dimensiune_intrare),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Clasificare binară: Originală (1) sau Falsă (0)
        ])
        logging.info("Modelul a fost construit cu succes.")  # Logare succes
        return model
    except Exception as e:
        logging.error(f"Eroare la construirea modelului: {e}")  # Logare eroare
        raise
