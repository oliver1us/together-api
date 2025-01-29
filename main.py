from together import Together
import requests
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

client = Together()

# client.set_api_key(os.get.environ("TOGETHER_API_KEY"))


def download_image(url, folder="downloaded_images"):
    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/generated_image_{timestamp}.jpg"

    # Download the image
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Image successfully downloaded to: {filename}")
        return filename
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
        return None


# Initialize Together client and generate image
client = Together()
imageCompletion = client.images.generate(
    model="black-forest-labs/FLUX.1-depth",
    width=1024,
    height=768,
    steps=28,
    prompt="Add Windows XP to the screen of the phone",
    image_url="https://img.asmedia.epimg.net/resizer/v2/QNGCIGL5GZHX7FF5X4WXOWWRVY.jpg?auth=e42f7a3b00b4f0265184d8e535e5f5a5b67d48e4284a2d3fedb51123c0773682&width=644&height=362&smart=true",
)

# Get the image URL and download it
image_url = imageCompletion.data[0].url
downloaded_file = download_image(image_url)
