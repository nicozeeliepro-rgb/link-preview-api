from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Link Preview API is running! Append /preview?url=... to the URL."}


@app.get("/preview")
def get_preview(url: str):
    try:
        # 1. Fetch the website content
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        # 2. Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. Extract Metadata (Title, Description, Image)
        # We look for <meta property="og:title"> etc.
        data = {
            "title": soup.find("meta", property="og:title") or soup.find("title"),
            "description": soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"}),
            "image": soup.find("meta", property="og:image"),
            "url": url
        }

        # Clean up the data (extract the 'content' attribute)
        return {
            "title": data["title"].get_text() if hasattr(data["title"], 'get_text') else data["title"].get("content", "No title found") if data["title"] else "N/A",
            "description": data["description"].get("content", "No description found") if data["description"] else "N/A",
            "image": data["image"].get("content", "") if data["image"] else ""
        }

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not process URL: {str(e)}")
