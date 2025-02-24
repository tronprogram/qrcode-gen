import io
import segno
from PIL import Image
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

port = 3007
# app is an instance of the FastAPI class, which is used to define the endpoints of the API
app=FastAPI()
# this defines app as a POST endpoint that should return the referred QR code
@app.post("/referido_qr")

async def gen_qr(ref: int = Query(..., description="Valor del referido")):
    outputbuffr = io.BytesIO()
    segno.make(f"https://amigoscelis.gestionpolitica.com/register/{ref}", error='H', mask=7).save(outputbuffr, border=4, scale=10, light='FFFFFF', dark='e2001b', data_dark='00519f', kind='png')
    outputbuffr.seek(0)
    outputimg = Image.open(outputbuffr)
    outputimg = outputimg.convert('RGBA')
    outputimg_width, outputimg_height = outputimg.size

    # Halve the size of the logo, can't be bothered to resize it outside of the script
    logo_maxsize = (outputimg_width // 4, outputimg_height // 4)

    logoimg = Image.open('cr.png')
    logoimg.thumbnail(logo_maxsize, Image.Resampling.LANCZOS)
    qrcenter = ((outputimg_width - logoimg.size[0]) // 2, (outputimg_height - logoimg.size[1]) // 2)
    outputimg.paste(logoimg, qrcenter)
    # you need to save the image to a new buffer after modifying it with pillow...
    finalbuffr=io.BytesIO()
    outputimg.save(finalbuffr,format='PNG')
    finalbuffr.seek(0)
    return StreamingResponse(finalbuffr,media_type='image/png')
if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=port)