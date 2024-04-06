from fastapi import FastAPI
from app.routes import link_route,auth_user, click_route
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
app.include_router(link_route.router)
app.include_router(click_route.router)
