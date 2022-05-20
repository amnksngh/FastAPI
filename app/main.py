from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from requests import Response

app = FastAPI()

class Post(BaseModel):
    title: str 
    content: str 
    published: bool = True 
    rating: Optional[int] = None  

while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database= 'fastapi',
        user='postgres', password='password123', cursor_factory= RealDictCursor)
        cursor = conn.cursor()
        print('Database Connection was successful!')
        break
    except Exception as error:
        print('Connecting to database failed')
        print(error)
        time.sleep(2)

my_posts = [{"title": "post 1", "content": "content of post 1", "id": 1},
            {"title": "post 2", "content": "content of post 2", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
def root():
    return {"message": "Welcome to my API!"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) 
    VALUES (%s, %s, %s) RETURNING *""", 
    (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'post with id: {id} does not exist')
    return {"data": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s
    RETURNING *""", (str(id),))
    delete_post = cursor.fetchone()
    if delete_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'post with id: {id} does not exist')
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s
            WHERE id = %s Returning *""", 
                    (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'post with id: {id} does not exist')
    conn.commit()
    return {"data": updated_post}