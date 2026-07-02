#!/usr/bin/env bash
set -euo pipefail

# Read hook input
file_path=$(jq -r '.tool_input.file_path // empty')

# Only trigger on test files
case "$file_path" in
    *tests/*.py)
        echo "🧪 Running pytest: $file_path"
        uv run pytest "$file_path" \
            -q \
            --tb=line \
            --color=yes \
            || true
        ;;
esac
