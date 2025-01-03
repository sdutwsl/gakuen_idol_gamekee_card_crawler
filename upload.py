import os
import boto3 # type: ignore
from botocore.exceptions import NoCredentialsError # type: ignore

R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
BUCKET_NAME = os.getenv("BUCKET_NAME")
PREFIX = os.getenv("PREFIX", "")

if not all([R2_ACCESS_KEY, R2_SECRET_KEY, R2_ENDPOINT_URL, BUCKET_NAME]):
    raise ValueError("Please make sure all required environment variables are set: R2_ACCESS_KEY, R2_SECRET_KEY, R2_ENDPOINT_URL, BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    endpoint_url=R2_ENDPOINT_URL,
)

def file_exists_in_bucket(bucket_name, file_path):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_path)
        return True
    except s3_client.exceptions.ClientError:
        return False

def upload_directory_to_r2(directory_path):
    if not os.path.isdir(directory_path):
        raise ValueError(f"{directory_path} is not a valid directory.")
    
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_file_path, directory_path)
            r2_path = os.path.join(PREFIX, relative_path).replace("\\", "/")

            if file_exists_in_bucket(BUCKET_NAME, r2_path):
                print(f"File already exists, skipping: {r2_path}")
                continue

            try:
                s3_client.upload_file(local_file_path, BUCKET_NAME, r2_path)
                print(f"Upload successful: {local_file_path} → {r2_path}")
            except NoCredentialsError:
                print("Invalid credentials.")
            except Exception as e:
                print(f"Upload failed: {local_file_path} → {r2_path}, error: {e}")

if __name__ == "__main__":
    directory_to_upload = "./download"
    upload_directory_to_r2(directory_to_upload)
