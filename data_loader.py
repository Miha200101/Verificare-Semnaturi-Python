import os
import cv2
import numpy as np
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def incarca_dataset_cedar(cale_dataset):
    """
    Încarcă și preprocesează imaginile și etichetele din dataset-ul CEDAR.
    """
    imagini = []
    etichete = []

    if not os.path.exists(cale_dataset):
        logging.error(f"Directorul {cale_dataset} nu există.")
        return np.array(imagini), np.array(etichete)

    # Eticheta 0 pentru semnături originale, 1 pentru falsificate
    for eticheta, folder in enumerate(['full_org', 'full_forg']):
        cale_folder = os.path.join(cale_dataset, folder)
        if not os.path.exists(cale_folder):
            logging.warning(f"Folderul {cale_folder} nu există. Este omis.")
            continue

        for fisier in os.listdir(cale_folder):
            if fisier.endswith('.png') or fisier.endswith('.jpg'):
                cale_imagine = os.path.join(cale_folder, fisier)
                try:
                    imagine = cv2.imread(cale_imagine, cv2.IMREAD_GRAYSCALE)
                    if imagine is not None:
                        imagine = cv2.resize(imagine, (128, 32))  # Redimensionare imagine
                        imagine = imagine / 255.0  # Normalizare imagine
                        imagini.append(imagine)
                        etichete.append(eticheta)
                    else:
                        logging.error(f"Eroare la încărcarea imaginii {cale_imagine}.")
                except Exception as e:
                    logging.error(f"Eroare la procesarea imaginii {cale_imagine}: {e}")

    imagini = np.expand_dims(np.array(imagini), axis=-1)  # Adaugare canal pentru format Keras
    etichete = np.array(etichete)

    logging.info(f"Încărcate {len(imagini)} imagini din dataset-ul {cale_dataset}.")
    return imagini, etichete
