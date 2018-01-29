from pdfrw import PdfReader, PdfWriter
from pdf2image import convert_from_path, convert_from_bytes
import os.path


def split(file_path):
    """

    :param file_path: Full path to file
    :return:
    """
    # TO DO
    inpfn = file_path
    outfn = 'test1.pdf'
    pages = PdfReader(inpfn).pages
    writer = PdfWriter(outfn)
    writer.addpage(pages[0])
    writer.write()


def convert_to_png(file_path):
    """

    :param file_path:
    :return:
    """
    images = convert_from_path(file_path)
    i = 1
    for image in images:
        image.save(os.path.join(os.path.dirname(file_path), "%i.png" % i), format="PNG")
        i += 1


def save(file_id, file_body, file_dir="/"):
    """

    :param file_id:
    :param file_body:
    :param file_dir:
    :return:
    """
    file_name = str(file_id) + ".pdf"
    os.makedirs(os.path.join(os.path.dirname(__file__), "{}/{}".format(file_dir, str(file_id))))
    file_path = os.path.join(os.path.dirname(__file__), "{}/{}/{}".format(file_dir, str(file_id), file_name))
    with open(file_path, "wb") as f:
        f.write(file_body)
    convert_to_png(file_path)