#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="${1:-demo}"
OUT_DIR="${2:-docs/demo_gif}"
MAX_MB="${3:-8}"
MANIFEST="${4:-README_DEMOS.md}"

# 默认转换完整视频。
# 如需手动截取，可运行：
# START=2 DURATION=5 ./scripts/convert_mp4_to_readme_gif.sh demo docs/demo_gif
START="${START:-}"
DURATION="${DURATION:-}"

command -v ffmpeg >/dev/null || {
  echo "Error: ffmpeg not found. Please install ffmpeg first."
  exit 1
}

command -v python3 >/dev/null || {
  echo "Error: python3 not found. python3 is used for URL encoding."
  exit 1
}

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Error: source directory not found: $SRC_DIR"
  exit 1
fi

max_bytes=$((MAX_MB * 1024 * 1024))

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$OUT_DIR"

printf "## Demos\n\n| Demo | Preview |\n|---|---|\n" > "$MANIFEST"

urlencode() {
  python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe="/"))' "$1"
}

found=0

while IFS= read -r -d '' in; do
  found=1

  rel="${in#"$SRC_DIR"/}"
  rel_noext="${rel%.*}"
  out="$OUT_DIR/$rel_noext.gif"

  mkdir -p "$(dirname "$out")"

  echo "==> Converting: $in"

  input_args=()

  if [[ -n "$START" ]]; then
    input_args+=(-ss "$START")
  fi

  if [[ -n "$DURATION" ]]; then
    input_args+=(-t "$DURATION")
  fi

  best="$tmpdir/best.gif"
  rm -f "$best"

  # 从清晰到更小逐步尝试。
  # 完整视频转 GIF 很容易变大，所以这里会自动降分辨率和 fps。
  for spec in "720 12" "640 10" "560 10" "480 8" "360 8"; do
    read -r width fps <<< "$spec"

    pal="$tmpdir/palette.png"
    tmpgif="$tmpdir/tmp.gif"

    rm -f "$pal" "$tmpgif"

    vf="fps=${fps},scale=${width}:-1:flags=lanczos"

    ffmpeg -nostdin -hide_banner -loglevel error -y \
      "${input_args[@]}" -i "$in" \
      -vf "${vf},palettegen=stats_mode=diff" \
      "$pal"

    ffmpeg -nostdin -hide_banner -loglevel error -y \
      "${input_args[@]}" -i "$in" -i "$pal" \
      -filter_complex "${vf}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
      "$tmpgif"

    bytes=$(wc -c < "$tmpgif" | tr -d ' ')
    mb=$(python3 -c 'import sys; print(f"{int(sys.argv[1]) / 1024 / 1024:.2f}")' "$bytes")

    echo "    width=${width}, fps=${fps} -> ${mb} MB"

    cp "$tmpgif" "$best"

    if (( bytes <= max_bytes )); then
      break
    fi
  done

  cp "$best" "$out"

  final_bytes=$(wc -c < "$out" | tr -d ' ')
  final_mb=$(python3 -c 'import sys; print(f"{int(sys.argv[1]) / 1024 / 1024:.2f}")' "$final_bytes")

  if (( final_bytes > max_bytes )); then
    echo "    Warning: final GIF is still larger than ${MAX_MB} MB: ${final_mb} MB"
  else
    echo "    Saved: $out (${final_mb} MB)"
  fi

  url="$(urlencode "$out")"
  printf "| \`%s\` | <img src=\"%s\" width=\"640\"> |\n" "$rel_noext" "$url" >> "$MANIFEST"

done < <(find "$SRC_DIR" -type f -iname "*.mp4" -print0)

if [[ "$found" -eq 0 ]]; then
  echo "No MP4 files found under: $SRC_DIR"
  exit 0
fi

echo
echo "Done."
echo "GIF output dir: $OUT_DIR"
echo "Markdown table: $MANIFEST"
echo
echo "Large generated GIFs:"
find "$OUT_DIR" -type f -name "*.gif" -size +"$MAX_MB"M -print || true