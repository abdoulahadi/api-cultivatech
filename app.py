from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from fastapi.responses import StreamingResponse

app = FastAPI()

class ImageUpload(BaseModel):
    file: bytes

def calculate_ndvi(red_band, nir_band):
    red_band[red_band == 0] = np.nan
    nir_band[nir_band == 0] = np.nan
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    return ndvi

@app.post("/process-image/")
async def process_image(image: UploadFile, recipient_email: str = None):
    img = Image.open(image.file).convert('RGB')
    img_array = np.array(img)

    # Extracting red and near-infrared bands
    red_band = img_array[:,:,0].astype(float)
    nir_band = img_array[:,:,1].astype(float)

    ndvi = calculate_ndvi(red_band, nir_band)
    plt.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(label='NDVI')
    plt.title('NDVI Image')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")
