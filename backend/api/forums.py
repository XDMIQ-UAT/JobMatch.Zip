"""
Forum API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.connection import get_db
from database.models import ForumPost

router = APIRouter(prefix="/api/forums", tags=["forums"])


class ForumPostRequest(BaseModel):
    """Request model for forum post."""
    user_id: str
    forum_topic: str
    title: str
    content: str
    parent_post_id: Optional[int] = None


class ForumPostResponse(BaseModel):
    """Response model for forum post."""
    id: int
    user_id: str
    forum_topic: str
    title: str
    content: str
    parent_post_id: Optional[int]
    created_at: str


@router.post("/posts", response_model=ForumPostResponse)
async def create_post(
    request: ForumPostRequest,
    db: Session = Depends(get_db)
):
    """Create a new forum post."""
    post = ForumPost(
        user_id=request.user_id,
        forum_topic=request.forum_topic,
        title=request.title,
        content=request.content,
        parent_post_id=request.parent_post_id
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return ForumPostResponse(
        id=post.id,
        user_id=post.user_id,
        forum_topic=post.forum_topic,
        title=post.title,
        content=post.content,
        parent_post_id=post.parent_post_id,
        created_at=post.created_at.isoformat()
    )


@router.get("/posts/{post_id}", response_model=ForumPostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get forum post by ID."""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return ForumPostResponse(
        id=post.id,
        user_id=post.user_id,
        forum_topic=post.forum_topic,
        title=post.title,
        content=post.content,
        parent_post_id=post.parent_post_id,
        created_at=post.created_at.isoformat()
    )


@router.get("/topics/{topic}/posts", response_model=List[ForumPostResponse])
async def list_topic_posts(
    topic: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List posts in a forum topic."""
    posts = db.query(ForumPost).filter(
        ForumPost.forum_topic == topic,
        ForumPost.parent_post_id == None  # Top-level posts only
    ).order_by(ForumPost.created_at.desc()).limit(limit).all()
    
    return [
        ForumPostResponse(
            id=p.id,
            user_id=p.user_id,
            forum_topic=p.forum_topic,
            title=p.title,
            content=p.content,
            parent_post_id=p.parent_post_id,
            created_at=p.created_at.isoformat()
        )
        for p in posts
    ]


@router.get("/posts/{post_id}/replies", response_model=List[ForumPostResponse])
async def get_replies(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get replies to a post."""
    replies = db.query(ForumPost).filter(
        ForumPost.parent_post_id == post_id
    ).order_by(ForumPost.created_at.asc()).all()
    
    return [
        ForumPostResponse(
            id=r.id,
            user_id=r.user_id,
            forum_topic=r.forum_topic,
            title=r.title,
            content=r.content,
            parent_post_id=r.parent_post_id,
            created_at=r.created_at.isoformat()
        )
        for r in replies
    ]


