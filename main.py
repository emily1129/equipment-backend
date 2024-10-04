import os
   import logging
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from database import engine, Base
   from router import router

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   try:
       Base.metadata.create_all(bind=engine)
       logger.info("Database tables created successfully")
   except Exception as e:
       logger.error(f"Error creating database tables: {e}")
       raise

   app = FastAPI()

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   app.include_router(router, prefix="/api")

   @app.get("/")
   async def root():
       return {"message": "Welcome to the Machine API"}

   if __name__ == "__main__":
       import uvicorn
       port = int(os.environ.get("PORT", 8000))
       uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)