from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import os

def resize_and_position_image(image_path, target_width, target_height, keep_aspect_ratio=True):
    """
    Resize and position an image within the target dimensions.

    Args:
    - image_path (str): Path to the input image.
    - target_width (int): The target width of the resized image.
    - target_height (int): The target height of the resized image.
    - keep_aspect_ratio (bool): Whether to maintain the aspect ratio of the image.

    Returns:
    - output_path (str): Path to the resized image.
    """
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

        # Create a new image with a white background and paste the resized image
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

def set_page_size(pdf_path, page_size=letter, margins=(0.5*72, 0.5*72, 0.5*72, 0.5*72)):
    """
    Set page size and margins for a print-ready PDF.

    Args:
    - pdf_path (str): Path to the input PDF file.
    - page_size (tuple): The target page size.
    - margins (tuple): Margins (left, right, top, bottom) in points.

    Returns:
    - output_path (str): Path to the resized PDF.
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        width, height = page_size

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            new_page = writer.add_blank_page(width, height)
            new_page.merge_page(page)

            # Center content within margins
            content_width = width - margins[1] - margins[3]
            content_height = height - margins[0] - margins[2]
            new_page.scale_to(content_width, content_height)
            new_page.trimbox.lower_left = (margins[3], margins[2])
            new_page.trimbox.upper_right = (width - margins[1], height - margins[0])

            writer.add_page(new_page)

        output_path = 'print_ready_' + os.path.basename(pdf_path)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    except Exception as e:
        print(f"Error setting page size: {e}")
        return None

def add_bleeds_and_crop_marks(pdf_path, bleed_size=0.125*72):
    """
    Add bleeds and crop marks to a PDF.

    Args:
    - pdf_path (str): Path to the input PDF file.
    - bleed_size (float): Size of the bleed area in points.

    Returns:
    - output_path (str): Path to the PDF with bleeds and crop marks.
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            new_page = writer.add_blank_page(width + 2*bleed_size, height + 2*bleed_size)
            new_page.merge_transformed_page(page, (1, 0, 0, 1, bleed_size, bleed_size))

            # Draw crop marks at the corners
            new_page.add_line((bleed_size, 0), (bleed_size, bleed_size))
            new_page.add_line((0, bleed_size), (bleed_size, bleed_size))
            new_page.add_line((width + bleed_size, 0), (width + bleed_size, bleed_size))
            new_page.add_line((width + 2*bleed_size, bleed_size), (width + bleed_size, bleed_size))
            new_page.add_line((bleed_size, height + bleed_size), (bleed_size, height + 2*bleed_size))
            new_page.add_line((0, height + bleed_size), (bleed_size, height + bleed_size))
            new_page.add_line((width + bleed_size, height + bleed_size), (width + bleed_size, height + 2*bleed_size))
            new_page.add_line((width + 2*bleed_size, height + bleed_size), (width + bleed_size, height + bleed_size))

            writer.add_page(new_page)

        output_path = 'bleeds_' + os.path.basename(pdf_path)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    except Exception as e:
        print(f"Error adding bleeds and crop marks: {e}")
        return None

def generate_cover_pages(cover_image_path, back_cover_image_path, spine_width, output_path='cover.pdf'):
    """
    Generate cover pages with a spine for a print-ready book.

    Args:
    - cover_image_path (str): Path to the front cover image.
    - back_cover_image_path (str): Path to the back cover image.
    - spine_width (int): Width of the spine in points.
    - output_path (str): Path to the generated cover PDF.

    Returns:
    - output_path (str): Path to the generated cover PDF.
    """
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
    """
    Embed fonts in a PDF to ensure correct rendering when printed.

    Args:
    - pdf_path (str): Path to the input PDF file.
    - output_path (str): Path to the PDF with embedded fonts.

    Returns:
    - output_path (str): Path to the PDF with embedded fonts.
    """
    try:
        from PyPDF2 import PdfReader, PdfWriter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            writer.add_page(page)

        # Embed the fonts
        font_dir = './fonts'  # Directory containing the font files
        for font_file in os.listdir(font_dir):
            if font_file.endswith('.ttf') or font_file.endswith('.otf'):
                font_path = os.path.join(font_dir, font_file)
                font_name = os.path.splitext(font_file)[0]
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                writer.add_font(font_name, font_path)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    except Exception as e:
        print(f"Error embedding fonts: {e}")
        return None

def merge_pdfs(pdf_paths, output_path='merged.pdf'):
    """
    Merge multiple PDF files into one.

    Args:
    - pdf_paths (list): List of paths to the input PDF files.
    - output_path (str): Path to the output merged PDF file.

    Returns:
    - output_path (str): Path to the merged PDF file.
    """
    try:
        writer = PdfWriter()

        for pdf_path in pdf_paths:
            reader = PdfReader(pdf_path)
            for page_num in range(len(reader.pages)):
                writer.add_page(reader.pages[page_num])

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return None

def create_print_ready_book(pdf_path, cover_image_path, back_cover_image_path, target_paper_size=letter, spine_width=36):
    """
    Create a print-ready PDF book with cover pages and correct formatting.

    Args:
    - pdf_path (str): Path to the input PDF file.
    - cover_image_path (str): Path to the front cover image.
    - back_cover_image_path (str): Path to the back cover image.
    - target_paper_size (tuple): The target paper size.
    - spine_width (int): Width of the spine in points.

    Returns:
    - print_ready_pdf (str): Path to the print-ready PDF book.
    """
    try:
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
    except Exception as e:
        print(f"Error creating print-ready book: {e}")
        return None

# Example usage
print_ready_pdf = create_print_ready_book('../test_data/RR.pdf', '../test_data/front.jpg', '../test_data/back.jpg')