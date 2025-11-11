from huggingface_hub import hf_hub_download
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

def downloadDatabase(repoID,accessToken,filename):
    dataset_path = hf_hub_download(
        repo_id=repoID,
        repo_type="dataset",
        token=accessToken,
        local_dir='../dataset',
        dry_run=True,
        filename=filename
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

