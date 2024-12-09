"""Flask app to summarize a website using OpenAI's GPT-3 model."""

import logging
import os
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from openai import Client

app = Flask(__name__)


# Replace with your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")


def summarize_website(url):
    """Fetches website content and generates a summary using GPT."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = BeautifulSoup(response.content, "html.parser").get_text()
        gpt_client = Client(api_key=OPENAI_API_KEY)
        gpt_response = gpt_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this website content: {content[:4000]}",
                }
            ],
        )
        if not gpt_response.choices:
            logging.error("Error no choices in response: %s", gpt_response)
            return "Error fetching or summarizing website"
        first_choice = gpt_response.choices[0]

        if not first_choice.message:
            logging.error("Error no message in response: %s", gpt_response)
            return "Error fetching or summarizing website"
        message = first_choice.message

        if not message.content:
            logging.error("Error no content in message: %s", message)
            return "Error fetching or summarizing website"

        content = message.content
        logging.debug("Content: %s", content)

        return content

    except Exception as error:  # pylint: disable=broad-except
        logging.error("Error fetching or summarizing website: %s", error)
        return f"Error fetching or summarizing website: {error}"


def extract_links(url):
    """Fetches website content and extracts all links."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        links = [
            "http://localhost:5000/?url=" + a["href"]
            for a in soup.find_all("a", href=True)
        ]
        return links
    except Exception as e:
        return [f"Error fetching links: {e}"]


@app.route("/")
def index():
    """Main route to render the website."""
    url = request.args.get("url")
    if url:
        summary = summarize_website(url)
        links = extract_links(url)
        return render_template("index.html", url=url, summary=summary, links=links)
    return render_template("index.html", url=None, summary=None, links=None)


if __name__ == "__main__":
    app.run(debug=True)
