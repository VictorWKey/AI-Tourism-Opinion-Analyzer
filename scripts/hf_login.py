#!/usr/bin/env python3
"""
Simple script to log in to Hugging Face Hub.

INSTRUCTIONS:
1. Create account at https://huggingface.co
2. Go to https://huggingface.co/settings/tokens
3. Create a new token with WRITE permission
4. Run this script and paste your token when prompted
"""

from huggingface_hub import login, whoami
import sys

def main():
    print("=" * 60)
    print("  Hugging Face Login")
    print("=" * 60)
    print("\n📝 Get your token from:")
    print("   https://huggingface.co/settings/tokens")
    print("\n⚠️  Make sure your token has WRITE permission!")
    print()
    
    try:
        # Check if already logged in
        try:
            user_info = whoami()
            print(f"✅ Already logged in as: {user_info['name']}")
            response = input("\n   Do you want to login again? (y/n): ")
            if response.lower() != 'y':
                return
        except:
            pass
        
        # Prompt for token
        token = input("\n🔑 Paste your Hugging Face token here: ").strip()
        
        if not token:
            print("❌ No token provided!")
            sys.exit(1)
        
        # Login
        print("\n🔄 Logging in...")
        login(token=token, add_to_git_credential=True)
        
        # Verify login
        user_info = whoami()
        print(f"\n✅ Successfully logged in as: {user_info['name']}")
        print(f"   Email: {user_info.get('email', 'N/A')}")
        print(f"\n💾 Token saved. You won't need to login again.")
        print("\n🎉 You can now run the upload script:")
        print("   python\\venv\\Scripts\\python.exe scripts\\upload_models_to_hf.py")
        
    except Exception as e:
        print(f"\n❌ Login failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
