from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionImg2ImgPipeline

def add_rounded_corners(img, radius):
    # Create a mask
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    width, height = img.size

    # Draw rounded corners on the mask
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=255)
    draw.pieslice((0, height - radius * 2, radius * 2, height), 90, 180, fill=255)
    draw.pieslice((width - radius * 2, height - radius * 2, width, height), 0, 90, fill=255)
    draw.pieslice((width - radius * 2, 0, width, radius * 2), 270, 360, fill=255)
    draw.rectangle((radius, 0, width - radius, height), fill=255)
    draw.rectangle((0, radius, width, height - radius), fill=255)

    # Add the mask to the image
    img.putalpha(mask)
    return img


# Function to wrap text
def text_wrap(text, font, max_width):
    lines = []
    if len(text) <= max_width:
        lines.append(text)
    else:
        words = text.split(' ')
        i = 0
        while i < len(words):
            line = ''
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                line = line + words[i] + ' '
                i += 1
            lines.append(line)
    return lines


def resize_proportional(img, new_height):
    try:
        width, height = img.size

        # Calculate the proportional width based on the new height
        ratio = new_height / height
        new_width = int(width * ratio)

        # Resize the image with the new width and height
        resized_img = img.resize((new_width, new_height))
        return resized_img

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def create_ad_template(main_img, logo_img, color, punchline_text, button_text, ):
    # Create a blank image for the ad template
    width, height = 500, 700  # Set the width and height of the ad template
    ad_template = Image.new('RGB', (width, height), color='white')

    logo_height = 80  # Adjust according to the logo's height
    logo_img = resize_proportional(img=logo_img, new_height=logo_height)
    main_image_height = 300  # Adjust according to the main image's height
    main_img = resize_proportional(img=main_img, new_height=main_image_height)

    # Calculate vertical gaps and positions to center the elements
    gap = 20  # Gap between elements
    punchline_font_size = 25  # Adjust the font size
    button_font_size = 15  # Adjust the font size

    total_height = logo_height + gap + main_image_height + gap + 4 * gap  # Total height of logo, main image, text, and button
    start_y = (height - total_height) // 2 - gap * 2

    # Calculate positions to center the elements with gaps
    logo_position = (int((width - logo_img.width) / 2), start_y)
    main_image_position = (int((width - main_img.width) / 2), start_y + logo_height + gap)

    # Paste the brand image and the main image onto the ad template
    logo_img_rounded = add_rounded_corners(logo_img, 10)
    main_image_rounded = add_rounded_corners(main_img, 50)
    ad_template.paste(im=logo_img_rounded, box=logo_position, mask=logo_img_rounded)
    ad_template.paste(im=main_image_rounded, box=main_image_position, mask=main_image_rounded)

    # Draw punchline text
    draw = ImageDraw.Draw(ad_template)
    punchline_font = ImageFont.truetype("arial.ttf", punchline_font_size)
    button_font = ImageFont.truetype("arial.ttf", button_font_size)

    # Calculate the text height for positioning
    text_position = start_y + logo_height + 2 * gap + main_image_height

    # Wrap punchline text to fit within the width
    max_width = width - 40  # Adjust according to design
    lines = text_wrap(punchline_text, punchline_font, max_width)
    for line in lines:
        # text_width, text_height = draw.textbbox (line, font=punchline_font)

        # Get the bounding box of the text using the font
        text_box = draw.textbbox((0, 0), line, font=punchline_font)

        # Calculate the width and height of the text within the bounding box
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]

        draw.text(((width - text_width) / 2, text_position), line, fill=color, font=punchline_font)
        text_position += text_height

    # Draw button with specified color and white text
    # button_text_width, button_text_height = draw.textsize(button_text, font=button_font)

    # Get the bounding box of the text using the font
    text_box = draw.textbbox((0, 0), button_text, font=button_font)

    # Calculate the width and height of the text within the bounding box
    button_text_width = text_box[2] - text_box[0]
    button_text_height = text_box[3] - text_box[1]

    button_width = button_text_width + 20  # Adjust the button width based on the text
    button_height = button_text_height + 10  # Adjust the button height based on the text
    button_position = ((width - button_width) // 2, text_position + gap)

    # Draw a filled rectangle (button) behind the text
    draw.rectangle([button_position, (button_position[0] + button_width, button_position[1] + button_height)],
                   fill=color)

    # Calculate the text position to center it within the button
    text_position = ((width - button_text_width) // 2, button_position[1] + 5)  # Adjust the Y coordinate for centering

    # Draw the button text in white color
    draw.text(text_position, button_text, fill='white', font=button_font)

    # Save the ad template to a file
    ad_template.save('ad_template.png')

    print("----------The ad is produced!----------")

    return ad_template


def produce_diffusion_image(image: Image.Image, prompt: str, color_name: str):
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
                         strength=0.5,
                         num_inference_steps=30,
                         guidance_scale=5).images[0]

    return created_image


if __name__ == '__main__':
    # Example usage
    logo_image = Image.open('trial_logo.png')
    main_image = Image.open('image.png')
    color = '#ff0000'
    punchline_text = 'Your long punchline text goes here and it should wrap to multiple lines if it exceeds the specified width '
    button_text = 'Click Here'

    create_ad_template(main_image, logo_image, color, punchline_text, button_text)
