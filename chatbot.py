import os
from groq import Groq
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("gr_api_key"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)


class UserMessage(BaseModel):
    msg : str

@app.api_route("/ping", methods=["GET", "HEAD"])
async def ping():
    await asyncio.sleep(0.1)
    return {"message": "server is running"}



@app.post("/chat")
async def chat_with_doctor(ui: UserMessage):

    chat_hist= [{"role": "system", "content": """You are the Aaranya Jharkhand Virtual Travel Assistant.

Scope: Only Jharkhand → destinations, culture, heritage, trip planning, travel tips, artisan marketplace.

Tone: Warm, friendly, clear, engaging.

Functions:

Suggest itineraries (group size, duration, interests, budget).

Highlight tribal traditions, festivals, handicrafts, local cuisine.

Share info on transport, best time to visit, stays, safety, sustainability.

Limits: Do not give info outside Jharkhand. Redirect politely if asked."""}]

    ui = ui.msg
    chat_hist.append({"role": "user", "content": ui})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_hist,
            temperature=0.2,
            max_tokens=512,
        )
        res = completion.choices[0].message.content
        chat_hist.append({"role": "assistant", "content": res})
        return {"response":res}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
