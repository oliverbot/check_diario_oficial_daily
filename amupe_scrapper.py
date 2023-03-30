import urllib.request
import yagmail
import PyPDF2
from bs4 import BeautifulSoup
import requests
from PyPDF2 import PdfFileWriter
from pdf2image import convert_from_bytes
import io
import os


SENDER_EMAIL_USERNAME = os.environ.get('SENDER_EMAIL_USERNAME')
SENDER_EMAIL_PASSWORD = os.environ.get('SENDER_EMAIL_PASSWORD')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

TEMP_IMG_NAME = './temp/tempIMG.jpg'
TEMP_PDF_NAME = './temp/tempPDF.pdf'

SEARCH_STRING = os.environ.get('SEARCH_STRING')


def search_pdf_link(pdf_link, search_string):
    # Download the PDF file
    urllib.request.urlretrieve(pdf_link, TEMP_PDF_NAME)

    # Open the PDF file
    with open(TEMP_PDF_NAME, "rb") as f:
        # Read the PDF file using PyPDF2
        pdf_reader = PyPDF2.PdfFileReader(f)

        # Check each page for the search string
        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            text = page.extractText().lower()
            search_string = search_string.lower()
            if search_string in text:
                wrt = PdfFileWriter()
                wrt.addPage(page)
                r = io.BytesIO()
                wrt.write(r)
                images = convert_from_bytes(r.getvalue())
                images[0].save(TEMP_IMG_NAME)
                print("Salvando a imagem...")
                return True

    # If the search string was not found, return False
    return False

def get_current_pdf_link():
    url = 'https://www.diariomunicipal.com.br/amupe/'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    pdf_link = soup.find("figure", id="ultima-edicao").a['href']

    return pdf_link

def send_email(pdf_link):
    if search_pdf_link(pdf_link, SEARCH_STRING):
        print("O arquivo PDF contém a string de busca.")

        print(TEMP_IMG_NAME)

        yag = yagmail.SMTP(SENDER_EMAIL_USERNAME, SENDER_EMAIL_PASSWORD)
        subject = "Notificação: Ralycia foi citada no Diário Oficial."
        contents = 'O nome de Ralycia foi citado no diário oficial. \n Segue em anexo o PDF com a página em que o nome foi citado.'
        yag.send(to=RECEIVER_EMAIL, subject=subject, contents=contents, attachments=TEMP_IMG_NAME)

        print("Email notification sent.")
    else:
        print("O arquivo PDF não contém a string de busca.")

def main():
    
    pdf_link = get_current_pdf_link()
    send_email(pdf_link)
    

    os.remove(TEMP_PDF_NAME)
    os.remove(TEMP_IMG_NAME)

if __name__ == "__main__":
    main()