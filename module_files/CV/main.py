from fastapi import FastAPI, UploadFile
import torch
from pydantic import BaseModel
import json
import pandas as pd
from PIL import Image
import numpy as np

app = FastAPI()

#Classes
df = pd.read_csv('/app/classes_words.csv', index_col = 'Word')
cl = dict(zip(df.index, df['Class']))

# Model
model_cv = torch.hub.load('/app/yolov5/', 'custom', path='/app/yolov5/weights_ASR/weights_s_640.pt', source='local', device='cpu', force_reload=True)



#temporary dict to store the chat_ids
dict = {}

def classify(img):
    results = model_cv(img)
    
    return results

@app.post('/predict' )
async def create_upload_file(file: UploadFile):

    image = Image.open(file.file)
    
    results = classify(image)
    
    df = results.pandas().xyxy[0]  # img predictions (pandas)
    parsed = df.to_json(orient="split")

    print(df)

    return json.dumps({'dataframe':parsed})
