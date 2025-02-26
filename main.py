# io is a module that provides Python’s main facilities for dealing with various types of I/O
import io
# segno is a module that provides a QR code generator
import segno
# PIL is a module that provides Python’s main facilities for dealing with images, and Image is a module that provides a class with the same name
from PIL import Image
# FastAPI is a module that provides Python’s main facilities for building APIs, and Query is a module that provides a class with the same name
from fastapi import FastAPI, Query
# StreamingResponse is a module that provides a class with the same name
from fastapi.responses import StreamingResponse

# port is a variable that stores the port number of the API
port = 3007
# app is an instance of the FastAPI class, which is used to define the endpoints of the API
app=FastAPI()
# this defines app as a POST endpoint that should return the referred QR code
@app.get("/referido_qr")
# this defines gen_qr as a function that takes in a parameter ref, which is an integer, and returns a StreamingResponse. the ... is a placeholder for the required parameter ref, and the description is a string that describes the parameter ref
# with that said, gen_qr generates a QR code with the URL "https://domain.com/register/{ref}" and returns it as a StreamingResponse, which is a response that streams data
async def gen_qr(ref: int = Query(..., description="Valor del referido")):
    # outputbuffr is a buffer that stores the QR code. it is an instance of the BytesIO class, which is used to read and write bytes-like objects
    outputbuffr = io.BytesIO()
    # segno.make is a function that generates a QR code with the specified URL, error correction level, and mask. the save method saves the QR code to the outputbuffr buffer
    # the border parameter specifies the size of the border around the QR code, the scale parameter specifies the size of the QR code, the light parameter specifies the color of the light squares in the QR code, the dark parameter specifies the color of the dark squares in the QR code, the data_dark parameter specifies the color of the dark data in the QR code, and the kind parameter specifies the format of the QR code. the kind parameter is important to set, given that we're saving the QR code to a buffer
    segno.make(f"https://domain.com/register/{ref}", error='H', mask=7).save(outputbuffr, border=4, scale=10, light='FFFFFF', dark='c12aeb', data_dark='480759', kind='png')
    # you need to seek to the beginning of the buffer before returning it
    outputbuffr.seek(0)
    # outputimg is an image that stores the QR code. it is an instance of the Image class, which is used to represent images
    # Image.open is a function that opens an image file, and Image.convert is a method that converts the image to a different color standard, in this case, RGBA.
    outputimg = Image.open(outputbuffr)
    outputimg = outputimg.convert('RGBA')
    # setting the height and width of the QR code
    outputimg_width, outputimg_height = outputimg.size

    # shrink down the logo to 1/4th, can't be bothered to resize it outside of the script
    logo_maxsize = (outputimg_width // 4, outputimg_height // 4)
    # logoimg is an image that stores the logo
    logoimg = Image.open('logo.png')
    # Image.thumbnail is a method that resizes the image to fit the specified size, it takes in the size of the image and the resampling filter to use
    logoimg.thumbnail(logo_maxsize, Image.Resampling.LANCZOS)
    # qrcenter is a tuple that stores the center of the QR code
    qrcenter = ((outputimg_width - logoimg.size[0]) // 2, (outputimg_height - logoimg.size[1]) // 2)
    # Image.paste is a method that pastes an image onto another image, it takes in the image to paste, the position to paste it at, and the mask of the image to paste
    outputimg.paste(logoimg, qrcenter)
    # you need to save the image to a new buffer after modifying it with pillow...
    finalbuffr=io.BytesIO()
    outputimg.save(finalbuffr,format='PNG')
    finalbuffr.seek(0)
    return StreamingResponse(finalbuffr,media_type='image/png')
if __name__=="__main__":
    # uvicorn is a module that provides Python’s main facilities for running ASGI applications
    import uvicorn
    # uvicorn.run is a function that runs an ASGI application, it takes in the app instance, the host to run the application on, and the port to run the application
    uvicorn.run(app,host='0.0.0.0',port=port)