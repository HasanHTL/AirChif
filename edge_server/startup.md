AirCHIF - Edge Server (quickstart)

1) Virtual Environment
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2) Start Postgres (Docker)
   docker-compose up -d db

   oder lokal:
   docker run --name airchif-db -e POSTGRES_USER=airchif -e POSTGRES_PASSWORD=password -e POSTGRES_DB=airchif -p 5432:5432 -d postgres:15

3) Set env (optional) in .env:
   DATABASE_URL=postgresql+psycopg2://airchif:password@localhost:5432/airchif
   JWT_SECRET_KEY=verysecret
   JWT_REFRESH_SECRET_KEY=verysecretrefresh
   CORS_ORIGINS=http://localhost,http://localhost:5173

4) Initialize DB (main will auto-create tables on startup)
   python -m edge_server.main

5) API docs:
   http://localhost:8000/docs

Typical flow (curl):
- Signup:
  curl -X POST "http://localhost:8000/api/v1/auth/signup" -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"pw"}'

- Login:
  curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"pw"}'

- Create Journey:
  curl -X POST "http://localhost:8000/api/v1/journeys/" -H "Authorization: Bearer <ACCESS_TOKEN>" -H "Content-Type: application/json" -d '{"name":"Test","description":"x","points":[{"sequence":0,"lat":48.2,"lon":16.37},{"sequence":1,"lat":48.201,"lon":16.371}]}'
