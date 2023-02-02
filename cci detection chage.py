import rasterio
from skimage.metrics import structural_similarity as ssim

# Aprire le immagini satellitari utilizzando rasterio
with rasterio.open('image1.tif') as src1:
    image1 = src1.read()

with rasterio.open('image2.tif') as src2:
    image2 = src2.read()

# Calcolare l'indice di cambiamento della costruzione utilizzando scikit-image
cci = 1 - ssim(image1, image2, multichannel=True)
print(cci)
################per dtatframe in serie temporale, diffenza immgine dall'altra
import os
import rasterio
from skimage.metrics import structural_similarity as ssim
import pandas as pd

# Creare una lista di immagini da elaborare
image_list = os.listdir('path/to/images')

# Creare un DataFrame per immagazzinare le informazioni sulla data e l'ora di acquisizione per ogni immagine
image_data = pd.DataFrame(image_list, columns=['filename', 'date_time'])

# Ordinare il DataFrame in base alla data e all'ora di acquisizione
image_data = image_data.sort_values(by='date_time')

# Creare un dizionario vuoto per immagazzinare i risultati
cci_results = {}

# Ciclo per ogni immagine nella serie temporale
for i in range(len(image_data) - 1):
    current_image = image_data.iloc[i]
    next_image = image_data.iloc[i + 1]
    #

#######
    import matplotlib.pyplot as plt

# Calcolare l'indice di cambiamento della costruzione per ogni coppia di immagini consecutive

# Creare una mappa a heatmap utilizzando matplotlib
plt.imshow(cci, cmap='hot')
plt.colorbar()
plt.show()
############georeferenziua heat map
import fiona

# Aprire l'immagine originale utilizzando fiona
with fiona.open('original_image.tif', 'r') as src:
    original_image_meta = src.meta

# Creare una copia dei metadati dell'immagine originale
new_image_meta = original_image_meta.copy()

# Modificare i metadati per specificare che la mappa delle differenze è una immagine georeferenziata
new_image_meta.update(driver='GTiff', dtype='float32', count=1)

# Scrivere la mappa delle differenze in un nuovo file utilizzando i metadati dell'immagine originale
with fiona.open('difference_map.tif', 'w', **new_image_meta) as dst:
    dst.write(cci, 1)

