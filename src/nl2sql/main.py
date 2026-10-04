from fastapi import FastAPI, HTTPException
from nl2sql.sqlgen import InputError, generate

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/generate")
def post_generate(body: dict):
    try:
        return generate(body.get("question"))
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
