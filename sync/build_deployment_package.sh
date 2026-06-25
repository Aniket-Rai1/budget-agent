#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${REPO_ROOT}/sync/.build"
OUTPUT_ZIP="${REPO_ROOT}/sync/deployment_package.zip"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

pip install -r "${REPO_ROOT}/sync/requirements.txt" -t "$BUILD_DIR"

cp "${REPO_ROOT}/sync/lambda_function.py" "$BUILD_DIR/"
cp "${REPO_ROOT}/sync/plaid_client.py" "$BUILD_DIR/"
cp -r "${REPO_ROOT}/db" "$BUILD_DIR/"
cp -r "${REPO_ROOT}/models" "$BUILD_DIR/"

rm -f "$OUTPUT_ZIP"
(cd "$BUILD_DIR" && zip -r "$OUTPUT_ZIP" .)

SIZE_BYTES=$(stat -f%z "$OUTPUT_ZIP" 2>/dev/null || stat -c%s "$OUTPUT_ZIP")
SIZE_MB=$(echo "scale=2; $SIZE_BYTES / 1048576" | bc)

echo "Built: $OUTPUT_ZIP (${SIZE_MB} MB)"

if [ "$(echo "$SIZE_MB > 50" | bc)" -eq 1 ]; then
    echo "WARNING: Zip exceeds Lambda's 50 MB direct-upload limit."
    echo "Upload via S3 instead of the Lambda console."
fi
