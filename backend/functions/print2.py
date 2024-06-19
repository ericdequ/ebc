from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image
import os
import zipfile

# Define the trim sizes
TRIM_SIZES = {
    '5 x 8 in': (5 * 72, 8 * 72),
    '5.25 x 8 in': (5.25 * 72, 8 * 72),
    '5.5 x 8.5 in': (5.5 * 72, 8.5 * 72),
    '6 x 9 in': (6 * 72, 9 * 72),
    '5.06 x 7.81 in': (5.06 * 72, 7.81 * 72),
    '6.14 x 9.21 in': (6.14 * 72, 9.21 * 72),
    '6.69 x 9.61 in': (6.69 * 72, 9.61 * 72),
    '7 x 10 in': (7 * 72, 10 * 72),
    '7.44 x 9.69 in': (7.44 * 72, 9.69 * 72),
    '7.5 x 9.25 in': (7.5 * 72, 9.25 * 72),
    '8 x 10 in': (8 * 72, 10 * 72),
    '8.5 x 11 in': (8.5 * 72, 11 * 72),
    '8.27 x 11.69 in': (8.27 * 72, 11.69 * 72),
    '8.25 x 6 in': (8.25 * 72, 6 * 72),
    '8.25 x 8.25 in': (8.25 * 72, 8.25 * 72),
    '8.5 x 8.5 in': (8.5 * 72, 8.5 * 72)
}

def resize_and_position_image(image_path, target_width, target_height, keep_aspect_ratio=True):
    try:
        img = Image.open(image_path)
        original_width, original_height = img.size

        if keep_aspect_ratio:
            ratio = min(target_width / original_width, target_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
        else:
            img = img.resize((target_width, target_height), Image.ANTIALIAS)

        new_img = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        new_img.paste(img, (paste_x, paste_y))

        output_path = 'resized_' + os.path.basename(image_path)
        new_img.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error resizing and positioning image: {e}")
        return None

def set_page_size(pdf_path, page_size, margins=(0.5*72, 0.5*72, 0.5*72, 0.5*72)):
    try:
        reader = PdfFileReader(pdf_path)
        writer = PdfFileWriter()
        width, height = page_size

        for page_num in range(reader.getNumPages()):
            page = reader.getPage(page_num)
            new_page = writer.addBlankPage(width, height)
            new_page.mergePage(page)

            content_width = width - margins[1] - margins[3]
            content_height = height - margins[0] - margins[2]
            new_page.scaleTo(content_width, content_height)
            new_page.trimBox.lowerLeft = (margins[3], margins[2])
            new_page.trimBox.upperRight = (width - margins[1], height - margins[0])

            writer.addPage(new_page)

        output_path = f'print_ready_{os.path.basename(pdf_path).replace(".pdf", "")}_{width}x{height}.pdf'
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    except Exception as e:
        print(f"Error setting page size: {e}")
        return None

def add_bleeds_and_crop_marks(pdf_path, bleed_size=0.125*72):
    try:
        reader = PdfFileReader(pdf_path)
        writer = PdfFileWriter()

        for page_num in range(reader.getNumPages()):
            page = reader.getPage(page_num)
            width = page.mediaBox.getWidth()
            height = page.mediaBox.getHeight()

            new_page = writer.addBlankPage(width + 2*bleed_size, height + 2*bleed_size)
            new_page.mergeTranslatedPage(page, bleed_size, bleed_size)

            new_page.drawLine((bleed_size, 0), (bleed_size, bleed_size))
            new_page.drawLine((0, bleed_size), (bleed_size, bleed_size))
            new_page.drawLine((width + bleed_size, 0), (width + bleed_size, bleed_size))
            new_page.drawLine((width + 2*bleed_size, bleed_size), (width + bleed_size, bleed_size))
            new_page.drawLine((bleed_size, height + bleed_size), (bleed_size, height + 2*bleed_size))
            new_page.drawLine((0, height + bleed_size), (bleed_size, height + bleed_size))
            new_page.drawLine((width + bleed_size, height + bleed_size), (width + bleed_size, height + 2*bleed_size))
            new_page.drawLine((width + 2*bleed_size, height + bleed_size), (width + bleed_size, height + bleed_size))

            writer.addPage(new_page)

        output_path = 'bleeds_' + os.path.basename(pdf_path)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    except Exception as e:
        print(f"Error adding bleeds and crop marks: {e}")
        return None

def generate_cover_pages(cover_image_path, back_cover_image_path, spine_width, output_path='cover.pdf'):
    try:
        cover_img = Image.open(cover_image_path)
        back_cover_img = Image.open(back_cover_image_path)

        width, height = cover_img.size
        total_width = 2*width + spine_width

        cover = Image.new('RGB', (total_width, height), (255, 255, 255))
        cover.paste(back_cover_img, (0, 0))
        cover.paste(cover_img, (width + spine_width, 0))

        cover.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error generating cover pages: {e}")
        return None

def embed_fonts(pdf_path, output_path='embedded_fonts.pdf'):
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        for page in doc:
            for font in page.get_fonts(full=True):
                font_name = font[3]
                # Placeholder for actual font embedding logic

        doc.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error embedding fonts: {e}")
        return None

def merge_pdfs(pdf_paths, output_path='merged.pdf'):
    try:
        writer = PdfFileWriter()

        for pdf_path in pdf_paths:
            reader = PdfFileReader(pdf_path)
            for page_num in range(reader.getNumPages()):
                writer.addPage(reader.getPage(page_num))

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return None

def create_print_ready_book(pdf_path, cover_image_path, back_cover_image_path, trim_sizes, spine_width=36, output_zip='print_ready_books.zip'):
    try:
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for size_name, size in trim_sizes.items():
                # Step 1: Set up page size and margins
                formatted_pdf = set_page_size(pdf_path, page_size=size)

                # Step 2: Add bleeds and crop marks
                pdf_with_bleeds = add_bleeds_and_crop_marks(formatted_pdf)

                # Step 3: Generate cover pages
                cover_pdf = generate_cover_pages(cover_image_path, back_cover_image_path, spine_width)

                # Step 4: Combine cover and content
                combined_pdf = merge_pdfs([cover_pdf, pdf_with_bleeds])

                # Step 5: Embed fonts
                print_ready_pdf = embed_fonts(combined_pdf)

                # Save the final print-ready PDF in the zip file
                zipf.write(print_ready_pdf, os.path.basename(print_ready_pdf))

        return output_zip
    except Exception as e:
        print(f"Error creating print-ready book: {e}")
        return None

# Example usage
output_zip = create_print_ready_book('example.pdf', 'cover.jpg', 'back_cover.jpg', TRIM_SIZES)
print(f"Print-ready books saved in: {output_zip}")
