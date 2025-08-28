"""Script to download Poppins fonts."""
import urllib.request
import os

# Create fonts directory if it doesn't exist
fonts_dir = os.path.join("resources", "fonts")
os.makedirs(fonts_dir, exist_ok=True)

# Font files to download
fonts = {
    "Poppins-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Medium.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Medium.ttf",
    "Poppins-SemiBold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-SemiBold.ttf",
    "Poppins-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"
}

# Download each font
for filename, url in fonts.items():
    filepath = os.path.join(fonts_dir, filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded {filename}")
    else:
        print(f"{filename} already exists")
