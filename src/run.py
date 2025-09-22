import logging
import typer
from service.dataset_service import DatasetService
from service.redis_service import RedisService

app = typer.Typer()

@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")

@app.command()
def download():
    typer.echo("Downloading datasets...")
    DatasetService.download_text_data()
    DatasetService.download_image_data()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    RedisService.configure()
    app()
