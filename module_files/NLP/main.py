from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pydantic import BaseModel
import json


app = FastAPI()

#model_name = "microsoft/DialoGPT-large"
#model_name=  "microsoft/DialoGPT-medium"
model_name = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model_NPL = AutoModelForCausalLM.from_pretrained(model_name)

#temporary dict to store the chat_ids
dict = {0: ''}

# Keep is separated it is a good candidate to have it moved to a docker container

class ChatText(BaseModel):
    text : str
    chat_history_id : int


@app.post('/chat' )
def casual_chat(chattext : ChatText):#, chat_history_ids =None):

    text = chattext.text
    id = chattext.chat_history_id
     
    chat_history_ids = dict.get(id)
    # encode the input and add end of string token
    input_ids = tokenizer.encode(text + tokenizer.eos_token, return_tensors="pt")
    
    # concatenate new user input with chat history (if there is one)
    if chat_history_ids != None:
        bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1)
    else:
        bot_input_ids = input_ids
    
    # generate a bot response
    chat_history_ids = model_NPL.generate(
        bot_input_ids,
        #num_beams = 3, #number of words used
        max_length=1000,
        do_sample=True,
        top_p=0.95,
        top_k=50,
        temperature=0.75,
        num_return_sequences = 1,
        pad_token_id=tokenizer.eos_token_id
    )
    
    dict[id] = chat_history_ids
    #print the output
    output = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    #print(dict)
    #print(output, dict[id])
    
    return json.dumps({'output':  output, 'id': id})
