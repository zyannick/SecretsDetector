from fastapi import FastAPI, UploadFile, File
from typing import List
import shutil
import os
from modules.scanner import scan_file 

app = FastAPI()

@app.post("/scan-file/")
async def create_upload_file(file: UploadFile = File(...)):
    temp_dir = "temp_uploads"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        findings = scan_file(temp_file_path)
        
        return {"filename": file.filename, "findings": findings}
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Secret Scanner API. Use the /docs endpoint to see the API documentation."}