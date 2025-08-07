#!/usr/bin/env python3
"""
Deployment setup script for RAG system
Handles SQLite version compatibility issues
"""

import sys
import os

def fix_sqlite_issue():
    """Fix SQLite version compatibility issue for ChromaDB"""
    try:
        # Import pysqlite3 and replace the default sqlite3
        import pysqlite3
        sys.modules['sqlite3'] = pysqlite3
        print("✅ SQLite compatibility fix applied")
    except ImportError:
        print("⚠️  pysqlite3-binary not found. Please install it: pip install pysqlite3-binary")
        return False
    return True

def check_sqlite_version():
    """Check if SQLite version is compatible"""
    try:
        import sqlite3
        version = sqlite3.sqlite_version
        print(f"📊 SQLite version: {version}")
        
        # Parse version string (e.g., "3.35.0")
        major, minor, patch = map(int, version.split('.'))
        version_num = major * 1000000 + minor * 1000 + patch
        
        if version_num >= 3035000:  # 3.35.0
            print("✅ SQLite version is compatible with ChromaDB")
            return True
        else:
            print("❌ SQLite version is too old for ChromaDB")
            return False
    except Exception as e:
        print(f"❌ Error checking SQLite version: {e}")
        return False

if __name__ == "__main__":
    print("🔧 RAG System Deployment Setup")
    print("=" * 40)
    
    # Check current SQLite version
    if not check_sqlite_version():
        print("\n🔧 Attempting to fix SQLite compatibility...")
        if fix_sqlite_issue():
            check_sqlite_version()
        else:
            print("\n❌ Please install pysqlite3-binary:")
            print("   pip install pysqlite3-binary")
            sys.exit(1)
    
    print("\n✅ Deployment setup complete!") 