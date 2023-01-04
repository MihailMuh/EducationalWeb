from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get('/')
async def sign(request: Request):
    return get_template("sign_in", request)


@app.get('/diary')
async def sign(request: Request):
    return get_template("main_diary", request)


@app.post("/html")
async def html(request: Request):
    return get_template((await request.json())["html"], request)


def get_template(name: str, request: Request):
    return templates.TemplateResponse(name + ".html", {"request": request})
