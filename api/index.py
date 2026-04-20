from mangum import Mangum

from app.index import app

# app in app.index already includes CORS middleware and all API routes.
handler = Mangum(app, lifespan="off")
