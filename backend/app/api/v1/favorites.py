from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.question import Question
from app.models.record import UserFavorite
from app.schemas.record import FavoriteRequest, FavoriteResponse
from app.schemas.question import QuestionResponse
from app.schemas.common import ResponseModel, PageResponse

router = APIRouter()

@router.post("", response_model=ResponseModel[FavoriteResponse], status_code=status.HTTP_201_CREATED)
def add_favorite(
    data: FavoriteRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """添加题目到收藏夹"""
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    fav = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.question_id == data.question_id
    ).first()

    if fav:
        return ResponseModel(code=200, message="已在收藏夹中", data=FavoriteResponse(
            id=fav.id, question_id=fav.question_id, created_at=fav.created_at, question=QuestionResponse.model_validate(question)
        ))

    fav = UserFavorite(user_id=current_user.id, question_id=data.question_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)

    return ResponseModel(
        code=201, 
        message="收藏成功", 
        data=FavoriteResponse(
            id=fav.id, 
            question_id=fav.question_id, 
            created_at=fav.created_at, 
            question=QuestionResponse.model_validate(question)
        )
    )

@router.delete("/{question_id}", response_model=ResponseModel[dict])
def remove_favorite(
    question_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """取消收藏题目"""
    fav = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.question_id == question_id
    ).first()

    if not fav:
        raise HTTPException(status_code=404, detail="未收藏该题目")

    db.delete(fav)
    db.commit()

    return ResponseModel(code=200, message="取消收藏成功", data={"question_id": question_id})

@router.get("", response_model=ResponseModel[PageResponse[FavoriteResponse]])
def list_favorites(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户收藏题目列表 (标准分页)"""
    query = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id)
    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    favs = query.order_by(UserFavorite.id.desc()).offset((page - 1) * size).limit(size).all()
    
    items = []
    for f in favs:
        q = db.query(Question).filter(Question.id == f.question_id).first()
        q_res = QuestionResponse.model_validate(q) if q else None
        items.append(FavoriteResponse(id=f.id, question_id=f.question_id, created_at=f.created_at, question=q_res))

    return ResponseModel(
        code=200,
        data=PageResponse(
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            items=items
        )
    )
