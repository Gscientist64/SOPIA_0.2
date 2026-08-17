# test_document_count.py - Verify document extraction
import pickle
import os

def test_knowledge_base():
    # Try enhanced first, then original
    kb_files = ["sopia_kb_enhanced.pkl", "sopia_kb.pkl"]
    
    for kb_file in kb_files:
        if os.path.exists(kb_file):
            print(f"📊 Testing {kb_file}...")
            try:
                with open(kb_file, "rb") as f:
                    data = pickle.load(f)
                
                kb = data.get("kb")
                stats = data.get("stats", {})
                
                if hasattr(kb, '_docs'):
                    doc_count = len(kb._docs)
                    print(f"   ✅ Documents: {doc_count}")
                    print(f"   📈 Stats: {stats}")
                    
                    # Test medical term extraction
                    test_terms = ['ART', 'ARV', 'HTS', 'CD4', 'VL', 'TB']
                    for term in test_terms:
                        results = kb.search(term, top_k=2)
                        print(f"   '{term}': {len(results)} results")
                    
                    if doc_count >= 200:
                        print("   🎉 SUCCESS: 200+ documents achieved!")
                    else:
                        print(f"   ⚠️  Only {doc_count} documents - need more extraction")
                        
                else:
                    print("   ❌ No _docs attribute found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"   ❌ {kb_file} not found")

if __name__ == "__main__":
    test_knowledge_base()