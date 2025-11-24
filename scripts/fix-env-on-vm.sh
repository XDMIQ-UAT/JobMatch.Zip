#!/bin/bash
# Fix malformed GOOGLE_SEARCH_CONSOLE_CREDENTIALS in .env file

cd /opt/jobmatch

# Find the line number where GOOGLE_SEARCH_CONSOLE_CREDENTIALS starts
LINE=$(grep -n "GOOGLE_SEARCH_CONSOLE_CREDENTIALS" .env | cut -d: -f1)

if [ -n "$LINE" ]; then
    # Delete from that line until we find the next variable (starts with uppercase letter) or end of file
    sed -i "${LINE},/^[A-Z_]/ { /^[A-Z_]/!d; }" .env
    
    # If the line still has the variable, replace it with empty string
    sed -i "${LINE}s/.*/GOOGLE_SEARCH_CONSOLE_CREDENTIALS=\"\"/" .env
fi

# Alternative: simple approach - just replace the problematic line
sed -i '/^GOOGLE_SEARCH_CONSOLE_CREDENTIALS=/c\GOOGLE_SEARCH_CONSOLE_CREDENTIALS=""' .env

echo "Fixed .env file"
cat .env | grep GOOGLE_SEARCH_CONSOLE_CREDENTIALS

