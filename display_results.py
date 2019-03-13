import os, glob, io
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PyPDF2 import PdfFileMerger, PdfFileWriter, PdfFileReader

src = ['6_trapped_images', '3_resulted_images']
# src = ['2_cropped_images', '3_resulted_images']

dest = '/home/arfin/Documents/GitHub/tea/Flc/test_data/5_join'
test_data_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/'
image_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/1_images/*'
augmented_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/4_augmented'
test_pdf_path = '/home/arfin/Documents/GitHub/tea/Flc/test_data/7_pdf_files'


def merge_test_and_result():
    i = 0
    for path, subdirs, files in os.walk(test_data_path + src[0]):
        for name in sorted(files):
            os.rename(os.path.join(path, name), os.path.join(dest, str(i) + '_' + name + '.jpg'))
            i = i + 1

    j = 0
    for path, subdirs, files in os.walk(test_data_path + src[1]):
        for name in sorted(files):
            os.rename(os.path.join(path, name), os.path.join(dest, str(j) + '_' + name + '.jpg'))
            j = j + 1

    r = glob.glob(image_path)
    for i in r:
        os.remove(i)


def merge_pdf(report_count):
    pdf_files = []
    for pdf_file in glob.glob(test_data_path + '/*.pdf'):
        print("arbaz")
        print(pdf_file)
        pdf_files.append(pdf_file)
    print(pdf_files)

    merger = PdfFileMerger()

    for pdf in pdf_files:
        merger.append(open(pdf, 'rb'))

    with open(augmented_path + '/report' + str(report_count) + '.pdf', 'wb') as fout:
        merger.write(fout)

    print("\npdf report generated", 'report' + str(report_count) + '.pdf')

    os.system('rm ' + test_data_path + '/*.pdf')


def final_report_pdf():
    final_pdf_files = []
    for final_pdf_file in glob.glob(test_pdf_path + '/*.pdf'):
        final_pdf_files.append(final_pdf_file)

    print(final_pdf_files)

    merger = PdfFileMerger()

    for each in final_pdf_files:
        merger.append(open(each, 'rb'))

    with open('report.pdf', 'wb') as fout:
        merger.write(fout)

    print("\nFinal pdf report generated")

    os.system('rm ' + test_pdf_path + '/*.pdf')


def make_files_list():
    list_of_files = []
    for file in sorted(glob.glob(dest + '/*')):
        list_of_files.append(file)
    print("ARFIN")
    print(list_of_files)
    print("FARHAN")
    imgs_ts = [list_of_files[x:x + 32] for x in range(0, len(list_of_files), 32)]
    page_nmbr = 0
    for imgs_t in imgs_ts:
        imgs_32 = [imgs_t[x:x + 2] for x in range(0, len(imgs_t), 2)]
        page_nmbr = page_nmbr + 1
        make_pdf(imgs_32, test_data_path + "/" + "test_" + str(page_nmbr) + ".pdf")

    os.system('rm ' + dest + '/*')


def generate(images, cx, w, h, y, pdf_name):
    c = canvas.Canvas(pdf_name)
    # move the origin up and to the left
    c.translate(inch, inch)
    c.setFillColorRGB(1, 0, 1)
    for chunks in images:
        x = cx
        for each in chunks:
            print(each, x, y)
            x = x + w
            c.drawImage(each, x, y, w, h)
        y = y - h
        if (y == -160) and (x == 140):
            y = 640
            cx = 210
    c.showPage()
    c.save()


def make_pdf(images, pdf_name):
    w = 70
    h = 100
    y = 640
    cx = 0
    generate(images, cx, w, h, y, pdf_name)


def write_counts(text, report_count):
    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(30, 750, text)
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open(augmented_path + '/report' + str(report_count) + '.pdf', "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open(test_pdf_path + "/destination" + str(report_count) + ".pdf", "wb")
    output.write(outputStream)
    outputStream.close()

#
# write_counts('Fine counts = 9', 1)
# write_counts('Fine counts = 6', 2)