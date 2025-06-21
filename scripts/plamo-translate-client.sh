#!/bin/bash

# PLaMo Translate HTTP Client Script
# Usage: plamo-translate-client.sh [OPTIONS] [TEXT]

# Default configuration
PLAMO_HOST="${PLAMO_HOST:-localhost}"
PLAMO_PORT="${PLAMO_PORT:-8080}"
FROM_LANG="${PLAMO_FROM:-English|Japanese}"
TO_LANG="${PLAMO_TO:-}"

# Function to show help
show_help() {
    cat << EOF
PLaMo Translate HTTP Client

Usage: $0 [OPTIONS] [TEXT]

Options:
    -h, --help              Show this help message
    -s, --server HOST:PORT  Server address (default: ${PLAMO_HOST}:${PLAMO_PORT})
    -f, --from LANG         Source language (default: ${FROM_LANG})
    -t, --to LANG           Target language (default: ${TO_LANG})
    -i, --input TEXT        Input text to translate
    --health                Check server health
    --languages             List supported languages

Environment Variables:
    PLAMO_HOST              Server host (default: localhost)
    PLAMO_PORT              Server port (default: 8080)
    PLAMO_FROM              Default source language
    PLAMO_TO                Default target language

Examples:
    # Basic usage
    $0 "Hello world"
    
    # With specific languages
    $0 --from English --to Japanese "Hello world"
    
    # Using pipe
    echo "家計は火の車だ" | $0
    
    # Check server status
    $0 --health
    
    # List supported languages
    $0 --languages

EOF
}

# Function to check server health
check_health() {
    local url="http://${PLAMO_HOST}:${PLAMO_PORT}/health"
    local response
    
    if response=$(curl -s -f "$url" 2>/dev/null); then
        echo "Server is healthy"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 0
    else
        echo "Server is not responding at $url" >&2
        return 1
    fi
}

# Function to list supported languages
list_languages() {
    local url="http://${PLAMO_HOST}:${PLAMO_PORT}/languages"
    local response
    
    if response=$(curl -s -f "$url" 2>/dev/null); then
        echo "Supported languages:"
        echo "$response" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for lang in data['supported_languages']:
    print(f'  - {lang}')
" 2>/dev/null || echo "$response"
        return 0
    else
        echo "Failed to get languages from server at $url" >&2
        return 1
    fi
}

# Function to translate text
translate_text() {
    local text="$1"
    local url="http://${PLAMO_HOST}:${PLAMO_PORT}/translate"
    local json_data
    local response
    
    # Create JSON payload
    json_data=$(python3 -c "
import json, sys
data = {
    'text': '''$text''',
    'from_lang': '''$FROM_LANG''',
    'to_lang': '''$TO_LANG'''
}
print(json.dumps(data, ensure_ascii=False))
" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo "Failed to create JSON payload" >&2
        return 1
    fi
    
    # Send request
    if response=$(curl -s -f -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$json_data" 2>/dev/null); then
        
        # Extract translated text
        echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data['translated_text'])
except:
    print(sys.stdin.read())
" 2>/dev/null || echo "$response"
        return 0
    else
        echo "Translation failed. Check if server is running at $url" >&2
        return 1
    fi
}

# Parse command line arguments
INPUT_TEXT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--server)
            if [[ -z "$2" ]]; then
                echo "Error: --server requires a value" >&2
                exit 1
            fi
            IFS=':' read -r PLAMO_HOST PLAMO_PORT <<< "$2"
            shift 2
            ;;
        -f|--from)
            if [[ -z "$2" ]]; then
                echo "Error: --from requires a value" >&2
                exit 1
            fi
            FROM_LANG="$2"
            shift 2
            ;;
        -t|--to)
            if [[ -z "$2" ]]; then
                echo "Error: --to requires a value" >&2
                exit 1
            fi
            TO_LANG="$2"
            shift 2
            ;;
        -i|--input)
            if [[ -z "$2" ]]; then
                echo "Error: --input requires a value" >&2
                exit 1
            fi
            INPUT_TEXT="$2"
            shift 2
            ;;
        --health)
            check_health
            exit $?
            ;;
        --languages)
            list_languages
            exit $?
            ;;
        -*)
            echo "Error: Unknown option $1" >&2
            exit 1
            ;;
        *)
            INPUT_TEXT="$1"
            shift
            ;;
    esac
done

# Get input text
if [[ -z "$INPUT_TEXT" ]]; then
    if [[ ! -t 0 ]]; then
        # Read from stdin
        INPUT_TEXT=$(cat)
    else
        echo "Error: No input text provided" >&2
        echo "Use --help for usage information" >&2
        exit 1
    fi
fi

# Translate
translate_text "$INPUT_TEXT"