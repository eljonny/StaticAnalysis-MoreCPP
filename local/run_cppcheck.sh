RUN_FINDFILES_SCRIPT="$1"
SRC_DIR="$2"
EXCLUDES="$3"
CPPCHECK_ARGS="$4"

#EXCLUDES="/out/ /.git /.vs /3rdparty/ /cmake/ /custom-overlay/ /infer-out/ /test/ /test_package/ /demo/ /_packages/ /res/"
#CPPCHECK_ARGS="--quiet --enable=all --inconclusive --suppress=missingIncludeSystem --suppress=unusedFunction --std=c++11 --inline-suppr --force --check-level=exhaustive --suppress='*:*3rdparty*' --checkers-report=cppcheck-checkers.report --suppress=checkersReport"

echo "Running $RUN_FINDFILES_SCRIPT on $SRC_DIR with the following exclusions: $EXCLUDES"

files_to_check=$(python3 $RUN_FINDFILES_SCRIPT -exclude="$EXCLUDES" -dir="$SRC_DIR" -lang="c++")

for file in $files_to_check; do
    file_extension="${file##*.}"
    if [[ "${file_extension,,}" =~ (c(c|p(pm?)?|\+\+)?|(c|i)xx) ]]; then
        # Replace '/' with '_'
        file_name=$(echo "$file" | tr '/' '_')

        echo "Running cppcheck --project=compile_commands.json $CPPCHECK_ARGS --file-filter=$file --output-format=sarif --output-file=cppcheck_$file_name.txt"
        eval cppcheck --project=compile_commands.json "$CPPCHECK_ARGS" --file-filter="$file" --output-format=sarif --output-file="cppcheck_$file_name.sarif" || true
    else
        echo "Skipping cppcheck run for $file"
    fi
done
