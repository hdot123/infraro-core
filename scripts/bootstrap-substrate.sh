#!/usr/bin/env bash

# Gate 4: Substrate Bootstrap Script
# One-click bootstrap for substrate manual entry machine automation
# Includes --dry-run option for verification

set -euo pipefail

# Configuration
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR")"

# Default values
DRY_RUN=false
VERBOSE=false
TARGET_SUBSTRATE_FEATURES=("substrate-map-and-manual" "substrate-gate-suite")

# Help function
print_help() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

One-click bootstrap script for substrate manual entry machine automation.

OPTIONS:
    --dry-run       Perform a dry run without making changes
    --verbose, -v   Enable verbose output
    --help, -h      Show this help message

EXAMPLES:
    $SCRIPT_NAME --dry-run              # Verify what would be done
    $SCRIPT_NAME                        # Run the bootstrap
EOF
}

# Log function
log() {
    if [[ "$VERBOSE" == true ]]; then
        echo "[INFO] $*" >&2
    fi
}

# Dry run log function
dry_run_log() {
    if [[ "$DRY_RUN" == true ]]; then
        echo "[DRY-RUN] $*" >&2
    else
        echo "[RUNNING] $*" >&2
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        echo "Error: git is not installed" >&2
        exit 1
    fi
    
    # Check if Python is available (needed for tests)
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 is not installed" >&2
        exit 1
    fi
    
    # Check if pip is available (needed for uv)
    if ! command -v pip &> /dev/null; then
        echo "Warning: pip is not installed (may be needed for uv)" >&2
    fi
    
    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        log "uv is not installed, will try to install"
    fi
    
    log "Prerequisites check completed"
}

# Bootstrap substrate manual entry
bootstrap_manual_entry() {
    log "Bootstrapping substrate manual entry..."
    
    dry_run_log "Creating substrate manual entry structure"
    
    # In a real implementation, this would create the manual entry
    # and initialize the substrate components
    if [[ "$DRY_RUN" == false ]]; then
        # Create directories if they don't exist
        mkdir -p "$REPO_ROOT/docs"
        mkdir -p "$REPO_ROOT/tests"
        
        # Create placeholder for substrate manual
        if [[ ! -f "$REPO_ROOT/docs/substrate-manual.md" ]]; then
            cat > "$REPO_ROOT/docs/substrate-manual.md" << 'EOF'
# Substrate Manual

This is the substrate manual entry point. 

## Components

- Memory/Knowledge Systems
- Factory Runtime  
- Notification Chain (Webhook)
- Runner Fleet
- Legacy Template Repositories
- Legacy Infrastructure
- Linear Workspace
- Basic Checks (Probes)

## Operation Guide

Follow the procedures outlined in substrate-map.md for operating substrate components.
EOF
            log "Created substrate manual entry"
        fi
    else
        log "Would create substrate manual entry structure"
    fi
}

# Verify substrate readiness
verify_readiness() {
    log "Verifying substrate readiness..."
    
    # Check if substrate-map exists
    if [[ -f "$REPO_ROOT/docs/substrate-map.md" ]]; then
        log "substrate-map.md exists"
    else
        echo "Warning: substrate-map.md not found" >&2
    fi
    
    # Check if basic tests exist
    if [[ -d "$REPO_ROOT/tests" ]]; then
        local test_count
        test_count=$(find "$REPO_ROOT/tests" -name "test_gate*.py" 2>/dev/null | wc -l)
        log "Found $test_count substrate gate tests"
    else
        log "No tests directory found"
    fi
    
    # Try to run a basic check
    if command -v python3 &> /dev/null; then
        if [[ -d "$REPO_ROOT/tests" ]]; then
            local gate_tests
            gate_tests=$(find "$REPO_ROOT/tests" -name "test_gate*.py" 2>/dev/null | head -5)
            if [[ -n "$gate_tests" ]]; then
                log "Found gate tests, verifying syntax:"
                while IFS= read -r test_file; do
                    if [[ -n "$test_file" ]]; then
                        dry_run_log "Syntax check: $(basename "$test_file")"
                        if [[ "$DRY_RUN" == false ]]; then
                            python3 -m py_compile "$test_file" 2>/dev/null && log "Syntax OK: $(basename "$test_file")" || echo "Syntax error in $test_file" >&2
                        fi
                    fi
                done <<< "$gate_tests"
            fi
        fi
    fi
}

# Main execution function
main() {
    log "Starting substrate bootstrap..."
    
    check_prerequisites
    bootstrap_manual_entry
    verify_readiness
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "Dry run completed successfully. No changes were made." >&2
    else
        echo "Bootstrap completed successfully!" >&2
    fi
    
    log "Bootstrap process finished"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            print_help
            exit 1
            ;;
    esac
done

# Run main function
main
