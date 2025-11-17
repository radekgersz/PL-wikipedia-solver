from huggingface_hub import hf_hub_download
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import os

def downloadDatabase(repoID, accessToken, filename):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
    dataset_dir = os.path.join(PROJECT_ROOT, "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    dataset_path = hf_hub_download(
        repo_id=repoID,
        repo_type="dataset",
        token=accessToken,
        filename=filename,
        local_dir=dataset_dir,
        dry_run=False
    )

    return dataset_path
def createSQLiteEngine(databasePath):
    URI = f'sqlite:///{databasePath}'
    engine = create_engine(
        URI,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
    return engine

