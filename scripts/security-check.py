#!/usr/bin/env python3
"""
Security Check Script for Trade Analytics App
Scans for API keys and sensitive data before GitHub push
"""

import os
import re
import sys
from pathlib import Path

def scan_for_api_keys(directory="."):
    """Scan directory for potential API keys and sensitive data"""
    
    # Patterns to look for
    patterns = {
        'openai_api_key': r'sk-[a-zA-Z0-9]{48}',
        'google_api_key': r'AIza[0-9A-Za-z-_]{35}',
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'[0-9a-zA-Z/+]{40}',
        'generic_api_key': r'api_key\s*=\s*["\'][^"\']{20,}["\']',
        'password': r'password\s*=\s*["\'][^"\']+["\']',
        'secret': r'secret\s*=\s*["\'][^"\']+["\']',
        'token': r'token\s*=\s*["\'][^"\']+["\']',
    }
    
    # Files to skip
    skip_files = {
        '.git', '.gitignore', '.env', 'env.example', 
        'node_modules', '__pycache__', '.DS_Store',
        '*.pyc', '*.log', '*.tmp'
    }
    
    # Extensions to scan
    scan_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml', '.txt', '.md'}
    
    issues_found = []
    
    for root, dirs, files in os.walk(directory):
        # Skip directories that should be ignored
        dirs[:] = [d for d in dirs if d not in skip_files]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip files that should be ignored
            if any(skip in str(file_path) for skip in skip_files):
                continue
                
            # Only scan certain file types
            if file_path.suffix not in scan_extensions:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern_name, pattern in patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = content.split('\n')[line_num - 1].strip()
                        
                        issues_found.append({
                            'file': str(file_path),
                            'line': line_num,
                            'pattern': pattern_name,
                            'match': match.group()[:20] + '...' if len(match.group()) > 20 else match.group(),
                            'line_content': line_content[:100] + '...' if len(line_content) > 100 else line_content
                        })
                        
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
    
    return issues_found

def check_gitignore():
    """Check if .gitignore contains necessary entries"""
    gitignore_path = Path('.gitignore')
    
    if not gitignore_path.exists():
        return False, "No .gitignore file found"
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    required_entries = [
        '.env', '*.env', 'config.py', 'credentials.py', 
        'secrets.py', 'api_keys.py', '__pycache__', '.DS_Store'
    ]
    
    missing_entries = []
    for entry in required_entries:
        if entry not in content:
            missing_entries.append(entry)
    
    return len(missing_entries) == 0, missing_entries

def main():
    """Main security check function"""
    print("🔒 Running Security Check for Trade Analytics App")
    print("=" * 50)
    
    # Check for API keys
    print("\n🔍 Scanning for API keys and sensitive data...")
    issues = scan_for_api_keys()
    
    if issues:
        print(f"\n❌ Found {len(issues)} potential security issues:")
        print("-" * 50)
        
        for issue in issues:
            print(f"File: {issue['file']}")
            print(f"Line: {issue['line']}")
            print(f"Type: {issue['pattern']}")
            print(f"Match: {issue['match']}")
            print(f"Content: {issue['line_content']}")
            print("-" * 30)
        
        print("\n🚨 SECURITY WARNING:")
        print("Please remove or secure these API keys before pushing to GitHub!")
        print("Use environment variables instead.")
        
        return False
    else:
        print("✅ No API keys or sensitive data found!")
    
    # Check .gitignore
    print("\n🔍 Checking .gitignore file...")
    gitignore_ok, missing_entries = check_gitignore()
    
    if gitignore_ok:
        print("✅ .gitignore file is properly configured!")
    else:
        print(f"⚠️  .gitignore missing entries: {missing_entries}")
        print("Consider adding these to your .gitignore file.")
    
    # Check for .env files
    print("\n🔍 Checking for .env files...")
    env_files = list(Path('.').glob('.env*'))
    
    if env_files:
        print(f"⚠️  Found .env files: {[f.name for f in env_files]}")
        print("Make sure these are in your .gitignore!")
    else:
        print("✅ No .env files found in root directory.")
    
    print("\n" + "=" * 50)
    print("🔒 Security check completed!")
    
    if issues:
        print("❌ Please fix security issues before pushing to GitHub.")
        return False
    else:
        print("✅ Your code is ready for GitHub!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

