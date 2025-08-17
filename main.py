import easyocr
import cv2
import re
import os

def load_image(image_path):
    """Load image with validation"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    return img

def parse_prescription(text):
    """Enhanced parser for medical prescriptions"""
    tabs = {
        "Patient Info": {"Name": "Not found", "Age": "Not found"},
        "Diagnosis": "Not found",
        "Prescription": [],
        "Doctor": "Not found"
    }
    
    # Normalize text (remove extra spaces, make lowercase)
    clean_text = " ".join(text.split()).lower()
    
    # Improved extraction patterns
    patterns = {
        "name": r"(?:patient|name|pt)[\s:]*([^\n]+?)(?=\n|age|$)",
        "age": r"(?:age|years|y/o)[\s:]*(\d+)",
        "diagnosis": r"(?:diagnosis|dx|problem)[\s:]*([^\n]+?)(?=\n|rx|prescription|$)",
        "doctor": r"(?:doctor|dr|physician)[\s:]*([^\n]+)"
    }
    
    # Extract basic info
    for field, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if field == "name":
                tabs["Patient Info"]["Name"] = value.title()
            elif field == "age":
                tabs["Patient Info"]["Age"] = value
            elif field == "diagnosis":
                tabs["Diagnosis"] = value.title()
            elif field == "doctor":
                tabs["Doctor"] = value.title()
    
    # Enhanced prescription item detection
    rx_section = re.search(r"(?:prescription|rx|medication)[\s:]*([\s\S]+?)(?=\n\s*\n|doctor|$)", text, re.IGNORECASE)
    if rx_section:
        rx_text = rx_section.group(1)
        # Match various prescription formats
        rx_items = re.finditer(r"(\d+\.|\-|\*|•)\s*([^\n]+)|([^\n]+?)\s*(?=\n\d+\.|\n\-|\n\*|\n•|$)", rx_text)
        for match in rx_items:
            item = match.group(2) or match.group(3)
            if item and len(item.strip()) > 3:  # Filter out noise
                tabs["Prescription"].append(item.strip())
    
    return tabs

def main():
    # Initialize EasyOCR
    reader = easyocr.Reader(['en'])
    
    try:
        # Use absolute path to your image
        image_path = os.path.abspath(r"D:\ANNLEE\smtg\cbit\capstone\capstone 2 ig\Capture_Prescription.JPG")
        
        if not os.path.exists(image_path):
            print(f"Error: File not found at {image_path}")
            return
        
        # Process image
        img = load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # OCR with enhanced configuration
        results = reader.readtext(gray, 
                                paragraph=True,
                                detail=0,
                                contrast_ths=0.5,
                                adjust_contrast=0.7)
        
        full_text = "\n".join(results)
        print("\nRaw OCR Text:\n", full_text)  # Debug output
        
        # Parse the prescription
        prescription_tabs = parse_prescription(full_text)
        
        # Display results
        print("\n" + "="*50)
        print("PRESCRIPTION ANALYSIS")
        print("="*50)
        
        print("\n=== PATIENT INFO ===")
        print(f"Name: {prescription_tabs['Patient Info']['Name']}")
        print(f"Age: {prescription_tabs['Patient Info']['Age']}")
        
        print("\n=== DIAGNOSIS ===")
        print(prescription_tabs["Diagnosis"])
        
        print("\n=== PRESCRIPTION ===")
        for i, med in enumerate(prescription_tabs["Prescription"], 1):
            print(f"{i}. {med}")
            
        print("\n=== DOCTOR ===")
        print(prescription_tabs["Doctor"])
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    main()