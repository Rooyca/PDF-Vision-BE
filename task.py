from fileinput import filename
from celery import Celery
import time
import uuid, os, glob, shutil, fitz, cloudinary
import cloudinary.uploader

from fastapi import HTTPException

from db import PDFVision

from dotenv import load_dotenv
load_dotenv()

celery = Celery(__name__)
REDIS = 'redis://:'+os.environ.get('REDIS_PASS')+'@'+os.environ.get('REDIS_PUBLIC')+'/0'
celery.conf.broker_url = REDIS

config = cloudinary.config(secure=True)
config.cloud_name = os.environ.get('CLOUD_NAME')
config.api_key = os.environ.get('API_KEY')
config.api_secret = os.environ.get('API_SECRET')

@celery.task(name='get_pdf_id',  max_retries=3, ignore_result=True)
def get_pdf_id(owner_email: str, slides_name: str, slides_id: str):
    all_urls = []
    filename = slides_id+'.pdf'

    def remove_pdf():
        pattern = f"{os.getcwd()}/*.pdf"
        files = glob.glob(pattern)

        for fl in files:
            try:
                os.remove(fl)
            except:
                pass

    try:
        doc = fitz.open(filename)
    except:
        raise HTTPException(status_code=400, detail="Oops, please check your file and try again")

    newDir = filename.split('.')[0]+'-'+str(uuid.uuid1())[:5]
    os.mkdir(f"{os.getcwd()}/imgs/{newDir}")

    for page in doc:  
        pix = page.get_pixmap()  
        pix.save(f"{os.getcwd()}/imgs/{newDir}/{page.number}.png" )
        cloudUpload = cloudinary.uploader.upload(
                                                    f"{os.getcwd()}/imgs/{newDir}/{page.number}.png", 
                                                    public_id=f"{page.number}",
                                                    folder=f"pdfvision/{newDir}", 
                                                    unique_filename=False, 
                                                    overwrite=True
                                                )
        all_urls.append(cloudUpload['secure_url'])

    shutil.rmtree(f"{os.getcwd()}/imgs/{newDir}")
    remove_pdf()

    data = {
            "ownerEmail": owner_email,
            "slidesName": slides_name,
            "slidesID": slides_id,
            "slidesPages": len(all_urls),
            "pdfPages": doc.page_count,
            "pdfMeta": doc.metadata,
            "dateUp": time.ctime(),
            "urls": all_urls
            }

    PDFVision.insert_one(data)

    return {
            "id": slides_id,
            'urls': all_urls
            }