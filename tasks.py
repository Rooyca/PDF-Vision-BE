from fileinput import filename
from celery import Celery
import uuid, os, glob, shutil, fitz, time, requests

from fastapi import HTTPException
from db import PDFVision

celery = Celery(__name__)

celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

def remove_pdf(slides_id):
    file = f"files/pdf/{slides_id}.pdf"
    try:
        os.remove(file)
    except:
        pass

@celery.task(name='get_pdf_id',  max_retries=3, ignore_result=False)
def get_pdf_id(owner_email: str, slides_name: str, slides_id: str, delKey: str):
    all_urls = []
    filename = 'files/pdf/'+slides_id+'.pdf'

    try:
        doc = fitz.open(filename)
    except:
        raise HTTPException(status_code=400, detail="Oops, please check your file and try again")

    newDir = slides_id[:5]+'-'+str(uuid.uuid1())[:5]
    os.mkdir(f"files/img/{newDir}")

    for page in doc:  
        pix = page.get_pixmap()  
        pix.save(f"files/img/{newDir}/{page.number}.png") 
        url_base_t = f'https://transfer.sh/{slides_id}.png'
        file_path = f"files/img/{newDir}/{page.number}.png" 

        with open(file_path, 'rb') as f:
            response = requests.put(url_base_t, data=f)

        all_urls.append({'url':response.text.replace('transfer.sh/', 'transfer.sh/get/'), 'url_delete':response.headers['X-Url-Delete']})

    page_count = doc.page_count
    del doc
    shutil.rmtree(f"files/img/{newDir}")
    del filename
    remove_pdf(slides_id)

    data = {
            "ownerEmail": owner_email,
            "slidesName": slides_name,
            "slidesID": slides_id,
            "slidesPages": len(all_urls),
            "pdfPages": page_count,
            "deleteKey": delKey,
            "dateUp": time.ctime(),
            "urls": all_urls
            }

    PDFVision.insert_one(data)

    return {"data": data}


@celery.task(name='del_pdf_by_id',  max_retries=3, ignore_result=True)
def del_pdf_by_id(slides_id: str):
    slide = PDFVision.find_one({'slidesID': slides_id})
    for url in slide['urls']:
        requests.delete(url['url_delete'])
    del_doc = PDFVision.delete_one({'slidesID': slides_id})
    return {'status':'ok'}
