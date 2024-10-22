from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.routers.auth import get_current_user
from app.schemas import CreateProduct

router = APIRouter(prefix='/products', tags=['products'])

@router.get('/')
async def all_product(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.is_active == True and Product.stock > 0))
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no product')
    return products.all()

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        await db.execute(insert(Product).values(name=create_product.name, description=create_product.description, slug=slugify(create_product.name), price=create_product.price, image_url=create_product.image_url, stock=create_product.stock, category_id=create_product.category, rating=0.0, supplier_id=get_user.get('id')))
        await db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
    else:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to use this method")

@router.get('/{category_slug}')
async def products_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(category_slug == Category.slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    subcategory = await db.scalars(select(Category).where(Category.parent_id == category.id))
    all_categories = [category.id] + [i.id for i in subcategory.all()]
    products = await db.scalars(select(Product).where(Product.category_id.in_(all_categories), Product.is_active == True, Product.stock > 0))
    return products.all()

@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(product_slug == Product.slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no product')
    return product

@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, update_product: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    product = await db.scalar(select(Category).where(product_slug == Product.slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no product found')
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        if get_user.get('id') == product.suppier_id or get_user.get('is_admin'):
            await db.execute(update(Product).where(product_slug == Product.slug).values(name=update_product.name, description=update_product.description, slug=slugify(update_product.name), price=update_product.price, image_url=update_product.image_url, stock=update_product.stock, category_id=update_product.category, rating=0.0))
            await db.commit()
            return {'status_code': status.HTTP_200_OK, 'transaction': 'Product update is successful'}
        else:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )


@router.delete('/delete')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product_delete = await db.scalar(select(Product).where(Product.id == product_id))
    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_delete.supplier_id or get_user.get('is_admin'):
            await db.execute(update(Product).where(Product.id == product_id).values(is_active=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )














