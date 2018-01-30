from pdfrw import PdfReader, PdfWriter
from pdf2image import convert_from_path, convert_from_bytes
import os.path
import zipfile


def split(file_path):
    """

    :param file_path: Full path to file
    :return: Number of splited pages
    """
    pages = PdfReader(file_path).pages
    pages_number = len(pages)
    for i in range(pages_number):
        out_path = os.path.join(os.path.dirname(file_path), 'page{}.pdf'.format(i + 1))
        writer = PdfWriter(out_path)
        writer.addpage(pages[i])
        writer.write()
    return pages_number


def convert_to_png(file_path):
    """

    :param file_path:
    :return:
    """
    images = convert_from_path(file_path)
    i = 1
    for image in images:
        image.save(file_path.replace("pdf", "png"), format="PNG")
        i += 1


def save(file_id, file_body, file_dir="/"):
    """

    :param file_id:
    :param file_body:
    :param file_dir:
    :return:
    """
    file_name = str(file_id) + ".pdf"
    main_dir = os.path.join(os.path.dirname(__file__), "{}/{}".format(file_dir, str(file_id)))
    os.makedirs(main_dir)
    file_path = os.path.join(os.path.dirname(__file__), "{}/{}/{}".format(file_dir, str(file_id), file_name))
    with open(file_path, "wb") as f:
        f.write(file_body)
    # Split pages
    pages_number = split(file_path)
    # Saving PNG splited files
    for i in range(pages_number):
        convert_to_png(os.path.join(os.path.dirname(file_path), 'page{}.pdf'.format(i + 1)))
    # Saving to ZIP
    z = zipfile.ZipFile(os.path.join(main_dir, '%i.zip' % file_id), 'w')
    for root, dirs, files in os.walk(main_dir):
        for file in files:
            if file == file_name or file[-4:] == ".png":
                z.write(os.path.join(root, file))
    z.close()
