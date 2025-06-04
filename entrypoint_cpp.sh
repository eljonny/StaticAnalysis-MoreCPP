#!/bin/bash
# shellcheck disable=SC2155

set -e

# Following variables are declared/defined in parent script
preselected_files=${preselected_files:-""}
print_to_console=${print_to_console:-false}
use_extra_directory=${use_extra_directory:-false}
common_ancestor=${common_ancestor:-""}

FLAWFINDER_ARGS="${INPUT_FLAWFINDER_ARGS//$'\n'/}"
FLAWFINDER_TGTS="${INPUT_FLAWFINDER_TARGETS//$'\n'/}"
CPPCHECK_ARGS="${INPUT_CPPCHECK_ARGS//$'\n'/}"
INFER_ARGS="${INPUT_FBINFER_ARGS//$'\n'/}"
CLANG_TIDY_ARGS="${INPUT_CLANG_TIDY_ARGS//$'\n'/}"

WS_BASE="$GITHUB_WORKSPACE/build"
WS_INFER="$GITHUB_WORKSPACE/build/infer-out"

cd build

if [ "$INPUT_REPORT_PR_CHANGES_ONLY" = true ]; then
  if [ -z "$preselected_files" ]; then
        # Create empty files
        touch flawfinder.txt
        touch cppcheck.txt
        touch infer.json
        touch clang_tidy.txt

        cd /
        python3 -m src.static_analysis_cpp -ff "$WS_BASE/flawfinder.txt" -cc "$WS_BASE/cppcheck.txt" -fi "$WS_BASE/infer.json" -ct "$WS_BASE/clang_tidy.txt" -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
        exit 0
   fi
fi

if [ "$INPUT_USE_CMAKE" = true ]; then
    # Trim trailing newlines
    INPUT_CMAKE_ARGS="${INPUT_CMAKE_ARGS%"${INPUT_CMAKE_ARGS##*[![:space:]]}"}"
    debug_print "Running cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON $INPUT_CMAKE_ARGS -S $GITHUB_WORKSPACE -B $(pwd)"
    eval "cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON $INPUT_CMAKE_ARGS -S $GITHUB_WORKSPACE -B $(pwd)"
fi

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    debug_print "Running: files_to_check=python3 /src/get_files_to_check.py -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\" -lang=\"c++\")"
    files_to_check=$(python3 /src/get_files_to_check.py -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="c++")
else
    debug_print "Running: files_to_check=python3 /src/get_files_to_check.py -exclude=\"$INPUT_EXCLUDE_DIR\" -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\" -lang=\"c++\")"
    files_to_check=$(python3 /src/get_files_to_check.py -exclude="$INPUT_EXCLUDE_DIR" -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="c++")
fi

debug_print "FLAWFINDER_ARGS = $FLAWFINDER_ARGS"
debug_print "FLAWFINDER_TGTS = $FLAWFINDER_TGTS"
debug_print "Files to check = $files_to_check"
debug_print "CPPCHECK_ARGS = $CPPCHECK_ARGS"
debug_print "CLANG_TIDY_ARGS = $CLANG_TIDY_ARGS"
debug_print "INFER_ARGS = $INFER_ARGS"
debug_print "WS_BASE = $WS_BASE"
debug_print "WS_INFER = $WS_INFER"

if [ -z "$files_to_check" ]; then
    echo "No files to check"

else
    cpp_files_to_check=""
    for file in $files_to_check; do
        file_extension="${file##*.}"
        if [[ "${file_extension,,}" =~ (c(c|p(pm?)?|\+\+)?|(c|i)xx) ]]; then
            if [ -z "${cpp_files_to_check}" ]; then
                cpp_files_to_check="$file"
            else
                cpp_files_to_check="$cpp_files_to_check $file"
            fi
        fi
    done

    debug_print "CPPCheck will check the following files: $cpp_files_to_check"

    for ffdir in $FLAWFINDER_TGTS; do
        dir_name=$(echo "$ffdir" | tr '/' '_')

        debug_print "Running flawfinder $FLAWFINDER_ARGS --sarif for files in /$GITHUB_WORKSPACE/$ffdir..."
        eval flawfinder "$FLAWFINDER_ARGS" --sarif "/$GITHUB_WORKSPACE/$ffdir" > "flawfinder_$dir_name.sarif" 2>&1 || true
    done

    debug_print "Aggregating flawfinder results into $WS_BASE/flawfinder.sarif..."
    python3 -m src.join_sarif --files "$(ls flawfinder_*.sarif)" --output "$WS_BASE/flawfinder.sarif"

    if [ "$INPUT_USE_CMAKE" = true ]; then
        for file in $cpp_files_to_check; do
            file_name=$(echo "$file" | tr '/' '_')

            debug_print "Running cppcheck --project=compile_commands.json $CPPCHECK_ARGS --file-filter=$file --output-format=sarif --output-file=cppcheck_$file_name.sarif"
            eval cppcheck --project=compile_commands.json "$CPPCHECK_ARGS" --file-filter="$file" --output-format=sarif --output-file="cppcheck_$file_name.sarif" || true
        done

        debug_print "Aggregating cppcheck results into $WS_BASE/cppcheck.sarif..."
        python3 -m src.join_sarif --files "$(ls cppcheck_*.sarif)" --output "$WS_BASE/cppcheck.sarif"

        debug_print "Running infer run --no-progress-bar --compilation-database compile_commands.json $INFER_ARGS --sarif..."
        eval infer run --no-progress-bar --compilation-database compile_commands.json "$INFER_ARGS" --sarif || true

        # Excludes for clang-tidy are handled in python script
        debug_print "Running run-clang-tidy-19 $CLANG_TIDY_ARGS -p $(pwd) $files_to_check >>clang_tidy.txt 2>&1"
        eval run-clang-tidy-19 "$CLANG_TIDY_ARGS" -p "$(pwd)" "$files_to_check" >clang_tidy.txt 2>&1 || true

    else
        debug_print "Running cppcheck $cpp_files_to_check $CPPCHECK_ARGS --output-format=sarif --output-file=cppcheck.sarif ..."
        eval cppcheck "$cpp_files_to_check" "$CPPCHECK_ARGS" --output-format=sarif --output-file=cppcheck.sarif || true

        debug_print "Running infer run --no-progress-bar --sarif $INFER_ARGS..."
        eval infer run --no-progress-bar --sarif "$INFER_ARGS" || true

        debug_print "Running run-clang-tidy-19 $CLANG_TIDY_ARGS $files_to_check >>clang_tidy.txt 2>&1"
        eval run-clang-tidy-19 "$CLANG_TIDY_ARGS" "$files_to_check" >clang_tidy.txt 2>&1 || true
    fi

    cd /

    python3 -m src.static_analysis_cpp -ff "$WS_BASE/flawfinder.sarif" -cc "$WS_BASE/cppcheck.sarif" -fi "$WS_INFER/report.sarif" -ct "$WS_BASE/clang_tidy.txt" -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
fi
