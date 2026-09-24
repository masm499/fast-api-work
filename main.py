from fastapi import FastAPI,HTTPException
from api_request_response_models import UserCreate,UserResponse
app = FastAPI()

users = {}

@app.get("/users",status_code=200)
def get_all_users():
    return users;

@app.get("/users/{user_id}",status_code=200,response_model=UserResponse)
def get_user(user_id: int):
    if user_id in users:
        return users[user_id]
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/users",response_model=UserResponse,status_code=201)
def create_user(user:UserCreate):
    
    user_id = len(users) + 1;

    if user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        users[user_id] = user ;
    
    return user;    

@app.put("/users/{user_id}",status_code=200)
def update_user(user_id: int, user : UserCreate):
    if user_id in users:
        #No more updates to email or password after pydantic validation
        user  = users[user_id] 
        user.name = user.name ;
        users[user_id] = user ;
        return {"message": "User updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}",status_code=200)
def delete_user(user_id: int):
    if user_id in users:
        del users[user_id]
        return {"message": "User deleted successfully"}
    else:
       raise HTTPException(status_code=404, detail="User not found")