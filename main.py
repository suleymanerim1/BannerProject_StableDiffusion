from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionImg2ImgPipeline
from webcolors import hex_to_name  # https://pypi.org/project/webcolors/1.3/


# to run app : uvicorn main:app --reload
app = FastAPI()


def produce_diffusion_image(image: Image.Image, prompt: str, color_name:str):



    model_id_or_path = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id_or_path,
        use_auth_token="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",
        safety_checker=None
    )

    prompt_with_color = prompt + ", " + "use color " + color_name

    init_image = image.resize((512, 512))
    created_image = pipe(prompt=prompt_with_color,
                         image=init_image,
                         strength=0.1,
                         num_inference_steps=50,
                         guidance_scale=5).images[0]

    return created_image



@app.post("/task1/")
async def create_upload_file(file: UploadFile = File(...), prompt: str = Form(...), hex_code: str = Form(...)):

    img = Image.open(BytesIO(await file.read()))

    # hex codes can be looked up from here : https://www.quackit.com/css/css_color_codes.cfm
    color_name = hex_to_name(hex_value=hex_code, spec='css3') # format : #FF0000
    print(color_name)

    # Apply manipulation to the image
    modified_img = produce_diffusion_image(img,prompt, color_name)

    # Save the modified image to a BytesIO object
    img_byte_array = BytesIO()
    modified_img.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)


    modified_img.save("image.png")
    # Return the modified image
    return StreamingResponse(img_byte_array, media_type="image/png")


@app.post("/task2/")
async def create_upload_file(logo: UploadFile = File(...),color_hex_code: str = Form(...),
                             punch_line: str = Form(...), button:str = Form(...) ):

   #return StreamingResponse(img_byte_array, media_type="image/png")


@app.get("/")
def read_root():
    return {"Hello": "World"}