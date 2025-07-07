import os
import fitz  # PyMuPDF
import pytesseract
from PyPDF2 import PdfReader
from PIL import Image
import io
import csv
import subprocess
import json
import sys

if len(sys.argv) < 2:
    print("❌ Error: PDF folder path not provided.")
    sys.exit(1)

pdf_folder = sys.argv[1]

# 📄 Output CSV path
output_csv = os.path.join(pdf_folder, "document_summary.csv")

# 🔍 Check if PDF is image-based
def is_image_based_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        if page.extract_text():
            return False
    return True

# 🧾 Extract text from image-based PDF using OCR
def extract_text_from_image_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text += pytesseract.image_to_string(img)
    return text

# 📄 Extract text from text-based PDF
def extract_text_from_text_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

# 🤖 Use Ollama (LLaMA 3) to classify and summarize
def classify_and_summarize(text):
    prompt = f"""
You are a document classification and summarization assistant.

Based on the content below, identify the type of document and write a summary of less than 100 words.

Document Content:
{text[:3000]}

Respond in this format:
Document Type: <Type>
Summary: <Summary>
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        output = result.stdout.decode("utf-8").strip()

        doc_type = "Unknown"
        summary = "N/A"
        if "Document Type:" in output and "Summary:" in output:
            parts = output.split("Summary:")
            doc_type = parts[0].replace("Document Type:", "").strip()
            summary = parts[1].strip()

        return doc_type, summary

    except subprocess.TimeoutExpired:
        return "Timeout", "LLM processing took too long."
    except Exception as e:
        return "Error", str(e)

# 🧠 Process PDFs
results = []
pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]

for idx, pdf_file in enumerate(pdf_files, 1):
    pdf_path = os.path.join(pdf_folder, pdf_file)
    print(f"[{idx}] Processing {pdf_file}...")

    is_image = is_image_based_pdf(pdf_path)
    content = extract_text_from_image_pdf(pdf_path) if is_image else extract_text_from_text_pdf(pdf_path)

    if not content.strip():
        doc_type, summary = "Unreadable or Empty", "No extractable content found."
    else:
        doc_type, summary = classify_and_summarize(content)

    results.append([idx, pdf_file, doc_type, summary])

# 💾 Save to CSV
with open(output_csv, mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Serial Number", "PDF Name", "Type of Document", "Summary"])
    writer.writerows(results)

print(f"\n✅ Process complete. Results saved to: {output_csv}")
