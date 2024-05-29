import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import os
import subprocess
import sys

# Function to install a package using pip
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try to import easyocr and install if not found
try:
    import pytesseract
except ImportError:
    st.warning("pytesseract not found. Installing...")
    install_package("pytesseract")
    import pytesseract

# Ensure tesseract is installed and available in PATH, or provide the correct path
# Use the path returned by `which tesseract`
def install_tesseract():
    try:
        subprocess.run(['apt-get', 'update'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'tesseract-ocr'], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"An error occurred while installing Tesseract: {e}")
        return False
    return True

# Check if Tesseract is installed and install if not found
tesseract_cmd = shutil.which("tesseract")
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    st.info("Tesseract not found. Installing...")
    if install_tesseract():
        tesseract_cmd = shutil.which("tesseract")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            st.error("Tesseract installation failed. Ensure it is installed and in your PATH.")
    else:
        st.error("Tesseract installation failed. Ensure it is installed and in your PATH.")

def extract_text_from_image(image):
    try:
        # Use pytesseract to do OCR on the image
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

def process_images_to_csv(images, output_csv):
    f = []
    t = []

    for img, filename in images:
        try:
            text = extract_text_from_image(img)
            if text:
                f.append(filename)
                t.append(text)
        except Exception as e:
            st.error(f"Error processing {filename}: {e}")
            continue

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(list(zip(f, t)), columns=['file_Name', 'Text'])

    # Write the DataFrame to a CSV file
    df.to_csv(output_csv, index=False)
    return df

def main():
    st.title("Image Text Extractor")

    # File uploader for multiple image files
    uploaded_files = st.file_uploader("Choose image files", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        images = [(Image.open(file), file.name) for file in uploaded_files]
        if st.button("Extract Text"):
            with st.spinner('Processing...'):
                output_csv = 'output_text.csv'
                df = process_images_to_csv(images, output_csv)
                st.success(f"Text extracted and saved to {output_csv}")
                st.dataframe(df)
                # Provide a download link
                st.download_button(
                    label="Download CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='output_text.csv',
                    mime='text/csv'
                )

if __name__ == "__main__":
    main()
