from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import Token, UserCreate, UserLogin
from app.services.auth_service import login, register

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user.
    """
    try:
        user = register(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            company=user_data.company
        )
        return {"email": user.email, "message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login_for_access_token(user_data: UserLogin):
    """
    Login and get an access token for future requests.
    """
    access_token = login(email=user_data.email, password=user_data.password)
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login using form data, get an access token for future requests.
    This endpoint is compatible with OAuth2 clients.
    """
    # The OAuth2 form uses "username" field, but our system uses "email"
    access_token = login(email=form_data.username, password=form_data.password)
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": access_token, "token_type": "bearer"}