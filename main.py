from fastapi import FastAPI, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import uuid, string, random

from tasks import get_pdf_id, del_pdf_by_id
from db import PDFVision

app = FastAPI()

# EDIT THIS FOR ALLOW ORIGINS WITH REGEX

app.add_middleware(CORSMiddleware, #allow_origin_regex=["https:.*\.vercel\.app"],
                                   allow_origins=["*"],
                                   allow_methods=["*"], 
                                   allow_headers=["*"])

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

@app.post("/files/")
def create_file(file: Union[bytes, None] = File(default=None), 
                        owner_email: str = Form(min_length=6, max_length=50, regex=regex),
                        slides_name: str = Form(min_length=3, max_length=50)):
    if file is None:
        raise HTTPException(status_code=400, detail="No file sent")

    if len(file) > 5e+6:
        raise HTTPException(status_code=413, detail="File too large")
    
    uuid_slide = str(uuid.uuid1())
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=5))
    del_key = random_string+uuid_slide[:2]

    with open('files/pdf/'+uuid_slide+".pdf", "wb") as f:
        f.write(file)
    
    get_pdf_id.delay(owner_email, slides_name, uuid_slide, del_key)
    
    return {'id_task': uuid_slide, 'SAVE_THIS_delete_key': del_key}

@app.get("/files/{task_id}")
def check_task(task_id: str):
    result = PDFVision.find_one({'slidesID': task_id})
    if result is None:
        raise HTTPException(status_code=404, detail="Task does not exist or still processing")
    urls_user = []
    for url in result['urls']:
        urls_user.append(url['url'])
    return {'result': urls_user}

@app.delete("/files/{task_id}")
def check_task(task_id: str, dk: str):
    result = PDFVision.find_one({'slidesID': task_id})
    if result is None:
        raise HTTPException(status_code=404, detail="Task does not exist")

    if dk != result['deleteKey']:
        raise HTTPException(status_code=403, detail="The verification code seems to be incorrect")

    del_pdf_by_id.delay(task_id)

    return {'result': 'Slide deleted'}