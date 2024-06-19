from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfFileReader, PdfFileWriter
from docx import Document
import cv2
import os
from ebooklib import epub
import tensorflow as tf
from PIL import Image
import io
from kindle_mobi import Mobi
import img2pdf

app = Flask(__name__)

def process_pdf(file):
    """Process a PDF file and extract text."""
    reader = PdfFileReader(file)
    text_content = ""
    for page_num in range(reader.getNumPages()):
        page = reader.getPage(page_num)
        text_content += page.extractText()
    return text_content

def process_docx(file):
    """Process a DOCX file and extract text."""
    doc = Document(file)
    text_content = "\n".join([para.text for para in doc.paragraphs])
    return text_content

def resize_image(image_path, width, height):
    """Resize an image to the specified dimensions."""
    img = cv2.imread(image_path)
    resized_img = cv2.resize(img, (width, height))
    resized_path = 'resized_' + os.path.basename(image_path)
    cv2.imwrite(resized_path, resized_img)
    return resized_path

def create_epub(text_content, title="Sample Ebook", author="Author Name"):
    """Create an EPUB file from text content."""
    book = epub.EpubBook()
    book.set_title(title)
    book.add_author(author)
    chapter = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', content=text_content)
    book.add_item(chapter)
    epub_path = 'sample.epub'
    epub.write_epub(epub_path, book, {})
    return epub_path

def convert_to_mobi(epub_path):
    """Convert an EPUB file to MOBI format."""
    mobi_path = epub_path.replace('.epub', '.mobi')
    Mobi(epub_path).write(mobi_path)
    return mobi_path

def compress_pdf(file):
    """Compress a PDF file."""
    reader = PdfFileReader(file)
    writer = PdfFileWriter()
    for page_num in range(reader.getNumPages()):
        page = reader.getPage(page_num)
        writer.addPage(page)
    compressed_path = 'compressed.pdf'
    with open(compressed_path, 'wb') as output_file:
        writer.write(output_file)
    return compressed_path

def enhance_image(image_path):
    """Apply AI-based image enhancement."""
    img = Image.open(image_path)
    # Apply AI-based enhancement techniques (e.g., super-resolution, denoising)
    # Here, we're just applying a simple sharpening filter as an example
    enhanced_img = img.filter(Image.SHARPEN)
    enhanced_path = 'enhanced_' + os.path.basename(image_path)
    enhanced_img.save(enhanced_path)
    return enhanced_path

def convert_images_to_pdf(image_paths):
    """Convert multiple images to a PDF file."""
    pdf_path = 'converted.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(img2pdf.convert(image_paths))
    return pdf_path

def convert_pdf_to_images(pdf_path):
    """Convert a PDF file to multiple images."""
    images = []
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        for page_num in range(pdf.getNumPages()):
            page = pdf.getPage(page_num)
            # Extract images from the page and save them
            # Append the image paths to the `images` list
    return images

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process PDF/DOCX files."""
    file = request.files['file']
    file_type = file.filename.split('.')[-1].lower()
    width = int(request.form.get('width', 800))
    height = int(request.form.get('height', 600))
    text_content = ""

    if file_type == 'pdf':
        text_content = process_pdf(file)
        compressed_path = compress_pdf(file)
    elif file_type == 'docx':
        text_content = process_docx(file)

    epub_path = create_epub(text_content)
    mobi_path = convert_to_mobi(epub_path)
    return jsonify({
        'message': 'File processed',
        'epub_path': epub_path,
        'mobi_path': mobi_path,
        'compressed_path': compressed_path
    })

@app.route('/resize_image', methods=['POST'])
def resize_image_route():
    """Resize an image."""
    file = request.files['file']
    book_type = request.form.get('book_type', 'softcover')
    if book_type == 'softcover':
        width = int(request.form.get('softcover_width', 800))
        height = int(request.form.get('softcover_height', 600))
    else:
        width = int(request.form.get('hardcover_width', 1000))
        height = int(request.form.get('hardcover_height', 800))
    file_path = 'uploaded_' + file.filename
    file.save(file_path)
    resized_path = resize_image(file_path, width, height)
    enhanced_path = enhance_image(resized_path)
    return jsonify({
        'message': 'Image resized and enhanced',
        'resized_path': resized_path,
        'enhanced_path': enhanced_path
    })

@app.route('/convert_images_to_pdf', methods=['POST'])
def convert_images_to_pdf_route():
    """Convert multiple images to a PDF file."""
    files = request.files.getlist('files')
    image_paths = []
    for file in files:
        file_path = 'uploaded_' + file.filename
        file.save(file_path)
        image_paths.append(file_path)
    pdf_path = convert_images_to_pdf(image_paths)
    return jsonify({'message': 'Images converted to PDF', 'pdf_path': pdf_path})

@app.route('/convert_pdf_to_images', methods=['POST'])
def convert_pdf_to_images_route():
    """Convert a PDF file to multiple images."""
    file = request.files['file']
    file_path = 'uploaded_' + file.filename
    file.save(file_path)
    image_paths = convert_pdf_to_images(file_path)
    return jsonify({'message': 'PDF converted to images', 'image_paths': image_paths})

@app.route('/download_epub/<path:filename>', methods=['GET'])
def download_epub(filename):
    """Download an EPUB file."""
    return send_file(filename, as_attachment=True)

@app.route('/download_mobi/<path:filename>', methods=['GET'])
def download_mobi(filename):
    """Download a MOBI file."""
    return send_file(filename, as_attachment=True)

@app.route('/download_compressed_pdf/<path:filename>', methods=['GET'])
def download_compressed_pdf(filename):
    """Download a compressed PDF file."""
    return send_file(filename, as_attachment=True)

@app.route('/download_resized_image/<path:filename>', methods=['GET'])
def download_resized_image(filename):
    """Download a resized image."""
    return send_file(filename, as_attachment=True)

@app.route('/download_enhanced_image/<path:filename>', methods=['GET'])
def download_enhanced_image(filename):
    """Download an enhanced image."""
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)