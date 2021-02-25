from PyPDF2 import PdfFileReader, PdfFileWriter


def merge_pdfs(paths, output, password=None):
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(path["path"])
        for page in range(path["min"]-1, path["max"]):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)


def add_encryption(input_pdf, output_pdf, password):
    pdf_writer = PdfFileWriter()
    pdf_reader = PdfFileReader(input_pdf)

    for page in range(pdf_reader.getNumPages()):
        pdf_writer.addPage(pdf_reader.getPage(page))

    pdf_writer.encrypt(user_pwd=password, owner_pwd=password,
                       use_128bit=True)

    with open(output_pdf, 'wb') as fh:
        pdf_writer.write(fh)


def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    txt = f"""
    Information about {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """

    print(txt)
    return information


def get_max_pages(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        number_of_pages = pdf.getNumPages()
        return number_of_pages


def unlock(pdf_path, password):
    pdf_writer = PdfFileWriter()
    pdf_reader = PdfFileReader(pdf_path)
    if pdf_reader.isEncrypted:
        pdf_reader.decrypt(password)
    for page in range(pdf_reader.getNumPages()):
        pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    with open(pdf_path, 'wb') as out:
        pdf_writer.write(out)