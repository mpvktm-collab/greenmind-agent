# build_vector_stores.py
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.vector_store import VectorStoreManager
from config import Config

def main():
    print("=" * 60)
    print("BUILDING VECTOR STORES")
    print("=" * 60)
    
    # Initialize vector store manager
    print("\n1. Initializing VectorStoreManager...")
    manager = VectorStoreManager()
    
    # Build policies vector store
    print("\n2. Building Policies Vector Store...")
    print("-" * 40)
    policies_path = os.path.join(Config.DATA_DIRECTORY, "policies")
    policies_store_path = os.path.join(Config.VECTOR_STORE_PATH, "policies_store")
    
    if os.path.exists(policies_path):
        files = os.listdir(policies_path)
        print(f"Found {len(files)} files in policies folder")
        
        policies_store = manager.load_or_create_store(policies_store_path, policies_path)
        
        if policies_store:
            print("\n✓ Policies vector store created successfully!")
        else:
            print("\n✗ Failed to create policies vector store")
    else:
        print(f"Policies folder not found: {policies_path}")
    
    # Build effects vector store
    print("\n3. Building Effects Vector Store...")
    print("-" * 40)
    effects_path = os.path.join(Config.DATA_DIRECTORY, "effects")
    effects_store_path = os.path.join(Config.VECTOR_STORE_PATH, "effects_store")
    
    if os.path.exists(effects_path):
        files = os.listdir(effects_path)
        print(f"Found {len(files)} files in effects folder")
        
        effects_store = manager.load_or_create_store(effects_store_path, effects_path)
        
        if effects_store:
            print("\n✓ Effects vector store created successfully!")
        else:
            print("\n✗ Failed to create effects vector store")
    else:
        print(f"Effects folder not found: {effects_path}")
    
    print("\n" + "=" * 60)
    print("VECTOR STORE BUILD COMPLETE")
    print("=" * 60)
    print(f"\nVector stores saved to: {Config.VECTOR_STORE_PATH}")

if __name__ == "__main__":
    main()