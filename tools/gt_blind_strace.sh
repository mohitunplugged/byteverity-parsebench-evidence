#!/bin/sh
# OS-level GT-blind audit: trace EVERY openat() (Python and native MuPDF) during a full replay.
# usage: tools/gt_blind_strace.sh <frozen_outputs/arm> <python>
strace -f -qq -e trace=openat,open -o strace_openat.log "$2" tools/gt_blind_audit.py "$1" > /dev/null 2>&1
grep -oE '"[^"]+"' strace_openat.log | tr -d '"' | sort -u > files_opened_os_level.txt
echo "OS-level distinct paths opened: $(wc -l < files_opened_os_level.txt)"
echo "  PDFs: $(grep -c '\.pdf$' files_opened_os_level.txt)  raw outputs: $(grep -c '\.raw\.json$' files_opened_os_level.txt)  rulebook files: $(grep -c '/rulebook/' files_opened_os_level.txt)"
GT=$(grep -E '\.jsonl$|\.test\.json$' files_opened_os_level.txt)
echo "GROUND-TRUTH FILES OPENED (OS level): ${GT:-NONE}"
rm -f strace_openat.log
