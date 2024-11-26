import logging.config
import os
import typer
import time
import uvicorn

from app.settings import settings

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('info')

app = typer.Typer()


@app.command('runserver')
def _run():
    print("Run at http://%s:%s" % (settings.API_HOST, settings.API_PORT))
    workers_count = int(os.getenv("UVICORN_WORKERS_COUNT", "4"))
    uvicorn.run(
        app='app.main:app',
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD,
        log_config=settings.LOGGING,
        workers=workers_count,
    )


@app.command()
def default():
    pass


if __name__ == '__main__':
    app()
