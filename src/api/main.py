from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.process import router as process_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="NCB KYC Document Processing API", 
        version="2.0.0",
        description="API for extracting information from NCB Bank KYC forms using custom Document AI extractor"
    )

    # CORS for Vite dev server and local use
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(process_router, prefix="/api/v1/documents", tags=["documents"])
    return app


app = create_app()


def main():  # pragma: no cover
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == "__main__":
    main()