#!/bin/sh

set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH='' cd -- "$script_dir/.." && pwd)
source_file="$repo_root/codex-plugin/skills/prompt-it/SKILL.md"
codex_root=${CODEX_HOME:-"$HOME/.codex"}
target_dir="$codex_root/skills/prompt-it"
target_file="$target_dir/SKILL.md"

usage() {
  echo "Usage: $0 [--check]"
}

case ${1:-} in
  "")
    mkdir -p "$target_dir"
    cp "$source_file" "$target_file"
    echo "Synced $target_file"
    ;;
  --check)
    if [ ! -f "$target_file" ]; then
      echo "Prompt It is not installed at $target_file" >&2
      exit 1
    fi
    if ! cmp -s "$source_file" "$target_file"; then
      echo "Installed Prompt It skill differs from the canonical repository copy:" >&2
      diff -u "$source_file" "$target_file" || true
      exit 1
    fi
    echo "Prompt It skill is in sync"
    ;;
  -h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
