from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image

def resize_and_position_image(image_path, target_width, target_height, keep_aspect_ratio=True):
    """Resize and position an image within the target dimensions."""
    img = Image.open(image_path)
    original_width, original_height = img.size

    if keep_aspect_ratio:
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
    else:
        img = img.resize((target_width, target_height), Image.ANTIALIAS)

    # Create a new image with white background and paste the resized image
    new_img = Image.new('RGB', (target_width, target_height), (255, 255, 255))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    new_img.paste(img, (paste_x, paste_y))

    output_path = 'resized_' + os.path.basename(image_path)
    new_img.save(output_path)
    return output_path


def set_page_size(pdf_path, page_size=letter, margins=(0.5*72, 0.5*72, 0.5*72, 0.5*72)):
    """Set page size and margins for print-ready PDF."""
    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()
    width, height = page_size

    for page_num in range(reader.getNumPages()):
        page = reader.getPage(page_num)
        new_page = writer.addBlankPage(width, height)
        new_page.mergePage(page)

        # Apply margins and resizing logic here
        # Example: Center content within margins
        content_width = width - margins[1] - margins[3]
        content_height = height - margins[0] - margins[2]
        new_page.scaleTo(content_width, content_height)
        new_page.trimBox.lowerLeft = (margins[3], margins[2])
        new_page.trimBox.upperRight = (width - margins[1], height - margins[0])

        writer.addPage(new_page)

    output_path = 'print_ready_' + os.path.basename(pdf_path)
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    return output_path


def add_bleeds_and_crop_marks(pdf_path, bleed_size=0.125*72):
    """Add bleeds and crop marks to a PDF."""
    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()

    for page_num in range(reader.getNumPages()):
        page = reader.getPage(page_num)
        width = page.mediaBox.getWidth()
        height = page.mediaBox.getHeight()

        new_page = writer.addBlankPage(width + 2*bleed_size, height + 2*bleed_size)
        new_page.mergeTranslatedPage(page, bleed_size, bleed_size)

        # Add crop marks here
        # Example: Draw crop marks at the corners
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


def generate_cover_pages(cover_image_path, back_cover_image_path, spine_width, output_path='cover.pdf'):
    """Generate cover pages with spine for a print-ready book."""
    cover_img = Image.open(cover_image_path)
    back_cover_img = Image.open(back_cover_image_path)

    width, height = cover_img.size
    total_width = 2*width + spine_width

    cover = Image.new('RGB', (total_width, height), (255, 255, 255))
    cover.paste(back_cover_img, (0, 0))
    cover.paste(cover_img, (width + spine_width, 0))

    cover.save(output_path)
    return output_path


def embed_fonts(pdf_path, output_path='embedded_fonts.pdf'):
    """Embed fonts in a PDF to ensure correct rendering when printed."""
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    for page in doc:
        for font in page.get_fonts(full=True):
            font_name = font[3]
            # Logic to embed the font

    doc.save(output_path)
    return output_path


def create_print_ready_book(pdf_path, cover_image_path, back_cover_image_path, target_paper_size=letter, spine_width=36):
    """Create a print-ready PDF book with cover pages and correct formatting."""
    # Step 1: Set up page size and margins
    formatted_pdf = set_page_size(pdf_path, page_size=target_paper_size)
    
    # Step 2: Add bleeds and crop marks
    pdf_with_bleeds = add_bleeds_and_crop_marks(formatted_pdf)
    
    # Step 3: Generate cover pages
    cover_pdf = generate_cover_pages(cover_image_path, back_cover_image_path, spine_width)
    
    # Step 4: Combine cover and content
    combined_pdf = merge_pdfs([cover_pdf, pdf_with_bleeds])
    
    # Step 5: Embed fonts
    print_ready_pdf = embed_fonts(combined_pdf)
    
    return print_ready_pdf

# Example usage
print_ready_pdf = create_print_ready_book('../test_data/RR.pdf', '../test_data/front.jpg', '../test_data/back.jpg')
