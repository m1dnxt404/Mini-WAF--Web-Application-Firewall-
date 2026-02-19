from fastapi import FastAPI

app = FastAPI(title="Dummy Backend API")


@app.get("/")
async def root():
    return {"message": "Backend API is running"}


@app.get("/api/data")
async def get_data():
    return {
        "items": [
            {"id": 1, "name": "Item One", "value": 100},
            {"id": 2, "name": "Item Two", "value": 200},
            {"id": 3, "name": "Item Three", "value": 300},
        ]
    }


@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "username": f"user_{user_id}", "email": f"user_{user_id}@example.com"}
