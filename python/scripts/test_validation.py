#!/usr/bin/env python3
"""
Test script for phase dependency validation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.api_bridge import APIBridge


def test_validation():
    """Test phase dependency validation"""

    print('=' * 60)
    print('Testing Phase Dependency Validation')
    print('=' * 60)

    # Create test dataset path
    dataset_path = Path(__file__).parent.parent / 'python' / 'data' / 'dataset.csv'

    # Initialize bridge
    bridge = APIBridge(str(dataset_path))

    # Test each phase
    for phase in range(1, 9):
        print(f'\n{"─" * 60}')
        print(f'Testing Phase {phase}')
        print('─' * 60)

        result = bridge.execute({'action': 'validate_phase_dependencies', 'phase': phase})

        if result.get('success'):
            print('✓ API call succeeded')
            print(f'  Can run: {result.get("canRun")}')
            print(f'  Valid: {result.get("valid")}')

            if result.get('missingPhases'):
                print(f'  Missing phases: {result.get("missingPhases")}')

            if result.get('missingColumns'):
                print(f'  Missing columns: {result.get("missingColumns")}')

            if result.get('missingFiles'):
                print(f'  Missing files: {result.get("missingFiles")}')

            if result.get('error'):
                print(f'  Error message: {result.get("error")}')
        else:
            print(f'✗ API call failed: {result.get("error")}')

    print('\n' + '=' * 60)
    print('Test scenarios')
    print('=' * 60)

    # Scenario 1: Fresh dataset (only basic columns)
    print('\n📋 Scenario 1: Fresh dataset with only basic columns')
    print('   Expected: Phase 1 should pass, others should fail')

    # Scenario 2: After running Phase 1-4
    print('\n📋 Scenario 2: After running Phases 1-4')
    print('   Expected: Phases 1-4 should pass, others may fail if missing Phase 5')

    # Scenario 3: All phases complete
    print('\n📋 Scenario 3: All phases complete')
    print('   Expected: All phases should pass')

    print('\n' + '=' * 60)
    print('Validation system ready!')
    print('=' * 60)


if __name__ == '__main__':
    test_validation()
