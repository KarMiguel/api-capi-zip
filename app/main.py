from fastapi import FastAPI
from app.schemas.schemas import Auth
from app.routes import route_link,auth_user, click_route
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_user.router)
app.include_router(route_link.router)
app.include_router(click_route.router)
