from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, Response
from PIL import Image
from io import BytesIO
from webcolors import hex_to_name  # https://pypi.org/project/webcolors/1.3/
from ad_creator import create_ad_template, produce_diffusion_image


#TODO: webcolors library does not include many html hex code , check it

# to run app : uvicorn main:app --reload
app = FastAPI()


@app.post("/task1/")
async def task1(file: UploadFile = File(...), prompt: str = Form(...), hex_code: str = Form(...)):

    img = Image.open(BytesIO(await file.read()))

    # hex codes can be looked up from here : https://www.quackit.com/css/css_color_codes.cfm

    try:
        color_name = hex_to_name(hex_value=hex_code, spec='css3')  # Format: #FF0000
    except Exception as e:
        error_message = "Hex code is not found in webcolors library"
        return {"error": error_message}

    print(color_name)

    # Apply manipulation to the image
    modified_img = produce_diffusion_image(img,prompt, color_name)

    # Save the modified image to a BytesIO object
    img_byte_array = BytesIO()
    modified_img.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)


    modified_img.save("image.png")
    # Return the modified image
    return Response(img_byte_array, media_type="image/png")


@app.post("/task2/")
async def task2(logo: UploadFile = File(...),color_hex_code: str = Form(...),
                             punch_line: str = Form(...), button:str = Form(...) ):

    logo_img = Image.open(BytesIO(await logo.read()))
    main_image = Image.open('image.png')


    ad_template = create_ad_template(main_image, logo_img, color_hex_code, punch_line, button)

    # Save the modified image to a BytesIO object
    img_byte_array = BytesIO()
    ad_template.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)


    # Return the ad template as a response
    return Response(content=img_byte_array, media_type="image/png")



@app.get("/")
def read_root():
    return {"Hello": "World"}


