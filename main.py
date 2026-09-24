from fastapi import FastAPI

app = FastAPI()

users = {}

@app.get("/users")
def get_all_users():
    return users;

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id in users:
        return users[user_id]
    else:
        return {"error": "User not found"}

@app.post("/users")
def create_user( name: str, email: str):
    
    user_id = len(users) + 1;

    if user_id in users:
        return {"error": "User already exists"}
    else:
        users[user_id] = {"name": name, "email": email}
        return {"message": "User created successfully"}    

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = None, email: str = None):
    if user_id in users:
        users[user_id] = {"name": name, "email": email}
        return {"message": "User updated successfully"}
    else:
        return {"error": "User not found"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id in users:
        del users[user_id]
        return {"message": "User deleted successfully"}
    else:
        return {"error": "User not found"}