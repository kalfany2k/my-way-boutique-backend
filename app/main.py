from fastapi import FastAPI
from app.api import auth, carts, product, user, reset_products, reviews, sets
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://mwb.local"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(carts.router)
app.include_router(reset_products.router)
app.include_router(reviews.router)
app.include_router(sets.router)