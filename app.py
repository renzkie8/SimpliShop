from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# This single line tells Azure to serve all your HTML, CSS, and JS files
# It will automatically find 'index.html' and make it your homepage!
app.mount("/", StaticFiles(directory=".", html=True), name="static")
