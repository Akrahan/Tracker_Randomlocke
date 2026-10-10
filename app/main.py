from fastapi import FastAPI

app = FastAPI(title="Tracker Randomlocke")


@app.get("/")
def raiz():
    return {"mensaje": "Tracker Randomlocke funcionando"}
