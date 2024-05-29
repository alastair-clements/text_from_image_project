import streamlit as st
from PIL import Image
import easyocr
import pandas as pd

# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])

def extract_text_from_image(image):
    try:
        # Use easyocr to do OCR on the image
        text = reader.readtext(image, detail=0)
        return ' '.join(text)
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
