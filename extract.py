import cv2
import pytesseract
import re
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def preprocess_image(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_front_details(text):
    details = {}

    name_match = re.search(r'\n([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3}|[A-Z]{2,}(?:\s[A-Z]{2,}){0,3})\n.*(Date of Birth|DOB)', text, re.IGNORECASE)

    details['Name'] = name_match.group(1).strip() if name_match else 'Not Found'

    
    dob_match = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', text)
    yob_match = re.search(r'\b(YOB|Year of Birth)[:\s]*([0-9]{4})\b', text, re.IGNORECASE)
    if dob_match:
        details['DOB/YOB'] = dob_match.group(1)
    elif yob_match:
        details['DOB/YOB'] = yob_match.group(2)
    else:
        details['DOB/YOB'] = 'Not Found'

   
    gender_match = re.search(r'\b(Male|Female|Transgender)\b', text, re.IGNORECASE)
    details['Gender'] = gender_match.group(1).capitalize() if gender_match else 'Not Found'

   
    aadhar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    details['Aadhar Number'] = aadhar_match.group(0) if aadhar_match else 'Not Found'

    return details


def extract_address(text):
    lines = text.split('\n')
    address_lines = []
    start = False

    start_keywords = ['Address','address','ADDRESS','s/o', 'c/o', 'd/o', 'w/o']
    stop_keywords = ['dob', 'date of birth', 'male', 'female', 'year of birth', 'yob']

    for line in lines:
        lower = line.lower().strip()
        if any(k in lower for k in start_keywords):
            start = True
            address_lines.append(line.strip())
        elif start:
            if any(k in lower for k in stop_keywords) or re.search(r'\d{4}\s\d{4}\s\d{4}', lower):
                break
            if line.strip():
                address_lines.append(line.strip())

    return ' '.join(address_lines).strip() if address_lines else 'Not Found'


def extract_from_aadhar_images(front_img_path, back_img_path):
   
    front_img = preprocess_image(front_img_path)
    front_text = pytesseract.image_to_string(front_img)
    front_details = extract_front_details(front_text)
    back_img = preprocess_image(back_img_path)
    back_text = pytesseract.image_to_string(back_img)
    address = extract_address(back_text)
    front_details['Address'] = address
    print("Front Text:\n", front_text)
    print("Back Text:\n", back_text)
    return front_details


if __name__ == "__main__":
    front_img_path = 'aadhar1_front.jpeg'   
    back_img_path = 'aadhar2_back.jpeg'    

    result = extract_from_aadhar_images(front_img_path, back_img_path)

    print("\n Extracted Aadhaar Details:")
    for key, value in result.items():
        print(f"{key}: {value}")