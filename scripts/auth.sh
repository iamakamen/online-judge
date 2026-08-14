#!/usr/bin/env bash

# Development-only authentication helper.
# Source this file to keep tokens in the current shell:
#   source scripts/auth.sh login

AUTH_BASE_URL="${AUTH_BASE_URL:-http://127.0.0.1:8000}"
AUTH_BASE_URL="${AUTH_BASE_URL%/}"

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    _AUTH_PERSISTENT_SHELL=0
else
    _AUTH_PERSISTENT_SHELL=1
fi

_auth_require_tools() {
    command -v curl >/dev/null 2>&1 || {
        echo "auth: curl is required" >&2
        return 1
    }
    command -v python3 >/dev/null 2>&1 || {
        echo "auth: python3 is required" >&2
        return 1
    }
}

_auth_login_request() {
    local request_file response_file http_code
    request_file=$(mktemp) || {
        echo "auth: could not create a temporary request file" >&2
        return 1
    }
    response_file=$(mktemp) || {
        rm -f "$request_file"
        echo "auth: could not create a temporary response file" >&2
        return 1
    }
    chmod 600 "$request_file" "$response_file"

    if ! printf '%s\0%s\0' "$1" "$2" | python3 -c '
import json
import sys

fields = sys.stdin.buffer.read().split(b"\0")
if len(fields) < 2:
    raise SystemExit(1)
sys.stdout.write(json.dumps({"identifier": fields[0].decode(), "password": fields[1].decode()}))
' >"$request_file"; then
        rm -f "$request_file" "$response_file"
        echo "auth: could not encode login request" >&2
        return 1
    fi

    http_code=$(curl -sS -o "$response_file" -w '%{http_code}' \
        -H 'Content-Type: application/json' \
        --data-binary "@$request_file" \
        "$AUTH_BASE_URL/auth/login") || {
        rm -f "$request_file" "$response_file"
        echo "auth: login request failed" >&2
        return 1
    }

    if [[ "$http_code" != 2* ]]; then
        rm -f "$request_file" "$response_file"
        echo "auth: login failed (HTTP $http_code)" >&2
        return 1
    fi

    if ! IFS=$'\t' read -r ACCESS_TOKEN REFRESH_TOKEN < <(python3 - "$response_file" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as response:
        payload = json.load(response)
    access = payload["access_token"]
    refresh = payload["refresh_token"]
    if not isinstance(access, str) or not access or not isinstance(refresh, str) or not refresh:
        raise ValueError
except (OSError, ValueError, KeyError, json.JSONDecodeError, TypeError):
    raise SystemExit(1)

print(f"{access}\t{refresh}")
PY
    ); then
        rm -f "$request_file" "$response_file"
        echo "auth: login returned malformed JSON" >&2
        return 1
    fi
    export ACCESS_TOKEN REFRESH_TOKEN

    rm -f "$request_file" "$response_file"
}

_auth_refresh_request() {
    local request_file response_file http_code
    request_file=$(mktemp) || {
        echo "auth: could not create a temporary request file" >&2
        return 1
    }
    response_file=$(mktemp) || {
        rm -f "$request_file"
        echo "auth: could not create a temporary response file" >&2
        return 1
    }
    chmod 600 "$request_file" "$response_file"

    if ! printf '%s' "$REFRESH_TOKEN" | python3 -c '
import json
import sys

token = sys.stdin.read()
if not token:
    raise SystemExit(1)
print(json.dumps({"refresh_token": token}), end="")
' >"$request_file"; then
        rm -f "$request_file" "$response_file"
        echo "auth: could not encode refresh request" >&2
        return 1
    fi

    http_code=$(curl -sS -o "$response_file" -w '%{http_code}' \
        -H 'Content-Type: application/json' \
        --data-binary "@$request_file" \
        "$AUTH_BASE_URL/auth/refresh") || {
        rm -f "$request_file" "$response_file"
        echo "auth: refresh request failed" >&2
        return 1
    }

    if [[ "$http_code" != 2* ]]; then
        rm -f "$request_file" "$response_file"
        echo "auth: refresh failed (HTTP $http_code)" >&2
        return 1
    fi

    if ! IFS=$'\t' read -r ACCESS_TOKEN REFRESH_TOKEN < <(python3 - "$response_file" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as response:
        payload = json.load(response)
    access = payload["access_token"]
    refresh = payload["refresh_token"]
    if not isinstance(access, str) or not access or not isinstance(refresh, str) or not refresh:
        raise ValueError
except (OSError, ValueError, KeyError, json.JSONDecodeError, TypeError):
    raise SystemExit(1)

print(f"{access}\t{refresh}")
PY
    ); then
        rm -f "$request_file" "$response_file"
        echo "auth: refresh returned malformed JSON" >&2
        return 1
    fi
    export ACCESS_TOKEN REFRESH_TOKEN

    rm -f "$request_file" "$response_file"
}

auth() {
    _auth_require_tools || return 1

    case "${1:-}" in
        login)
            local identifier password
            read -r -p 'Username/email: ' identifier || return 1
            read -r -s -p 'Password: ' password || return 1
            printf '\n' >&2
            _auth_login_request "$identifier" "$password"
            local result=$?
            unset password
            (( result == 0 )) || return "$result"
            if (( _AUTH_PERSISTENT_SHELL )); then
                echo 'auth: login successful; tokens exported in this shell'
            else
                echo 'auth: login successful; source this command to retain tokens in your shell'
            fi
            ;;
        refresh)
            if [[ -z "${REFRESH_TOKEN:-}" ]]; then
                echo 'auth: REFRESH_TOKEN is not set' >&2
                return 1
            fi
            _auth_refresh_request || return 1
            if (( _AUTH_PERSISTENT_SHELL )); then
                echo 'auth: refresh successful; tokens replaced in this shell'
            else
                echo 'auth: refresh successful; source this command to retain tokens in your shell'
            fi
            ;;
        status)
            local access_status='missing' refresh_status='missing'
            [[ -n "${ACCESS_TOKEN:-}" ]] && access_status='present'
            [[ -n "${REFRESH_TOKEN:-}" ]] && refresh_status='present'
            echo "ACCESS_TOKEN: $access_status"
            echo "REFRESH_TOKEN: $refresh_status"

            if [[ "$access_status" == present ]]; then
                local status_code
                status_code=$(curl -sS -o /dev/null -w '%{http_code}' \
                    -H "Authorization: Bearer $ACCESS_TOKEN" \
                    "$AUTH_BASE_URL/api/v1/problems") || {
                    echo 'access token verification: request failed' >&2
                    return 1
                }
                if [[ "$status_code" == 2* ]]; then
                    echo 'access token verification: valid'
                elif [[ "$status_code" == 401 ]]; then
                    echo 'access token verification: expired or invalid'
                else
                    echo "access token verification: HTTP $status_code"
                fi
            fi
            ;;
        *)
            echo 'Usage: source scripts/auth.sh {login|refresh|status}' >&2
            return 2
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" || $# -gt 0 ]]; then
    auth "$@"
fi
