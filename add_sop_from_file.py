#!/usr/bin/env python3
"""
Add SOP content from .txt files to your knowledge base
Usage: python add_sop_from_file.py
"""

import requests
import os
import glob
import time

def check_server_ready():
    """Check if the SOPiA server is running"""
    try:
        response = requests.get("http://localhost:5050/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SOPiA Server is running: {data.get('message', 'Ready')}")
            return True
        else:
            print(f"❌ Server responded with error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to SOPiA server on http://localhost:5050")
        print("💡 Please start your server first with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def add_sop_from_txt(file_path, source_id=None):
    """Add SOP content from a .txt file"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        print(f"⚠️ File is empty: {file_path}")
        return False
    
    # Use filename as source_id if not provided
    if not source_id:
        source_id = os.path.splitext(os.path.basename(file_path))[0]
    
    print(f"📥 Adding SOP from: {file_path}")
    print(f"📝 Content preview: {content[:100]}...")
    
    try:
        response = requests.post(
            "http://localhost:5050/add-sop-text",
            json={
                "text": content,
                "source_id": source_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: Added '{source_id}'")
            print(f"   📊 Total documents: {result.get('total_documents')}")
            print(f"   🧠 Medical concepts: {result.get('medical_concepts', 'N/A')}")
            print(f"   📋 Chunks created: {result.get('chunks_created', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED: Server returned {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is app.py running?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def add_all_sops_from_folder(folder_path="new_sops"):
    """Add all .txt files from a folder"""
    
    if not os.path.exists(folder_path):
        print(f"📁 Folder '{folder_path}' not found - creating it...")
        os.makedirs(folder_path)
        print(f"\n💡 INSTRUCTIONS:")
        print(f"1. Add your new SOP .txt files to the '{folder_path}' folder")
        print(f"2. Run this script again to add them to the knowledge base")
        print(f"3. Example: Create '{folder_path}/new_protocol.txt' with your SOP content")
        
        # Create an example file
        example_file = os.path.join(folder_path, "example_new_protocol.txt")
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write("""NEW PATIENT MONITORING PROTOCOL

Enhanced monitoring for patients with CD4 < 200:
- Weekly clinical assessments
- Monthly viral load tests  
- Nutritional support evaluation
- Adherence counseling sessions

Required forms:
- Form PM-01: Enhanced Monitoring Checklist
- Form PM-02: Nutritional Assessment
""")
        print(f"📝 Created example file: {example_file}")
        return
    
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    
    if not txt_files:
        print(f"📝 No .txt files found in '{folder_path}'")
        print("💡 Add your SOP files as .txt and run this script again")
        return
    
    print(f"📚 Found {len(txt_files)} SOP files to add:")
    for i, file_path in enumerate(txt_files, 1):
        print(f"   {i}. {os.path.basename(file_path)}")
    
    print("\n" + "="*50)
    
    success_count = 0
    for file_path in txt_files:
        print(f"\n🔄 Processing: {os.path.basename(file_path)}...")
        if add_sop_from_txt(file_path):
            success_count += 1
        time.sleep(1)  # Small delay between files
    
    print("\n" + "="*50)
    print(f"🎉 SUMMARY: {success_count}/{len(txt_files)} files added successfully")
    
    if success_count > 0:
        print("\n🧪 Testing new content...")
        test_questions = [
            "What is the new monitoring protocol?",
            "What forms are required for enhanced monitoring?",
            "CD4 monitoring guidelines"
        ]
        
        for question in test_questions:
            try:
                response = requests.post(
                    "http://localhost:5050/ask",
                    json={"question": question},
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"❓ '{question}'")
                    print(f"💡 {result.get('answer', 'No answer')[:150]}...")
                    print(f"   Confidence: {result.get('confidence', 'N/A')}")
                    print("---")
            except Exception as e:
                print(f"⚠️ Test failed for '{question}': {e}")

def main():
    print("🚀 SOP File Adder - Add New SOPs Without Retraining")
    print("=" * 60)
    
    # First check if server is running
    if not check_server_ready():
        return
    
    print("\n📁 Looking for new SOP files...")
    
    # Add all SOPs from the new_sops folder
    add_all_sops_from_folder()
    
    print("\n💡 You can also add individual files by calling:")
    print('   add_sop_from_txt("path/to/your/sop.txt")')

if __name__ == "__main__":
    main()