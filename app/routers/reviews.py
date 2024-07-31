from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update

from app.backend.db_depends import get_db
from app.models import Product, Review, Rating
from app.routers.auth import get_current_user
from app.schemas import CreateReview, CreateRating


router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    ratings = await db.scalars(select(Rating).where(Rating.is_active == True))
    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There are not review')
    return {'Reviews': reviews.all(), 'Ratings': ratings.all()}


@router.get('/{product_id}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    reviews = await db.scalars(select(Review).where(Review.product_id == product_id))
    ratings = await db.scalars(select(Rating).where(Rating.product_id == product_id))
    return {'Reviews': reviews.all(), 'Ratings': ratings.all()}


@router.post('/create/{product_id}')
async def add_review(db: Annotated[AsyncSession, Depends(get_db)], product_id: int, create_review: CreateReview, create_rating: CreateRating, get_user: Annotated[dict, Depends(get_current_user)]):
    product = await db.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no product found')
    if get_user.get('is_customer'):
        await db.execute(
            insert(Rating).values(grade=create_rating.grade, user_id=get_user.get('id'), product_id=product.id))
        await db.commit()
        rating = await db.scalar(select(Rating).where(Rating.product_id == product.id))
        await db.execute(insert(Review).values(user_id=get_user.get('id'), product_id=product.id, rating_id=rating.id, comment=create_review.comment, comment_date=datetime.now()))
        if create_review:
            ratings = await db.scalars(select(Rating).where(product_id == product.id))
            ratings_list = list(i.grade for i in ratings.all())
            average_value = sum(ratings_list) / len(ratings_list)
            await db.execute(update(Product).where(Product.id == product.id).values(rating=average_value))
        await db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )
@router.delete('/delete')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product = await db.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no Review found'
        )
    if get_user.get('is_admin'):
        await db.execute(update(Rating).where(Product.id == product.id).values(is_active=False))
        await db.execute(update(Review).where(Product.id == product.id).values(is_active=False))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Review delete is successful'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

