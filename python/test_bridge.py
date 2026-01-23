#!/usr/bin/env python3
"""
Test script for Python API Bridge
==================================
Verifies that the api_bridge.py works correctly for Phase 2 validation.
"""

import sys
import json
import subprocess
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_result(test_name: str, passed: bool, message: str = ""):
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {status} {test_name}")
    if message and not passed:
        print(f"       {YELLOW}{message}{RESET}")

def send_command(proc, command: dict) -> dict:
    """Send a command to the bridge and get response."""
    cmd_str = json.dumps(command) + '\n'
    proc.stdin.write(cmd_str)
    proc.stdin.flush()
    
    # Read response (may include progress updates, find the actual response)
    while True:
        line = proc.stdout.readline().strip()
        if line:
            response = json.loads(line)
            # Skip progress and ready messages
            if response.get('type') not in ['progress', 'ready']:
                return response

def main():
    print(f"\n{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}  Phase 2: Python Bridge Test Suite{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}\n")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    bridge_script = script_dir / 'api_bridge.py'
    
    if not bridge_script.exists():
        print(f"{RED}Error: api_bridge.py not found at {bridge_script}{RESET}")
        sys.exit(1)
    
    tests_passed = 0
    tests_total = 0
    
    print(f"{BOLD}Starting Python bridge process...{RESET}\n")
    
    try:
        # Start the bridge process
        proc = subprocess.Popen(
            [sys.executable, str(bridge_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(script_dir),
            env={**dict(__import__('os').environ), 'PYTHONUNBUFFERED': '1'}
        )
        
        # Wait for ready signal
        ready_line = proc.stdout.readline().strip()
        ready_response = json.loads(ready_line)
        
        # Test 1: Ready signal
        tests_total += 1
        test_passed = ready_response.get('type') == 'ready' and ready_response.get('status') == 'initialized'
        if test_passed:
            tests_passed += 1
        print_result("Bridge initialization (ready signal)", test_passed, 
                    f"Got: {ready_response}" if not test_passed else "")
        
        # Test 2: Ping command
        tests_total += 1
        response = send_command(proc, {"action": "ping"})
        test_passed = response.get('success') == True and response.get('message') == 'pong'
        if test_passed:
            tests_passed += 1
        print_result("Ping command", test_passed,
                    f"Got: {response}" if not test_passed else "")
        
        # Test 3: Get status
        tests_total += 1
        response = send_command(proc, {"action": "get_status"})
        test_passed = response.get('success') == True and response.get('isRunning') == False
        if test_passed:
            tests_passed += 1
        print_result("Get status command", test_passed,
                    f"Got: {response}" if not test_passed else "")
        
        # Test 4: Check Ollama
        tests_total += 1
        response = send_command(proc, {"action": "check_ollama"})
        test_passed = response.get('success') == True
        if test_passed:
            tests_passed += 1
        ollama_status = "running" if response.get('running') else "not running"
        print_result(f"Check Ollama (Ollama is {ollama_status})", test_passed,
                    f"Got: {response}" if not test_passed else "")
        
        # Test 5: Get LLM info
        tests_total += 1
        response = send_command(proc, {"action": "get_llm_info"})
        test_passed = response.get('success') == True
        if test_passed:
            tests_passed += 1
        print_result("Get LLM info command", test_passed,
                    f"Got: {response}" if not test_passed else "")
        
        # Test 6: Unknown action
        tests_total += 1
        response = send_command(proc, {"action": "unknown_action"})
        test_passed = response.get('success') == False and 'Unknown action' in response.get('error', '')
        if test_passed:
            tests_passed += 1
        print_result("Unknown action error handling", test_passed,
                    f"Got: {response}" if not test_passed else "")
        
        # Test 7: Validate dataset with non-existent file
        tests_total += 1
        response = send_command(proc, {"action": "validate_dataset", "path": "/nonexistent/file.csv"})
        test_passed = response.get('success') == False
        if test_passed:
            tests_passed += 1
        print_result("Validate dataset (non-existent file)", test_passed,
                    f"Got: {response}" if not test_passed else "")
        
        # Test 8: Stop command
        tests_total += 1
        response = send_command(proc, {"action": "stop"})
        test_passed = response.get('success') == True
        if test_passed:
            tests_passed += 1
        print_result("Stop command", test_passed,
                    f"Got: {response}" if not test_passed else "")
        
        # Clean up
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=5)
        
    except Exception as e:
        print(f"\n{RED}Error during testing: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print summary
    print(f"\n{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    if tests_passed == tests_total:
        print(f"{GREEN}{BOLD}  All tests passed! ({tests_passed}/{tests_total}){RESET}")
    else:
        print(f"{YELLOW}{BOLD}  Tests passed: {tests_passed}/{tests_total}{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}\n")
    
    # Return exit code
    sys.exit(0 if tests_passed == tests_total else 1)

if __name__ == "__main__":
    main()
