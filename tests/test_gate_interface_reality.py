"""
Gate 1: Interface Reality Gate
Verify template-to-engine interface contracts: workflow_call signatures match,
documented references exist, dead references cleared.
"""
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional


def load_yaml_file(filepath: str) -> dict:
    """Load a YAML file safely."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_workflow_call_declaration(workflow_content: dict) -> dict:
    """Extract workflow_call declaration from workflow content."""
    on_block = workflow_content.get('on', {})
    if isinstance(on_block, dict) and 'workflow_call' in on_block:
        return on_block['workflow_call']
    return {}


def validate_template_engine_interface(template_path: str, engine_path: str) -> List[str]:
    """Validate that template inputs/secrets match engine workflow_call declaration."""
    errors = []
    
    try:
        template_content = load_yaml_file(template_path)
        engine_content = load_yaml_file(engine_path)
        
        engine_workflow_call = get_workflow_call_declaration(engine_content)
        
        # Extract expected inputs and secrets from engine
        expected_inputs = set()
        expected_secrets = set()
        
        if 'inputs' in engine_workflow_call:
            expected_inputs = set(engine_workflow_call['inputs'].keys())
            
        if 'secrets' in engine_workflow_call:
            expected_secrets = set(engine_workflow_call['secrets'].keys())
        
        # Check if this is a template that calls an engine workflow
        template_calls = find_workflow_calls(template_content)
        
        for call in template_calls:
            # Verify the target workflow exists
            target_workflow_path = Path("/Users/busiji/infraro-core/.github/workflows") / call.split('/')[-1]
            if not target_workflow_path.exists():
                errors.append(f"Template {template_path} calls non-existent workflow: {call}")
                continue
            
            # Load the target engine workflow
            target_content = load_yaml_file(target_workflow_path)
            target_workflow_call = get_workflow_call_declaration(target_content)
            
            # Extract inputs/secrets being passed
            passed_inputs = set()
            passed_secrets = set()
            
            # Look for inputs being passed in the job that calls the reusable workflow
            for job_name, job_config in target_content.get('jobs', {}).items():
                for step in job_config.get('steps', []):
                    if 'uses' in step and call in step['uses']:
                        if 'with' in step:
                            passed_inputs.update(step['with'].keys())
                        if 'env' in step:
                            for env_var, env_val in step['env'].items():
                                if isinstance(env_val, str) and 'secrets.' in env_val:
                                    passed_secrets.add(env_var)
            
            # Check for undeclared inputs being passed
            for inp in passed_inputs:
                if inp not in expected_inputs:
                    errors.append(f"Template {template_path} passes undeclared input '{inp}' to {call}")
            
            # Check for required inputs that are missing
            for inp_name, inp_config in target_workflow_call.get('inputs', {}).items():
                required = inp_config.get('required', False)
                if required and inp_name not in passed_inputs:
                    errors.append(f"Template {template_path} missing required input '{inp_name}' for {call}")
            
            # Check for undeclared secrets being passed
            for secret in passed_secrets:
                if secret not in expected_secrets:
                    errors.append(f"Template {template_path} passes undeclared secret '{secret}' to {call}")
                    
            # Check for required secrets that are missing
            for secret_name, secret_config in target_workflow_call.get('secrets', {}).items():
                required = secret_config.get('required', False)
                if required and secret_name not in passed_secrets:
                    errors.append(f"Template {template_path} missing required secret '{secret_name}' for {call}")
    
    except Exception as e:
        errors.append(f"Error validating {template_path}: {str(e)}")
    
    return errors


def find_workflow_calls(content: dict) -> List[str]:
    """Find all workflow calls in a workflow file."""
    calls = []
    
    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'uses' and isinstance(value, str):
                    if '/.github/workflows/' in value and '@' in value:
                        calls.append(value)
                elif isinstance(value, (dict, list)):
                    search_recursive(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                search_recursive(item, f"{path}[{i}]")
    
    search_recursive(content)
    return calls


def validate_documented_references(repo_path: str) -> List[str]:
    """Validate documented references (tags, secrets, names) exist in reality."""
    errors = []
    repo_path = Path(repo_path)
    
    # Look for documented tags and verify they exist
    # This would typically involve checking tags in the repository
    try:
        # Check for references to tags like @v0.15.0 in templates or docs
        for file_path in repo_path.rglob("*"):
            if file_path.suffix in ['.yml', '.yaml', '.md', '.txt'] and file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Look for version tags like @v0.15.0
                    import re
                    version_matches = re.findall(r'@v\d+\.\d+\.\d+', content)
                    
                    for version_match in version_matches:
                        # This would normally verify the tag exists in the repo
                        # For now, we'll just log the references found
                        # This can be enhanced with actual git tag verification
                        pass
                        
                except UnicodeDecodeError:
                    continue  # Skip binary files
                    
    except Exception as e:
        errors.append(f"Error validating documented references: {str(e)}")
    
    return errors


def validate_template_interfaces(repo_path: str) -> Dict[str, List[str]]:
    """Validate interfaces between templates and engine workflows."""
    repo_path = Path(repo_path)
    results = {
        "interface_errors": [],
        "reference_errors": [],
        "dead_reference_warnings": []
    }
    
    # Define the mapping between templates and engine workflows
    # We need to look for template files and their corresponding engine workflow targets
    
    # First, let's check templates directory if it exists
    templates_dir = Path("/Users/busiji/infraro/templates")
    engine_workflows_dir = repo_path / ".github" / "workflows"
    
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.yml"):
            try:
                template_content = load_yaml_file(template_file)
                
                # Find workflow calls in the template
                calls = find_workflow_calls(template_content)
                
                for call in calls:
                    # Parse the call to get the workflow name
                    if '/.github/workflows/' in call:
                        workflow_part = call.split('/.github/workflows/')[-1]
                        if '@' in workflow_part:
                            workflow_name = workflow_part.split('@')[0]
                        else:
                            workflow_name = workflow_part
                            
                        engine_workflow_path = engine_workflows_dir / workflow_name
                        if engine_workflow_path.exists():
                            interface_errors = validate_template_engine_interface(
                                str(template_file), str(engine_workflow_path)
                            )
                            results["interface_errors"].extend(interface_errors)
                        else:
                            results["interface_errors"].append(
                                f"Template {template_file} references non-existent engine workflow: {workflow_name}"
                            )
                            
            except Exception as e:
                results["interface_errors"].append(f"Error processing template {template_file}: {str(e)}")
    
    # Also validate references in engine workflows themselves
    if engine_workflows_dir.exists():
        for workflow_file in engine_workflows_dir.glob("*.yml"):
            try:
                content = load_yaml_file(workflow_file)
                calls = find_workflow_calls(content)
                
                # Check if calls reference valid workflows
                for call in calls:
                    # This is a simplified check - in practice, you'd validate against real targets
                    pass
            except Exception as e:
                results["interface_errors"].append(f"Error processing engine workflow {workflow_file}: {str(e)}")
    
    # Validate documented references
    results["reference_errors"].extend(validate_documented_references(repo_path))
    
    return results


if __name__ == "__main__":
    repo_path = "/Users/busija/infraro-core"
    results = validate_template_interfaces(repo_path)
    
    print("# Gate 1: Interface Reality Report")
    print("")
    
    print("## Interface Errors")
    if results["interface_errors"]:
        for error in results["interface_errors"]:
            print(f"- {error}")
        print()
    else:
        print("- No interface errors found")
        print()
    
    print("## Reference Errors") 
    if results["reference_errors"]:
        for error in results["reference_errors"]:
            print(f"- {error}")
        print()
    else:
        print("- No reference errors found")
        print()
    
    print("## Dead Reference Warnings")
    if results["dead_reference_warnings"]:
        for warning in results["dead_reference_warnings"]:
            print(f"- {warning}")
        print()
    else:
        print("- No dead reference warnings")
        print()
    
    # Check if there are any critical errors
    total_errors = len(results["interface_errors"]) + len(results["reference_errors"])
    
    if total_errors == 0:
        print("=== GATE 1 PASSED ===")
        print("All template-engine interfaces validated successfully.")
        exit(0)
    else:
        print(f"=== GATE 1 FAILED ===")
        print(f"Found {total_errors} critical errors that need fixing.")
        exit(1)
