from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db, MovieModel
from src.schemas import MovieListResponseSchema, MovieDetailResponseSchema


router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=20), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).offset((page - 1) * per_page).limit(per_page))
    movies = result.scalars().all()
    count_query = select(func.count()).select_from(MovieModel)
    total_items = (await db.execute(count_query)).scalar_one()
    total_pages = (total_items + per_page - 1) // per_page
    if page == 1:
        prev_page = None
    else:
        prev_page = f"/theater/movies/?page={page-1}&per_page={per_page}"
    if page >= total_pages:
        next_page = None
    else:
        next_page = f"/theater/movies/?page={page+1}&per_page={per_page}"
    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")
    return {"movies": movies,
            "prev_page": prev_page,
            "next_page": next_page,
            "total_pages": total_pages,
            "total_items": total_items
    }


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_detail(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="No movie found.")
    return movie
