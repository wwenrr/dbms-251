import logging
import os
import typer
from service.dataset_service import DatasetService
from service.ima_service import ImaService
from service.mri_service import MriService
from service.redis_service import RedisService

app = typer.Typer()

# ========== COMMANDS ==========

@app.command()
def clean():
    RedisService.clean()
    typer.echo("Redis database cleaned.")

@app.command()
def insert():
    if not os.path.exists("data"):
        typer.echo("Error: 'data' folder not found. Please install data first.", err=True)
        raise typer.Exit(code=1)
    if not os.path.exists("data/metadata"):
        typer.echo("Error: 'data/metadata' folder not found. Please parse data first.", err=True)
        raise typer.Exit(code=2)
    
    MriService.process_mri_data()
    typer.echo("All checks passed. Proceeding with insert...")

@app.command()
def parse():
    ImaService.parse_all()

@app.command()
def download():
    typer.echo("------------------ Downloading datasets ------------------")
    DatasetService.download_text_data()
    DatasetService.download_image_data()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    RedisService.configure()
    app()
