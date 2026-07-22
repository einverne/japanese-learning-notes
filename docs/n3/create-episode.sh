#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -gt 1 ]]; then
  echo "Usage: $(basename "$0") [episode_number]" >&2
  exit 1
fi

if [[ $# -eq 1 ]]; then
  if [[ ! $1 =~ ^[0-9]+$ ]]; then
    echo "Episode number must be a non-negative integer." >&2
    exit 1
  fi
  episode_number=$((10#$1))
else
  latest_number=0
  shopt -s nullglob
  for file in "$script_dir"/n3-ep[0-9][0-9][0-9].md; do
    filename="${file##*/}"
    number="${filename#n3-ep}"
    number="${number%.md}"
    value=$((10#$number))
    if (( value > latest_number )); then
      latest_number=$value
    fi
  done
  episode_number=$((latest_number + 1))
fi

printf -v episode "%03d" "$episode_number"
target="$script_dir/n3-ep${episode}.md"

if [[ -e $target ]]; then
  echo "File already exists: $target" >&2
  exit 1
fi

printf '%s\n' '---' 'comments: true' '---' > "$target"
echo "Created: $target"
