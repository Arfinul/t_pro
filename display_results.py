import os, glob, io, shutil, configparser
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PyPDF2 import PdfFileMerger, PdfFileWriter, PdfFileReader


config = configparser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'

src = ['6_trapped_images', '3_resulted_images']
src_without_fil = ['2_cropped_images', '3_resulted_images']

image_dir = '/1_images'
join_dir = '/5_join'
augmented_dir = '/4_augmented'
pdf_dir = '/7_pdf_files'
report_path = root_folder + '/reports'


def write_counts(text, user_dir):
    packet = io.BytesIO()
    test_pdf_path = user_dir + pdf_dir
    test_data_path = user_dir + '/'

    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(30, 750, text)
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)

    shutil.move(test_data_path + '/test_1.pdf', test_pdf_path)

    # read your existing PDF
    existing_pdf = PdfFileReader(open(test_pdf_path + '/test_1.pdf', "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open(test_data_path + "/test_1.pdf", "wb")
    output.write(outputStream)
    outputStream.close()
    os.system('rm ' + test_pdf_path + '/*')


def merge_test_and_result(userId, sectionId):
    i = 0
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    test_data_path = user_dir + '/'
    image_path = user_dir + image_dir + '/*'
    dest = user_dir + join_dir

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
        
        
def merge_test_and_result_without_fil(userId, sectionId):
    i = 0
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    test_data_path = user_dir + '/'
    image_path = user_dir + image_dir + '/*'
    dest = user_dir + join_dir

    for path, subdirs, files in os.walk(test_data_path + src_without_fil[0]):
        for name in sorted(files):
            if i < 10:
                os.rename(os.path.join(path, name), os.path.join(dest, '0' + str(i) + '_' + name + '.jpg'))
            else:
                os.rename(os.path.join(path, name), os.path.join(dest, str(i) + '_' + name + '.jpg'))

            i = i + 1

    j = 0
    for path, subdirs, files in os.walk(test_data_path + src_without_fil[1]):
        for name in sorted(files):
            if j < 10:
                os.rename(os.path.join(path, name), os.path.join(dest, '0' + str(j) + '_' + name + '.jpg'))
            else:
                os.rename(os.path.join(path, name), os.path.join(dest, str(j) + '_' + name + '.jpg'))

            j = j + 1

    r = glob.glob(image_path)
    for i in r:
        os.remove(i)


def merge_pdf(report_count, userId, sectionId):
    pdf_files = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    test_data_path = user_dir + '/'
    augmented_path = user_dir + augmented_dir

    for pdf_file in glob.glob(test_data_path + '/*.pdf'):
        #print("Merged all test number images")
        pdf_files.append(pdf_file)

    merger = PdfFileMerger()

    for pdf in sorted(pdf_files):
        merger.append(open(pdf, 'rb'))

    with open(augmented_path + '/report' + str(report_count) + '.pdf', 'wb') as fout:
        merger.write(fout)
    #print("\npdf report generated", 'report' + str(report_count) + '.pdf')
    os.system('rm ' + test_data_path + '/*.pdf')
    
    
def merge_pdf_without_r(userId, sectionId):
    pdf_files = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    test_data_path = user_dir + '/'
    augmented_path = user_dir + augmented_dir

    for pdf_file in sorted(glob.glob(test_data_path + '/*.pdf')):
        print("Merged all test number images")
        print(pdf_file)
        pdf_files.append(pdf_file)
    print(pdf_files)

    merger = PdfFileMerger()

    for pdf in sorted(pdf_files):
        merger.append(open(pdf, 'rb'))

    with open(augmented_path + '/report' + '.pdf', 'wb') as fout:
        merger.write(fout)

    print("\npdf report generated", 'report.pdf')

    os.system('rm ' + test_data_path + '/*.pdf')


def final_report_pdf(userId, sectionId):
    import datetime
    final_pdf_files = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    augmented_path = user_dir + augmented_dir


    for final_pdf_file in glob.glob(augmented_path + '/*.pdf'):
        final_pdf_files.append(final_pdf_file)

    merger = PdfFileMerger()

    for each in sorted(final_pdf_files):
        merger.append(open(each, 'rb'))

    with open(report_path + '/report_'+ str(datetime.datetime.now())+'.pdf', 'wb') as fout:
        merger.write(fout)

    print("Final pdf report generated")

    # os.system('rm ' + augmented_path + '/*.pdf')


def make_files_list(report_count,fine_count, coarse_count, userId, sectionId):
    list_of_files = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    dest = user_dir + join_dir
    test_data_path = user_dir + '/'

    for file in sorted(glob.glob(dest + '/*')):
        list_of_files.append(file)
    #print(list_of_files)
    imgs_ts = [list_of_files[x:x + 32] for x in range(0, len(list_of_files), 32)]
    page_nmbr = 0
    for imgs_t in imgs_ts:
        imgs_32 = [imgs_t[x:x + 2] for x in range(0, len(imgs_t), 2)]
        page_nmbr = page_nmbr + 1
        make_pdf(imgs_32, test_data_path + "/" + "test_" + str(page_nmbr) + ".pdf")

    if report_count == 1:
        write_counts('Fine counts = ' + str(fine_count), user_dir)
    if report_count == 2:
        write_counts('Coarse counts = ' + str(coarse_count), user_dir)

    os.system('rm ' + dest + '/*')
    
    
def make_files_list_without_r(userId, sectionId):
    list_of_files = []
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId
    dest = user_dir + join_dir
    test_data_path = user_dir + '/'

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

    #os.system('rm ' + dest + '/*')


def generate(images, cx, w, h, y, pdf_name):
    c = canvas.Canvas(pdf_name)
    # move the origin up and to the left
    c.translate(inch, inch)
    c.setFillColorRGB(1, 0, 1)
    for chunks in images:
        x = cx
        for each in chunks:
           # print(each, x, y)
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


