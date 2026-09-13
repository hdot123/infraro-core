"""
Gate 0: Coverage Completeness Invariant Test
Ensures every directory/asset in the repositories falls under at least one checker's scanning domain.
Unowned areas generate exemption registration list (exemption = registration + owner).
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Set


def get_all_top_level_paths(repo_path: str) -> Set[str]:
    """Get all top-level paths/assets in the repository."""
    repo = Path(repo_path)
    paths = set()
    
    for item in repo.iterdir():
        if item.is_dir():
            paths.add(item.name + "/")
        else:
            paths.add(item.name)
    
    return paths


def get_boundary_scanner_coverage(repo_path: str) -> Set[str]:
    """Get paths covered by boundary scanners (actionlint, etc.)."""
    covered = set()
    
    # Get GitHub Actions workflows
    workflows_dir = Path(repo_path) / ".github" / "workflows"
    if workflows_dir.exists():
        for wf_file in workflows_dir.glob("*.yml"):
            covered.add(f".github/workflows/{wf_file.name}")
        for wf_file in workflows_dir.glob("*.yaml"):
            covered.add(f".github/workflows/{wf_file.name}")
    
    # Get GitHub Actions composite actions
    actions_dir = Path(repo_path) / ".github" / "actions"
    if actions_dir.exists():
        for action_dir in actions_dir.iterdir():
            if action_dir.is_dir():
                covered.add(f".github/actions/{action_dir.name}/")
                for action_file in action_dir.rglob("*"):
                    if action_file.is_file():
                        rel_path = action_file.relative_to(Path(repo_path))
                        covered.add(str(rel_path))
    
    # Get src files
    src_dir = Path(repo_path) / "src"
    if src_dir.exists():
        covered.add("src/")
        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(Path(repo_path))
                covered.add(str(rel_path))
    
    # Get tests
    tests_dir = Path(repo_path) / "tests"
    if tests_dir.exists():
        covered.add("tests/")
        for test_file in tests_dir.rglob("*"):
            if test_file.is_file():
                rel_path = test_file.relative_to(Path(repo_path))
                covered.add(str(rel_path))
                
    return covered


def get_existing_contract_test_coverage(repo_path: str) -> Set[str]:
    """Get paths covered by existing contract tests."""
    covered = set()
    
    # Contract tests typically cover specific files
    # Look for common testable files
    possible_contracts = [
        "pyproject.toml", "uv.lock", ".gitignore", "README.md", "LICENSE",
        "CHANGELOG.md", ".release-please-manifest.json", "release-please-config.json",
        "runner-tools.toml"
    ]
    
    for filename in possible_contracts:
        file_path = Path(repo_path) / filename
        if file_path.exists():
            covered.add(filename)
    
    # Get all .github files
    github_dir = Path(repo_path) / ".github"
    if github_dir.exists():
        for gh_file in github_dir.rglob("*"):
            if gh_file.is_file():
                rel_path = gh_file.relative_to(Path(repo_path))
                covered.add(str(rel_path))
    
    return covered


def identify_unowned_areas(repo_path: str) -> Dict[str, List[str]]:
    """Identify areas not covered by any scanner/checker."""
    all_paths = get_all_top_level_paths(repo_path)
    boundary_covered = get_boundary_scanner_coverage(repo_path)
    contract_covered = get_existing_contract_test_coverage(repo_path)
    
    # Union of all covered areas
    all_covered = boundary_covered.union(contract_covered)
    
    # Identify unowned areas
    unowned = []
    for path in all_paths:
        # Check if this path or any of its subdirectories are covered
        is_covered = False
        for covered_path in all_covered:
            if covered_path.startswith(path) or path.startswith(covered_path.rstrip('/')):
                is_covered = True
                break
        
        if not is_covered:
            unowned.append(path)
    
    # Special handling for known exemption areas
    exemptions = []
    potential_exemptions = []
    
    for path in unowned:
        if path.startswith("cf/") or path.startswith("webhook-scripts/"):
            potential_exemptions.append(path)
        else:
            exemptions.append(path)
    
    return {
        "unowned": exemptions,
        "potential_exemptions": potential_exemptions
    }


def generate_gate0_report(repo_path: str) -> str:
    """Generate a report for Gate 0 coverage completeness."""
    result = identify_unowned_areas(repo_path)
    
    report = []
    report.append("# Gate 0: Coverage Completeness Report")
    report.append("")
    report.append("## Summary")
    report.append(f"- Total top-level paths: {len(get_all_top_level_paths(repo_path))}")
    report.append(f"- Boundary scanner coverage: {len(get_boundary_scanner_coverage(repo_path))}")
    report.append(f"- Contract test coverage: {len(get_existing_contract_test_coverage(repo_path))}")
    report.append("")
    
    report.append("## Unowned Areas (Require Investigation)")
    if result["unowned"]:
        for path in result["unowned"]:
            report.append(f"- {path}")
    else:
        report.append("- None found")
    
    report.append("")
    report.append("## Potential Exemption Areas")
    report.append("(These may be designated as exempted areas after boundary feature ruling)")
    if result["potential_exemptions"]:
        for path in result["potential_exemptions"]:
            report.append(f"- {path}")
    else:
        report.append("- None found")
    
    return "\n".join(report)


if __name__ == "__main__":
    repo_path = "/Users/busiji/infraro-core"
    report = generate_gate0_report(repo_path)
    print(report)
    
    result = identify_unowned_areas(repo_path)
    
    # Print unowned areas for potential exemption registration
    if result["unowned"] or result["potential_exemptions"]:
        print("\n=== REGISTRATION NEEDED ===")
        print("The following areas need exemption registration:")
        for area in result["unowned"]:
            print(f"  - {area} (unowned, investigate)")
        for area in result["potential_exemptions"]:
            print(f"  - {area} (potential exemption - cf/, webhook-scripts/)")
        print("\nRegister these in exemption list with owner assignments.")
        
        # Fail the test if there are unowned areas
        exit(1)
    else:
        print("\n=== GATE 0 PASSED ===")
        print("All repository paths covered by at least one scanner/checker.")
        exit(0)
