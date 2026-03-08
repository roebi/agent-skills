# Bash Reference

## Filesystem — complete

### Navigate & inspect

```bash
pwd                              # Current directory
ls -la                           # List all files with details
ls -lah                          # Human-readable sizes
tree -L 2                        # Directory tree (2 levels)
tree -L 3 -I "node_modules"      # Exclude a directory
find /path -name "*.log"         # Find by filename pattern
find /path -type f -name "*.sh"  # Files only
find /path -mtime -1             # Modified in last 24 hours
find /path -size +100M           # Larger than 100 MB
find /path -name "*.log" -delete # Find and delete
du -sh /path                     # Size of a directory
du -sh /path/*                   # Size of each item inside
df -h                            # Disk usage per mount point
```

### Create, copy, move, delete

```bash
mkdir -p /path/to/dir            # Create dir (with parents)
touch file.txt                   # Create empty file
cp src dst                       # Copy file
cp -r src/ dst/                  # Copy directory recursively
cp -a src/ dst/                  # Copy preserving attributes
mv src dst                       # Move or rename
rm file.txt                      # Delete file
```

### Permissions & ownership

```bash
chmod +x file                    # Make executable
chmod 644 file                   # rw-r--r-- (file)
chmod 755 dir                    # rwxr-xr-x (directory)
chmod -R 755 dir/                # Recursive
chown user:group file            # Change owner and group
chown -R user:group dir/         # Recursive
ls -la                           # View permissions
stat file                        # Full file metadata
```

### Links

```bash
ln -s /target /link              # Create symbolic link
ln /target /hardlink             # Create hard link
readlink -f /link                # Resolve symlink to absolute path
ls -la | grep " -> "             # Show symlinks in listing
```

### Mounts

```bash
mount                            # List all active mounts
mount /dev/sdb1 /mnt/data        # Mount a device
umount /mnt/data                 # Unmount
lsblk                            # Block device tree
findmnt                          # Mount tree
df -h                            # Disk space per mount
```

### Archives & compression

```bash
tar -czf archive.tar.gz dir/     # Create gzip tar
tar -xzf archive.tar.gz          # Extract gzip tar
tar -xzf archive.tar.gz -C /dst  # Extract to specific dir
zip -r archive.zip dir/          # Create zip
unzip archive.zip                # Extract zip
unzip archive.zip -d /dst        # Extract to specific dir
```

### xargs — apply a command to many items

```bash
find /path -name "*.log" | xargs cat         # cat found files to stdout
find /path -name "*.py" | xargs grep "TODO"  # Search inside found files
cat list.txt | xargs -I{} cp {} /backup/     # Use {} as placeholder
```

---

## Install & update — complete

### APT (Debian / Ubuntu)

```bash
sudo apt update                  # Refresh package index
sudo apt upgrade -y              # Upgrade all installed packages
sudo apt install -y pkg          # Install a package
sudo apt remove pkg              # Remove (keep config)
sudo apt purge pkg               # Remove including config
sudo apt autoremove              # Remove unused dependencies
apt search keyword               # Search available packages
apt show pkg                     # Package details and dependencies
dpkg -l | grep pkg               # Check if package is installed
```

### pip (Python)

```bash
pip install pkg --break-system-packages
pip install -r requirements.txt --break-system-packages
pip install "pkg==1.2.3" --break-system-packages  # Pin version
pip list                         # Installed packages
pip show pkg                     # Package info and location
pip uninstall pkg                # Remove package
pip install --upgrade pkg --break-system-packages
```

### npm (Node.js)

```bash
npm install -g pkg               # Install globally
npm install pkg                  # Install locally (project)
npm install pkg@1.2.3            # Pin version
npm update                       # Update all local packages
npm list -g --depth=0            # Globally installed packages
npm uninstall -g pkg             # Remove global package
```

### Snap

```bash
sudo snap install pkg            # Install
sudo snap refresh                # Update all snaps
sudo snap refresh pkg            # Update specific snap
sudo snap remove pkg             # Remove
snap list                        # Installed snaps
```

### From a URL / install script

```bash
# Download and execute (review the script first)
curl -fsSL https://url/install.sh | bash

# Download, inspect, then run
curl -fsSL https://url/install.sh -o install.sh
cat install.sh                   # Inspect before running
bash install.sh
```

---

## Environment variables — complete

```bash
# View
env                              # All environment variables
printenv                         # Same as env
printenv VAR_NAME                # Single variable
echo $VAR_NAME                   # Print a variable

# Set (current shell only — lost when shell exits)
export VAR_NAME="value"
export PATH="$PATH:/new/path"    # Extend PATH

# Set only for a single command (does not affect shell)
VAR=value command

# Unset
unset VAR_NAME

# Check if a variable is set
[ -z "$VAR" ] && echo "not set" || echo "set to $VAR"

# Persist across sessions (add to shell profile)
echo 'export VAR_NAME="value"' >> ~/.bashrc
source ~/.bashrc                 # Reload profile immediately

# Load from a .env file
export $(grep -v '^#' .env | xargs)     # Simple method
set -a; source .env; set +a             # Handles multi-line values

# List all variables including shell functions
set
```

---

## Scripting patterns

### Error handling

```bash
#!/bin/bash
set -euo pipefail
# -e  exit on any error
# -u  treat unset variables as errors
# -o pipefail  pipe fails if any command in it fails

trap 'echo "Error on line $LINENO"' ERR
```

### Conditional logic

```bash
if [ -f "file.txt" ]; then
  echo "file exists"
elif [ -d "dir/" ]; then
  echo "dir exists"
else
  echo "neither"
fi

# One-liner
[ -f "file.txt" ] && echo "exists" || echo "not found"
```

### Loops

```bash
# Over items
for item in a b c; do
  echo "$item"
done

# Over files
for f in *.txt; do
  echo "Processing $f"
done

# While
while [ condition ]; do
  command
done

# With counter
for i in $(seq 1 10); do
  echo "Step $i"
done
```

### Functions

```bash
greet() {
  local name="$1"       # local scoping
  echo "Hello, $name"
}

greet "World"
```

### Process management

```bash
command &               # Run in background
jobs                    # List background jobs
fg %1                   # Bring job 1 to foreground
kill %1                 # Kill background job
kill -9 PID             # Force kill by PID
ps aux | grep name      # Find process by name
top                     # Interactive process viewer
htop                    # Better interactive viewer (if installed)
```
