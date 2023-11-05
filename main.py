from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.templating import Jinja2Templates
import base64
from PIL import Image
from io import BytesIO
from webcolors import hex_to_name  # https://pypi.org/project/webcolors/1.3/
from ad_creator import create_ad_template, produce_diffusion_image


# TODO: webcolors library does not include many html hex code , check it
# in webpage write the hex code style as hint
# TODO: improve stable diffusion output

# to run app : uvicorn main:app --reload
app = FastAPI()

templates = Jinja2Templates(directory="templates")


# uvicorn main:app --reload

@app.get("/")
def dynamic_file(request: Request):
    return templates.TemplateResponse("get_input.html", {"request": request})


@app.post("/ad")
async def ad(request: Request,
                  file: UploadFile = File(),
                  prompt: str = Form(...),
                  img_hex_code: str = Form(...),
                  logo: UploadFile = File(...),
                  color_hex_code: str = Form(...),
                  punch_line: str = Form(...),
                  button: str = Form(...)
                  ):
    img = Image.open(BytesIO(await file.read()))

    # hex codes can be looked up from here : https://www.quackit.com/css/css_color_codes.cfm
    try:
        color_name = hex_to_name(hex_value=img_hex_code, spec='css3')  # Format: #000080
        print(color_name)
    except Exception:
        error_message = "Hex code is not found in webcolors library"
        return {"error": error_message}

    modified_img = produce_diffusion_image(img,prompt, color_name)
    modified_img.save("modified_img.png")

    logo_img = Image.open(BytesIO(await logo.read()))

    ad_template = create_ad_template(modified_img, logo_img, color_hex_code, punch_line, button)

    # Convert the 'PngImageFile' object to bytes
    img_bytes = BytesIO()
    ad_template.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    encoded_image = base64.b64encode(img_bytes).decode("utf-8")

    return templates.TemplateResponse(
        "ad_display.html", {"request": request, "img": encoded_image})
