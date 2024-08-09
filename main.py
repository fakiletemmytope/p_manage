from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routes import admin, user, project
from utils.auth import authenticate_token

app = FastAPI()
app.include_router(admin.admin_router)
app.include_router(user.user_router)
app.include_router(project.project_router)



#middleware
@app.middleware("http")
async def authenticateUser(request: Request, call_next):
    urlpath = request.url.path
    verb = request.method
    print(verb, urlpath)
    if urlpath == "/user/login" or urlpath == "/docs" or urlpath=="/":
        response = await call_next(request)
        return response
    elif urlpath == "/user/" and verb == "POST":
        response = await call_next(request)
        return response
    else:
        if request.headers.get("authorization"):
            decode = await authenticate_token(request.headers.get("authorization").split(" ")[1])
            #print(decode)
            if  decode is None:
                return JSONResponse(content={"detail":"Expired Token"}) 
            else:   
                print(decode)
                current_username = decode["current_user_name"]   
                current_userId = decode["current_user_id"]  
                if decode["current_user_is_admin"]:
                    current_userRole = 'admin'
                else:
                    current_userRole = 'not_admin'
                request.state.custom_data = {"current_username": current_username,
                                             "current_userId": current_userId,
                                             "current_userRole": current_userRole
                                             } 
                response = await call_next(request)
                return response
        else:
            return JSONResponse(content={"detail":"Token required"}, status_code=422)

@app.get("/")
def root():
    return {"message":"welcome to the Project Management hub"}

