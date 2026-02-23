import pypdf
import argparse

def add_bookmarks_to_pdf(input_pdf_path, output_pdf_path, toc_file_path, page_offset=0):
    """
    Reads a text file containing TOC data and adds it as bookmarks to a PDF.

    :param input_pdf_path: Path to the original PDF.
    :param output_pdf_path: Path where the new PDF with bookmarks will be saved.
    :param toc_file_path: Path to the text file containing the TOC.
    :param page_offset: Difference between the printed page number and the PDF's actual 0-indexed page count.
    """
    # Initialize reader and writer
    reader = pypdf.PdfReader(input_pdf_path)
    writer = pypdf.PdfWriter()

    # Copy all pages from the original PDF to the new writer object
    for page in reader.pages:
        writer.add_page(page)

    # Dictionary to track the parent items for nesting.
    # Level 0 is None (meaning it's a top-level bookmark).
    parents = {0: None}

    with open(toc_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue

            try:
                # Parse the line based on the pipe delimiter
                level_str, title, page_str = line.split('|')

                level = int(level_str.strip())
                title = title.strip()

                # PyPDF2 is 0-indexed (Page 1 is index 0).
                # The offset handles PDFs where the printed "Page 1" is actually the 10th page of the file.
                printed_page = int(page_str.strip())
                actual_pdf_index = printed_page - 1 + page_offset

                # Prevent crashing if page numbers are out of bounds
                actual_pdf_index = max(0, min(actual_pdf_index, len(reader.pages) - 1))

                # Get the parent bookmark object from the level above
                parent_bookmark = parents.get(level - 1)

                # Add the bookmark to the PDF
                new_bookmark = writer.add_outline_item(
                    title=title,
                    page_number=actual_pdf_index,
                    parent=parent_bookmark
                )

                # Store this new bookmark as the potential parent for the next level
                parents[level] = new_bookmark

            except ValueError:
                print(f"Skipping invalid line format: {line}. Please use 'Level | Title | Page'")

    # Save the final result
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

    print(f"Successfully added bookmarks and saved to: {output_pdf_path}")


# ... [Keep the add_bookmarks_to_pdf function exactly as it was] ...

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Add hierarchical bookmarks to a PDF using a formatted text file."
    )

    # Define positional arguments (required)
    parser.add_argument(
        "input_pdf",
        help="Path to the original PDF file."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default = "",
        help="Path where the new PDF with bookmarks will be saved. Default value will be input with _with_bookmark as suffix"
    )
    parser.add_argument(
        "toc_file",
        help="Path to the text file containing the Table of Contents."
    )

    # Define optional argument for the page offset
    parser.add_argument(
        "-s", "--start",
        type=int,
        default=1,
        help="Starting Page number. Default is 1."
    )

    # Parse the arguments from the command line
    args = parser.parse_args()

    output = args.output
    if output == "":
        output = args.input_pdf.rstrip(".pdf") + "_with_bookmarks.pdf"

    if args.start < 1:
        raise Exception("Starting page can't be less than 1")

    # Call the function with the parsed arguments
    add_bookmarks_to_pdf(args.input_pdf, output, args.toc_file, args.start-1)

if __name__ == "__main__":

    main()
