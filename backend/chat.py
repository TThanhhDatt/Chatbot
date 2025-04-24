import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import PyPDF2
import pdfplumber
import serpapi
import requests
from bs4 import BeautifulSoup
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = "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"
SERPAPI_API_KEY = "9ad62df181fdb716f080eb7f70e2fe1473dff2a92ce2afb67264df9b44385fe5"
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

pdf_content_store = {}

@app.get("/")
async def root():
    return {"message": "Backend is running"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket connection attempted")
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            try:
                user_message = json.loads(data).get("message", "")
                session_id = json.loads(data).get("session_id", "default")
            except json.JSONDecodeError as e:
                print(f"JSON error: {e}")
                await websocket.send_text(json.dumps({"response": "Invalid message format"}))
                continue

            if user_message.startswith("search_pdf:"):
                query = user_message.replace("search_pdf:", "").strip()
                pdf_content = pdf_content_store.get(session_id, "")
                if not pdf_content:
                    await websocket.send_text(json.dumps({"response": "No PDF uploaded for this session."}))
                    continue
                search_results = []
                for page_num, text in enumerate(pdf_content.split("\n\n")):
                    if query.lower() in text.lower():
                        search_results.append(f"Page {page_num + 1}: {text[:200]}...")
                if search_results:
                    await websocket.send_text(json.dumps({"response": "\n".join(search_results)}))
                else:
                    await websocket.send_text(json.dumps({"response": "No matches found in PDF."}))
                continue

            if user_message.startswith("search_web:"):
                query = user_message.replace("search_web:", "").strip()
                search_results = search_web(query)
                if search_results:
                    response = "Found articles:\n" + "\n".join(
                        [f"- {result['title']} ({result['link']})\n  Summary: {result['summary']}" for result in search_results]
                    )
                else:
                    response = "No articles found."
                await websocket.send_text(json.dumps({"response": response}))
                continue

            try:
                response = await client.chat.completions.create(
                    model="google/gemini-2.0-flash-exp:free",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Provide concise and accurate responses."},
                        {"role": "user", "content": user_message}
                    ],
                    stream=True,
                    max_tokens=2000
                )
                if hasattr(response, '__aiter__'):
                    async for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            print(f"Sending chunk: {chunk.choices[0].delta.content}")
                            await websocket.send_text(json.dumps({"response": chunk.choices[0].delta.content}))
                else:
                    content = response.choices[0].message.content
                    print(f"Sending response: {content}")
                    await websocket.send_text(json.dumps({"response": content}))
            except Exception as e:
                print(f"Open Router error: {e}")
                await websocket.send_text(json.dumps({"response": f"Open Router error: {str(e)}"}))
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"response": f"Error: {str(e)}"}))
    finally:
        await websocket.close()

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = "default"):
    try:
        print(f"Uploading PDF for session: {session_id}")
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
        pdf_content_store[session_id] = text
        print("PDF uploaded successfully")
        return {"status": "PDF uploaded successfully"}
    except Exception as e:
        print(f"Upload error: {e}")
        return {"error": str(e)}

def search_web(query: str):
    try:
        if SERPAPI_API_KEY:
            params = {"q": query, "api_key": SERPAPI_API_KEY, "num": 3}
            response = serpapi.GoogleSearch(params).get_dict()
            results = response.get("organic_results", [])
            return [
                {
                    "title": result["title"],
                    "link": result["link"],
                    "summary": result.get("snippet", "No summary available")
                } for result in results
            ]
        else:
            response = requests.get(f"https://www.google.com/search?q={query}")
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            for g in soup.find_all("div", class_="g")[:3]:
                title = g.find("h3")
                link = g.find("a")
                if title and link:
                    results.append({
                        "title": title.text,
                        "link": link["href"],
                        "summary": "Summary not available (requires SerpAPI for better results)"
                    })
            return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)