import os
from datetime import datetime, timezone
from pathlib import Path

import boto3


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIRECTORIES = [
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "data" / "warehouse",
    PROJECT_ROOT / "data" / "power_bi",
]


def collect_output_files():
    """Return every generated pipeline output file."""

    files = []

    for directory in OUTPUT_DIRECTORIES:
        if directory.exists():
            files.extend(
                path
                for path in directory.rglob("*")
                if path.is_file()
            )

    if not files:
        raise FileNotFoundError(
            "No pipeline output files were found for upload."
        )

    return sorted(files)


def main():
    bucket_name = os.getenv("S3_BUCKET")

    if not bucket_name:
        raise RuntimeError(
            "S3_BUCKET environment variable is missing."
        )

    aws_region = os.getenv(
        "AWS_REGION",
        "eu-central-1",
    )

    s3_prefix = (
        os.getenv("S3_PREFIX", "energy-analytics")
        .strip("/")
        or "energy-analytics"
    )

    run_id = os.getenv("PIPELINE_RUN_ID")

    if not run_id:
        run_id = datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%SZ")

    output_files = collect_output_files()

    s3_client = boto3.client(
        "s3",
        region_name=aws_region,
    )

    print(f"Uploading outputs to s3://{bucket_name}/")
    print(f"Pipeline run ID: {run_id}")

    for local_file in output_files:
        relative_path = local_file.relative_to(
            PROJECT_ROOT
        ).as_posix()

        run_key = (
            f"{s3_prefix}/runs/"
            f"{run_id}/{relative_path}"
        )

        latest_key = (
            f"{s3_prefix}/latest/"
            f"{relative_path}"
        )

        for object_key in [run_key, latest_key]:
            s3_client.upload_file(
                str(local_file),
                bucket_name,
                object_key,
                ExtraArgs={
                    "ServerSideEncryption": "AES256",
                },
            )

            print(
                f"Uploaded {relative_path} "
                f"to s3://{bucket_name}/{object_key}"
            )

    print(
        f"Successfully uploaded {len(output_files)} "
        "pipeline files to run-specific and latest paths."
    )


if __name__ == "__main__":
    main()