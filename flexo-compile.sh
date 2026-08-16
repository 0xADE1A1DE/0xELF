#!/bin/bash

FLEXO_DIR=$(realpath ./Flexo 2>/dev/null)

if [ ! -d "$FLEXO_DIR" ]; then
    echo "Flexo not found at $FLEXO_DIR"
    exit 1
fi

if [ -z "$1" ]; then
    echo "SYNTAX: $0 <cppfile> [other compilation dependencies]"
    exit 1
fi

ABS_SRC=$(realpath "$1" 2>/dev/null)

if [ -z "$ABS_SRC" ] || [ ! -f "$ABS_SRC" ]; then
    echo "$1 is not a valid file"
    exit 1
fi

SRC_BASENAME=$(basename "$ABS_SRC")
SRC_NAME="${SRC_BASENAME%%.*}"
TMP_NAME="tmp_compile_$$"
TMP_DIR="$FLEXO_DIR/$TMP_NAME"

# Create temporary directory inside Flexo
mkdir -p "$TMP_DIR"
cp "$ABS_SRC" "$TMP_DIR/"

shift
while [ $# -gt 0 ]; do
	DEP=$(realpath "$1" 2>/dev/null)
	cp "$DEP" "$TMP_DIR/"
	shift
done

if [ ! -z "$WM_CIRCUIT_FILE" ]; then
	cp "$WM_CIRCUIT_FILE" "$TMP_DIR/"
	WM_CIRCUIT_FILE="$TMP_NAME/$(basename "$WM_CIRCUIT_FILE")"
fi

# Temporary files
SOURCE_FILE="$TMP_NAME/$SRC_BASENAME"
LL_FILE="$TMP_NAME/$SRC_NAME.ll"
WMLL_FILE="$TMP_NAME/$SRC_NAME-wm.ll"
OUTPUT_FILE="$TMP_NAME/$SRC_NAME.elf"

ENVIRON_REGEX="(WM.*|RET_.*|WR.*|DUAL_WM_MAX_INPUT)"

echo "1. COMPILING $SRC_BASENAME TO LLVM IR"
podman run -i -t --rm \
  --mount type=bind,source="$FLEXO_DIR",target=/flexo,z \
  flexo \
  clang-17 -fno-discard-value-names -O1 -fno-inline-functions -S -emit-llvm \
    "/flexo/$SOURCE_FILE" -o "/flexo/$LL_FILE"

echo "2. RUNNING FLEXO WITH PARAMETERS "
printf "\t$(env | grep -P "$ENVIRON_REGEX" | tr '\n' ' ')"
#printf "\tCommand: opt-17 -load-pass-plugin ./build/lib/libFlexo.so -passes=\"create-WMs\" \"$LL_FILE\" -o \"$WMLL_FILE\"\n"

if [ ! -d "$FLEXO_DIR/tmp" ]; then
    mkdir "$FLEXO_DIR/tmp"
fi

podman run --env "WM_*" --env "RET_*" --env "WR_*" --env "DUAL_WM_MAX_INPUT" -i -t --rm \
  --mount type=bind,source="$FLEXO_DIR",target=/flexo,z \
  --mount type=bind,source="$FLEXO_DIR/tmp",target=/tmp,z \
  flexo bash -c "cd /flexo && opt-17 -load-pass-plugin ./build/lib/libFlexo.so -passes=\"create-WMs\" \"$LL_FILE\" -S -o \"$WMLL_FILE\""

echo "3. FINAL COMPILATION STEP"
podman run -i -t --rm \
  --mount type=bind,source="$FLEXO_DIR",target=/flexo,z \
  flexo \
  clang-17 -static "/flexo/$WMLL_FILE" -o "/flexo/$OUTPUT_FILE" -lm -lstdc++

echo "Compiled binary generated in $FLEXO_DIR/$OUTPUT_FILE"
# Copy the final elf to the original source directory
cp -i "$FLEXO_DIR/$OUTPUT_FILE" "$(dirname "$ABS_SRC")/$SRC_NAME.elf"

#echo -n "The hash of the file is: "
#sha256sum "$(dirname "$ABS_SRC")/$SRC_NAME.elf"
if [ $? -eq 0 ]; then
	echo "Binary copied to $(dirname "$ABS_SRC")/$SRC_NAME.elf"
fi

# Cleanup temporary directory
# rm -rf "$TMP_DIR"
