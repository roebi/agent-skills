# curl Reference

curl transfers data to and from servers using URLs. It supports HTTP, HTTPS, FTP, and more.

## Basic usage

```bash
curl https://example.com                  # GET, print to stdout
curl -o output.html https://example.com   # Save to file
curl -O https://example.com/file.zip      # Save with remote filename
curl -L https://example.com               # Follow redirects
curl -fsSL https://example.com            # Fail silently on error,
                                          # suppress progress, follow redirects
                                          # (common pattern for install scripts)
```

## HTTP methods

```bash
# GET (default)
curl https://api.example.com/resource

# POST with JSON body
curl -X POST https://api.example.com/endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# POST with form data
curl -X POST https://example.com/form \
  -F "field=value" \
  -F "file=@/path/to/file"

# PUT
curl -X PUT https://api.example.com/resource/1 \
  -H "Content-Type: application/json" \
  -d '{"key": "updated"}'

# PATCH
curl -X PATCH https://api.example.com/resource/1 \
  -H "Content-Type: application/json" \
  -d '{"key": "partial"}'

# DELETE
curl -X DELETE https://api.example.com/resource/1
```

## Headers & authentication

```bash
# Custom header
curl -H "Accept: application/json" https://api.example.com

# Bearer token
curl -H "Authorization: Bearer $TOKEN" https://api.example.com

# Basic auth
curl -u username:password https://api.example.com

# Multiple headers
curl -H "Content-Type: application/json" \
     -H "X-Custom-Header: value" \
     https://api.example.com

# Send cookies
curl -b "session=abc123" https://example.com
curl -b cookies.txt https://example.com     # From file

# Save cookies
curl -c cookies.txt https://example.com
```

## Inspect responses

```bash
curl -I https://example.com               # HEAD — response headers only
curl -v https://example.com               # Verbose — full request + response
curl -s https://example.com               # Silent — suppress progress/errors
curl -w "\n%{http_code}\n" https://example.com  # Print HTTP status code
curl -w "%{time_total}s\n" https://example.com  # Print total time
```

## Download

```bash
# Download with progress bar
curl -# -o file.zip https://example.com/file.zip

# Resume interrupted download
curl -C - -o file.zip https://example.com/file.zip

# Download multiple files
curl -O https://example.com/file1.zip \
     -O https://example.com/file2.zip
```

## Timeouts & retries

```bash
curl --connect-timeout 5 https://example.com     # Connection timeout (seconds)
curl --max-time 30 https://example.com           # Max total time (seconds)
curl --retry 3 https://example.com               # Retry on transient errors
curl --retry 3 --retry-delay 2 https://example.com
```

## TLS / SSL

```bash
curl -k https://self-signed.example.com   # Skip SSL verification (insecure)
curl --cacert ca.crt https://example.com  # Use custom CA certificate
curl --cert client.crt --key client.key https://example.com  # Client cert
```

## Data from files & environment

```bash
# Send file content as body
curl -X POST -d @payload.json \
  -H "Content-Type: application/json" \
  https://api.example.com

# Use environment variable in data
curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$API_TOKEN\"}" \
  https://api.example.com
```

## Useful combinations

```bash
# GET and parse JSON with jq
curl -fsSL https://api.example.com/data | jq '.items[0].name'

# Health check: return 0 if HTTP 200, 1 otherwise
curl -fsS --head https://example.com > /dev/null && echo OK || echo FAIL

# Download and extract archive in one step
curl -fsSL https://example.com/archive.tar.gz | tar -xzf -
```
