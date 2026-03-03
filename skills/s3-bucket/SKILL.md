---
name: s3-bucket
description: Interact with S3-compatible object storage (AWS S3, MinIO, etc.). Use when you need to list buckets, list objects in a bucket, upload files, download files, or delete objects. Reads credentials and endpoint from environment variables.
metadata:
  {
    "openclaw":
      {
        "emoji": "🪣",
        "requires": { "bins": ["uv"] },
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# S3 Bucket

Interact with S3-compatible object storage using Python and `boto3`. Supports AWS S3 and any S3-compatible service (MinIO, Backblaze B2, Cloudflare R2, etc.).

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | Yes | Access key ID |
| `AWS_SECRET_ACCESS_KEY` | Yes | Secret access key |
| `AWS_ENDPOINT_URL` | No | Custom endpoint URL (for MinIO, R2, etc.) |
| `AWS_DEFAULT_REGION` | No | AWS region (default: `us-east-1`) |

## Usage

### List all buckets

```bash
uv run {baseDir}/scripts/s3.py list-buckets
```

### List objects in a bucket

```bash
uv run {baseDir}/scripts/s3.py list-objects my-bucket
uv run {baseDir}/scripts/s3.py list-objects my-bucket --prefix photos/
```

### Upload a file

```bash
uv run {baseDir}/scripts/s3.py upload /path/to/local/file.txt my-bucket
uv run {baseDir}/scripts/s3.py upload /path/to/local/file.txt my-bucket --key custom/key/file.txt
```

### Download a file

```bash
uv run {baseDir}/scripts/s3.py download my-bucket remote/key.txt /path/to/local/file.txt
```

### Delete an object

```bash
uv run {baseDir}/scripts/s3.py delete my-bucket remote/key.txt
```

### JSON output (all commands)

Append `--json` to any command for machine-readable output:

```bash
uv run {baseDir}/scripts/s3.py list-buckets --json
uv run {baseDir}/scripts/s3.py list-objects my-bucket --json
```

## Example: MinIO / self-hosted S3

```bash
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_ENDPOINT_URL=http://localhost:9000
export AWS_DEFAULT_REGION=us-east-1

uv run {baseDir}/scripts/s3.py list-buckets
```

## Example: AWS S3

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-east-1

uv run {baseDir}/scripts/s3.py list-objects my-bucket --prefix logs/
```
