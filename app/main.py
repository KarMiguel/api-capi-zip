from fastapi import FastAPI
from app.schemas.schemas import Auth
from app.routes import route_link,auth_user, click_route
from datetime import datetime


app = FastAPI()


@app.post("/")
def health_check(user: Auth):
    user.created_at = datetime.utcnow()
    return user

app.include_router(auth_user.router)
app.include_router(route_link.router)
app.include_router(click_route.router)
