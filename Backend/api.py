from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from    dotenv import load_dotenv
import os
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Recipes API", description="API for managing recipes")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv('FRONTEND_URL', 'http://localhost:3000'),
        'http://127.0.0.1:3000'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Redirect to the API documentation."""
    return RedirectResponse(url="/docs")

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

@app.get("/api/recipes")
def get_recipes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort: str = Query("desc", regex="^(asc|desc)$")
):
    offset = (page - 1) * limit
    sort_order = "DESC" if sort == "desc" else "ASC"
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as total FROM recipes")
            total = cur.fetchone()['total']
        
            cur.execute(f"""
                SELECT * FROM recipes 
                ORDER BY rating {sort_order}
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            recipes = cur.fetchall()
        
            for recipe in recipes:
                for key, value in recipe.items():
                    if hasattr(value, 'isoformat'):
                        recipe[key] = value.isoformat()
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "data": recipes
            }

@app.get("/api/recipes/search")
def search_recipes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    calories_min: Optional[float] = None,
    calories_max: Optional[float] = None,
    cuisine: Optional[str] = None,
    title: Optional[str] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    total_time_min: Optional[int] = None,
    total_time_max: Optional[int] = None
):
    offset = (page - 1) * limit
    conditions = []
    params = []
    
    if calories_min is not None:
        conditions.append("CAST(nutrients->>'calories' AS FLOAT) >= %s")
        params.append(calories_min)
    if calories_max is not None:
        conditions.append("CAST(nutrients->>'calories' AS FLOAT) <= %s")    
        params.append(calories_max)
    if cuisine:
        conditions.append("cuisine = %s")
        params.append(cuisine)
    if title:
        conditions.append("title ILIKE %s")
        params.append(f"%{title}%")
    if rating_min is not None:
        conditions.append("rating >= %s")
        params.append(rating_min)
    if rating_max is not None:
        conditions.append("rating <= %s")
        params.append(rating_max)
    if total_time_min is not None:
        conditions.append("total_time >= %s")
        params.append(total_time_min)
    if total_time_max is not None:
        conditions.append("total_time <= %s")
        params.append(total_time_max)
    
    where_clause = " AND ".join(conditions) if conditions else "TRUE"

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # use tuples for psycopg2 parameter substitution
                params_tuple = tuple(params)
                cur.execute(f"SELECT COUNT(*) as total FROM recipes WHERE {where_clause}", params_tuple)
                total = cur.fetchone()['total']

                query = f"""
                    SELECT * FROM recipes 
                    WHERE {where_clause}
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, params_tuple + (limit, offset))
                recipes = cur.fetchall()

                for recipe in recipes:
                    for key, value in recipe.items():
                        if hasattr(value, 'isoformat'):
                            recipe[key] = value.isoformat()

                return {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "data": recipes
                }
    except Exception as e:
        # return clearer error to client and ensure it's visible in logs
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 

