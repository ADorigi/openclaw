#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "boto3>=1.26.0",
# ]
# ///
"""
Interact with S3-compatible object storage via boto3.

Credentials and endpoint are read from environment variables:
  AWS_ACCESS_KEY_ID       - access key ID (required)
  AWS_SECRET_ACCESS_KEY   - secret access key (required)
  AWS_ENDPOINT_URL        - custom endpoint URL, e.g. http://localhost:9000 (optional)
  AWS_DEFAULT_REGION      - region, defaults to us-east-1 (optional)

Usage:
    uv run s3.py list-buckets [--json]
    uv run s3.py list-objects <bucket> [--prefix PREFIX] [--json]
    uv run s3.py upload <local-path> <bucket> [--key KEY] [--json]
    uv run s3.py download <bucket> <key> <local-path> [--json]
    uv run s3.py delete <bucket> <key> [--json]
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
except ImportError:
    print("Error: boto3 is not installed.", file=sys.stderr)
    print("Install it with: uv add boto3", file=sys.stderr)
    sys.exit(2)


def make_client():
    """Build an S3 client from environment variables."""
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")  # None = use AWS default

    try:
        client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            # boto3 picks up AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY automatically
        )
    except NoCredentialsError:
        return None, "AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not set"

    return client, None


def cmd_list_buckets(client) -> dict:
    """Return all buckets the credentials can see."""
    try:
        resp = client.list_buckets()
        buckets = [
            {"name": b["Name"], "created": b["CreationDate"].isoformat()}
            for b in resp.get("Buckets", [])
        ]
        return {"success": True, "buckets": buckets}
    except (ClientError, BotoCoreError) as exc:
        return {"success": False, "error": str(exc)}


def cmd_list_objects(client, bucket: str, prefix: str = "") -> dict:
    """List objects in a bucket, optionally filtered by prefix."""
    try:
        paginator = client.get_paginator("list_objects_v2")
        objects = []
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                objects.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                    }
                )
        return {"success": True, "bucket": bucket, "prefix": prefix, "objects": objects}
    except (ClientError, BotoCoreError) as exc:
        return {"success": False, "error": str(exc)}


def cmd_upload(client, local_path: str, bucket: str, key: str | None = None) -> dict:
    """Upload a local file to a bucket."""
    path = Path(local_path)
    if not path.is_file():
        return {"success": False, "error": f"Local file not found: {local_path}"}

    # Default key is the filename
    remote_key = key if key else path.name

    try:
        client.upload_file(str(path), bucket, remote_key)
        return {
            "success": True,
            "uploaded": str(path),
            "bucket": bucket,
            "key": remote_key,
        }
    except (ClientError, BotoCoreError) as exc:
        return {"success": False, "error": str(exc)}


def cmd_download(client, bucket: str, key: str, local_path: str) -> dict:
    """Download an object from a bucket to a local file."""
    dest = Path(local_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        client.download_file(bucket, key, str(dest))
        return {
            "success": True,
            "bucket": bucket,
            "key": key,
            "downloaded_to": str(dest),
        }
    except (ClientError, BotoCoreError) as exc:
        return {"success": False, "error": str(exc)}


def cmd_delete(client, bucket: str, key: str) -> dict:
    """Delete an object from a bucket."""
    try:
        client.delete_object(Bucket=bucket, Key=key)
        return {"success": True, "deleted": {"bucket": bucket, "key": key}}
    except (ClientError, BotoCoreError) as exc:
        return {"success": False, "error": str(exc)}


def format_result(result: dict, command: str) -> str:
    """Format a result dict as human-readable text."""
    if not result["success"]:
        return f"Error: {result['error']}"

    if command == "list-buckets":
        buckets = result["buckets"]
        if not buckets:
            return "No buckets found."
        lines = [f"{'Bucket':<40}  Created"]
        lines.append("-" * 60)
        for b in buckets:
            lines.append(f"{b['name']:<40}  {b['created']}")
        return "\n".join(lines)

    if command == "list-objects":
        objects = result["objects"]
        if not objects:
            prefix_note = f" (prefix: {result['prefix']})" if result["prefix"] else ""
            return f"No objects in {result['bucket']}{prefix_note}."
        lines = [f"{'Key':<60}  {'Size':>12}  Last Modified"]
        lines.append("-" * 100)
        for obj in objects:
            size_str = _human_size(obj["size"])
            lines.append(f"{obj['key']:<60}  {size_str:>12}  {obj['last_modified']}")
        lines.append(f"\n{len(objects)} object(s)")
        return "\n".join(lines)

    if command == "upload":
        return f"Uploaded {result['uploaded']} → s3://{result['bucket']}/{result['key']}"

    if command == "download":
        return f"Downloaded s3://{result['bucket']}/{result['key']} → {result['downloaded_to']}"

    if command == "delete":
        d = result["deleted"]
        return f"Deleted s3://{d['bucket']}/{d['key']}"

    return json.dumps(result, indent=2)


def _human_size(n: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Interact with S3-compatible object storage"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-buckets", help="List all buckets")

    p_list = sub.add_parser("list-objects", help="List objects in a bucket")
    p_list.add_argument("bucket", help="Bucket name")
    p_list.add_argument("--prefix", default="", help="Key prefix to filter by")

    p_upload = sub.add_parser("upload", help="Upload a local file")
    p_upload.add_argument("local_path", help="Path to local file")
    p_upload.add_argument("bucket", help="Destination bucket")
    p_upload.add_argument("--key", default=None, help="Remote object key (default: filename)")

    p_dl = sub.add_parser("download", help="Download an object")
    p_dl.add_argument("bucket", help="Source bucket")
    p_dl.add_argument("key", help="Object key")
    p_dl.add_argument("local_path", help="Destination local path")

    p_del = sub.add_parser("delete", help="Delete an object")
    p_del.add_argument("bucket", help="Bucket name")
    p_del.add_argument("key", help="Object key to delete")

    args = parser.parse_args()

    client, err = make_client()
    if err:
        result = {"success": False, "error": err}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {err}", file=sys.stderr)
        return 1

    if args.command == "list-buckets":
        result = cmd_list_buckets(client)
    elif args.command == "list-objects":
        result = cmd_list_objects(client, args.bucket, args.prefix)
    elif args.command == "upload":
        result = cmd_upload(client, args.local_path, args.bucket, args.key)
    elif args.command == "download":
        result = cmd_download(client, args.bucket, args.key, args.local_path)
    elif args.command == "delete":
        result = cmd_delete(client, args.bucket, args.key)
    else:
        result = {"success": False, "error": f"Unknown command: {args.command}"}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_result(result, args.command))

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
