from fastapi import FastAPI

app = FastAPI(title="Lapped AI")

@app.get("/")
def root():
    return {"message": "Lapped is running"}