
## Info

    stack: Django, Postgresql
    auth: JWT, session for admin and docs
    

## Setup & Run
    
    cp example.env .env

Fill example.env with your data
    
    docker compose up --build -d

## Fulfillment

All requirements are complete, except for Celery and tests.

## Docs

    GET: http://127.0.0.1:8000/api/docs/
