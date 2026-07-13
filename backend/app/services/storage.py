import os
import tempfile
from supabase import create_client
from app.config import settings

client = create_client(settings.SUPABASE_URL,
                       settings.SUPABASE_SERVICE_ROLE_KEY)


async def download_from_storage(org_id: str, file_name: str) -> str:
    data = client.storage.from_(
        "raw-uploads").download(f"{org_id}/{file_name}")
    tmp_path = os.path.join(tempfile.gettempdir(), file_name)
    with open(tmp_path, "wb") as f:
        f.write(data)
    return tmp_path


async def upload_to_storage(org_id: str, file_name: str, contents: bytes) -> None:
    client.storage.from_(
        "raw-uploads").upload(f"{org_id}/{file_name}", contents, {"upsert": "true"})
