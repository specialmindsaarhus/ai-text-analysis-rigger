# Git Snapshot Guide

## Current Status
Repository initialized with initial snapshot (commit 9432d13)

## How to Create Snapshots

### 1. Check Status
See what files have changed:
```bash
git status
```

### 2. Create a New Snapshot
When you've made changes you want to save:
```bash
git add .
git commit -m "Brief description of changes"
```

### 3. View Snapshot History
```bash
git log --oneline
```

### 4. Restore to a Previous Snapshot
```bash
# View available snapshots
git log --oneline

# Restore to specific snapshot (use commit hash from log)
git checkout [commit-hash]

# Return to latest
git checkout master
```

## Example Workflow

```bash
# Make some changes to files...

# Check what changed
git status

# Save snapshot
git add .
git commit -m "Added new feature X"

# Later, if you need to go back
git log --oneline
git checkout [commit-hash]
```
