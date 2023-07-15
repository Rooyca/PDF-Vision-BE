from fileinput import filename
from celery import Celery
import uuid, os, shutil, fitz, time, boto3, random

from fastapi import HTTPException
from db import PDFVision

celery = Celery(__name__)

celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")


s3 = boto3.resource('s3', endpoint_url=os.environ['S3_ENDPOINT'],
                       aws_access_key_id=os.environ['KEY_ID'], aws_secret_access_key=os.environ['KEY_SECRET'])

bucket = s3.Bucket('tmpimg')

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

        file_path = f"files/img/{newDir}/{page.number}.png"
        sub = random.randrange(0,9999) 
        object_key = f'{slides_id}_{sub}.png'

        bucket.upload_file(file_path, object_key)

        all_urls.append({'url': os.environ.get("URL_STORAGE")+object_key})

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
    del_doc = PDFVision.delete_one({'slidesID': slides_id})
    return {'status':'ok'}
