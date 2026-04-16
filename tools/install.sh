#!/usr/bin/env bash
# Claude Skills installer — symlink skills to ~/.claude/skills/
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

usage() {
    cat <<EOF
Claude Skills Installer

Usage:
    install.sh install <skill-name>   安裝指定 skill（symlink）
    install.sh install --all          安裝全部 skills
    install.sh remove <skill-name>    移除指定 skill
    install.sh update                 git pull 並重新 symlink
    install.sh list                   列出所有可安裝的 skills
    install.sh installed              列出已安裝的 skills
    install.sh help                   顯示此說明

EOF
}

install_skill() {
    local name="$1"

    # Guard against path traversal (e.g. "../../.ssh/keys")
    if [[ "$name" == */* ]] || [[ "$name" == *..* ]]; then
        echo "Error: invalid skill name '$name' (must not contain / or ..)"
        exit 1
    fi

    local src="$SKILLS_DIR/$name"
    local dst="$TARGET_DIR/$name"

    if [ ! -d "$src" ]; then
        echo "Error: skill '$name' not found in $SKILLS_DIR/"
        echo "Available skills:"
        list_skills
        exit 1
    fi

    mkdir -p "$TARGET_DIR"

    if [ -L "$dst" ]; then
        echo "Updating: $name (re-linking)"
        rm "$dst"
    elif [ -d "$dst" ]; then
        echo "Warning: $dst exists and is not a symlink. Skipping."
        echo "  Remove it manually if you want to install from this repo."
        return 1
    fi

    ln -s "$src" "$dst"
    echo "Installed: $name -> $dst"
}

remove_skill() {
    local name="$1"

    # Guard against path traversal
    if [[ "$name" == */* ]] || [[ "$name" == *..* ]]; then
        echo "Error: invalid skill name '$name' (must not contain / or ..)"
        exit 1
    fi

    local dst="$TARGET_DIR/$name"

    if [ -L "$dst" ]; then
        rm "$dst"
        echo "Removed: $name"
    elif [ -d "$dst" ]; then
        echo "Warning: $dst is not a symlink (not installed by this tool). Skipping."
        exit 1
    else
        echo "Skill '$name' is not installed."
    fi
}

list_skills() {
    for dir in "$SKILLS_DIR"/*/; do
        [ -d "$dir" ] || continue
        local name
        name=$(basename "$dir")
        local desc=""
        if [ -f "$dir/SKILL.md" ]; then
            desc=$(grep '^description:' "$dir/SKILL.md" | head -1 | sed 's/^description: *//')
        fi
        printf "  %-25s %s\n" "$name" "$desc"
    done
}

list_installed() {
    local found=0
    for dir in "$TARGET_DIR"/*/; do
        [ -d "$dir" ] || continue
        if [ -L "${dir%/}" ]; then
            local target
            target=$(readlink "${dir%/}")
            if [[ "$target" == "$SKILLS_DIR"* ]]; then
                echo "  $(basename "$dir") (from claude-skills repo)"
                found=1
            fi
        fi
    done
    if [ "$found" -eq 0 ]; then
        echo "  (none installed from this repo)"
    fi
}

update_skills() {
    echo "Pulling latest..."
    cd "$REPO_DIR" && git pull --ff-only
    echo ""
    echo "Re-linking all installed skills..."
    for dir in "$TARGET_DIR"/*/; do
        [ -L "${dir%/}" ] || continue
        local target
        target=$(readlink "${dir%/}")
        if [[ "$target" == "$SKILLS_DIR"* ]]; then
            local name
            name=$(basename "$dir")
            if [ -d "$SKILLS_DIR/$name" ]; then
                install_skill "$name"
            else
                echo "Warning: '$name' no longer exists in repo; skipping (symlink left in place)"
            fi
        fi
    done
    echo "Done."
}

# --- Main ---
cmd="${1:-help}"
shift || true

case "$cmd" in
    install)
        if [ "${1:-}" = "--all" ]; then
            for dir in "$SKILLS_DIR"/*/; do
                [ -d "$dir" ] || continue
                install_skill "$(basename "$dir")"
            done
        elif [ -n "${1:-}" ]; then
            install_skill "$1"
        else
            echo "Usage: install.sh install <skill-name|--all>"
            exit 1
        fi
        ;;
    remove)
        [ -n "${1:-}" ] || { echo "Usage: install.sh remove <skill-name>"; exit 1; }
        remove_skill "$1"
        ;;
    update)
        update_skills
        ;;
    list)
        echo "Available skills:"
        list_skills
        ;;
    installed)
        echo "Installed skills (from this repo):"
        list_installed
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo "Unknown command: $cmd"
        usage
        exit 1
        ;;
esac
