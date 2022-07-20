#/usr/env/python3
from fastapi import FastAPI, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Union

from task import get_pdf_id
from db import PDFVision

import uuid

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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

    with open(uuid_slide+".pdf", "wb") as f:
        f.write(file)
    
    get_pdf_id.delay(owner_email, slides_name, uuid_slide)
    
    return {'id_task': uuid_slide}

@app.get("/files/{task_id}")
def check_task(task_id: str):
    result = PDFVision.find_one({'slidesID': task_id})
    if result is None:
        raise HTTPException(status_code=404, detail="Task does not exist or still processing")
    return {'result': result['urls']}