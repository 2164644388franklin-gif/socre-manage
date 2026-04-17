from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from fastapi import HTTPException

app = FastAPI()


list_user=[
    {"user_id":1,"username":"Mary","score":99},
    {"user_id":2,"username":"Lisa","score":96},
    {"user_id":3,"username":"Mask","score":95},
    {"user_id":4,"username":"Altman","score":95},
    {"user_id":5,"username":"Dario","score":95},
]

class Item(BaseModel):
    user_id:int
    username: str
    score: int


@app.get("/user/{user_id}",response_model=Item)
def get_user(user_id:int):
    for user in list_user:
        if user["user_id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="用户不存在")



@app.get("/users",response_model=list[Item])
def get_users(page: int = 1, page_size: int = 10):
    
    filtered_users = list_user
 
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_users = filtered_users[start_index:end_index]
    return  paginated_users

@app.post("/register",response_model=Item)
def usr_register(user:Item):
    new_user_id = max([u["user_id"] for u in list_user]) + 1
    new_user = {
        "user_id":new_user_id,
        "username": user.username,
        "score": user.score
    }
    list_user.append(new_user)
    # 返回新用户信息
    return new_user


@app.delete("/user/{user_id}")
def delete_user(user_id: int):
     for index, existing_user in enumerate(list_user):
        if existing_user["user_id"] == user_id:
            del list_user[index]
            return {"message": "用户删除成功"}
        
     return {"detail":"用户信息不存在"}


class UpdateUser(BaseModel):
    score: int

@app.put("/user/{user_id}", response_model=Item)
def update_user(user_id: int, user: UpdateUser):
    
    for index, existing_user in enumerate(list_user):
        if existing_user["user_id"] == user_id:
            
            updated_user = existing_user.copy()
        
            updated_user["score"] = user.score

            existing_user["score"]=updated_user["score"]


            return updated_user
   
    raise HTTPException(status_code=404, detail="用户不存在")

