from fastapi import FastAPI


app = FastAPI()


<<<<<<< HEAD
@app.get("/")
def health_check():
    return {"status": "ok"}

=======
@app.get("/health-check")
def health_check():
    return {"status": "ok"}
>>>>>>> 7460434a6a0601a56eac8a201d9257c754c49816
