# reprocess_with_multikey.py - Enhanced with Medical Knowledge Extraction
import os
import sys
import pickle
import time
import json

sys.path.append(os.getcwd())
from dotenv import load_dotenv
load_dotenv()

from app import MultiKeyLLMClient, InMemoryKB, EnhancedMedicalKB, ClinicalReasoningEngine
from document_processor import DocumentProcessor

print("🚀 ENHANCED MULTI-KEY SOP REPROCESSING")
print("=" * 50)

# Check available API keys
api_keys = [
    os.getenv("GOOGLE_API_KEY"),
    os.getenv("GOOGLE_API_KEY_2"), 
    os.getenv("GOOGLE_API_KEY_3"),
    os.getenv("GOOGLE_API_KEY_4"),
    os.getenv("GOOGLE_API_KEY_5"),
    os.getenv("GOOGLE_API_KEY_6"),
    os.getenv("GOOGLE_API_KEY_7"),
    os.getenv("GOOGLE_API_KEY_8"),
    os.getenv("GOOGLE_API_KEY_9")
]

valid_keys = [key for key in api_keys if key]
print(f"🔑 Available API keys: {len(valid_keys)}")
print(f"📊 Estimated requests: {len(valid_keys) * 250}")

if len(valid_keys) < 2:
    print("⚠️  Recommend at least 2 API keys for reliable processing")
    print("   Add more keys to your .env file as GOOGLE_API_KEY_2, GOOGLE_API_KEY_3, etc.")
else:
    print(f"✅ Excellent! {len(valid_keys)} API keys available for processing")

# Load existing progress to resume
sop_path = os.path.join("sops", "ACE5_SOP.docx")
checkpoint_file = "ACE5_SOP.docx_progress.pkl"

if os.path.exists(checkpoint_file):
    with open(checkpoint_file, "rb") as f:
        progress = pickle.load(f)
    completed = len(progress['completed_chunks'])
    print(f"🔄 Resuming from checkpoint: {completed} analyses completed")
else:
    print("🧹 Starting fresh processing...")

# Initialize with multi-key client
print("🔑 Initializing multi-key LLM...")
try:
    # First, we need a KB for the multi-key client
    temp_kb = InMemoryKB()
    llm = MultiKeyLLMClient(temp_kb)
    print(f"✅ Multi-key LLM initialized with {len(llm.clients)} API clients")
except Exception as e:
    print(f"❌ Multi-key LLM failed: {e}")
    exit(1)

# Process SOP with enhanced analysis
print(f"📄 Processing: {sop_path}")
print("🧠 Starting comprehensive processing with medical knowledge extraction...")

try:
    processor = DocumentProcessor(sop_path, llm_client=llm)
    result = processor.process()
    
    if not result:
        print("❌ Processing returned no result")
        exit(1)
        
    documents = result.get("documents", [])
    stats = result.get("stats", {})
    
    print(f"✅ Document processing completed!")
    print(f"   - Total documents: {len(documents)}")
    print(f"   - Document types: {stats.get('document_types', {})}")
    print(f"   - Analyses completed: {stats.get('analysis_count', 0)}")
    
except Exception as e:
    print(f"❌ Processing failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Build enhanced medical knowledge base
print("🧬 Building medical knowledge base...")
medical_kb = EnhancedMedicalKB()
medical_kb.extract_medical_concepts(documents)

print(f"✅ Medical KB created with {len(medical_kb.concepts)} concepts")
print("📋 Extracted concepts:")
for concept_name, concept in medical_kb.concepts.items():
    print(f"   - {concept_name}: {concept.definition[:100]}...")

# Build clinical reasoning engine
print("🔬 Building clinical reasoning engine...")
reasoning_engine = ClinicalReasoningEngine(medical_kb)
print(f"✅ Clinical reasoning engine ready with {len(reasoning_engine.rules)} rules")

# Build final knowledge base
print("📚 Building comprehensive knowledge base...")
kb = InMemoryKB()

kb_docs = []
for i, doc in enumerate(documents):
    kb_docs.append({
        "text": doc['text'],
        "source_id": doc['source_id']
    })

print(f"📖 Indexing {len(kb_docs)} documents...")
kb.index(kb_docs)

# Save enhanced knowledge base with medical components
kb_data = {
    "kb": kb,
    "medical_kb": medical_kb,
    "stats": {
        "total_documents": len(kb_docs),
        "document_types": stats.get('document_types', {}),
        "analysis_count": stats.get('analysis_count', 0),
        "medical_concepts": len(medical_kb.concepts),
        "medication_regimens": len(medical_kb.medication_regimens),
        "api_keys_used": len(valid_keys),
        "extraction_method": "enhanced_medical",
        "sop_file": sop_path,
        "processing_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
}

with open("sopia_kb.pkl", "wb") as f:
    pickle.dump(kb_data, f)

file_size = os.path.getsize("sopia_kb.pkl") / 1024 / 1024
print(f"💾 ENHANCED KNOWLEDGE BASE SAVED: sopia_kb.pkl")
print(f"   - Documents: {len(kb_docs)}")
print(f"   - Medical concepts: {len(medical_kb.concepts)}")
print(f"   - File size: {file_size:.2f} MB")
print(f"   - API keys utilized: {len(valid_keys)}")

# Test the knowledge base
print("🧪 Testing enhanced knowledge base...")
test_queries = [
    "What is AHD and how is it diagnosed?",
    "CD4 count criteria for Advanced HIV Disease",
    "TB diagnosis in HIV patients",
    "Viral load monitoring frequency",
    "ART regimens for treatment-naive patients",
    "Cryptococcal meningitis screening"
]

for query in test_queries:
    results = kb.search(query, top_k=3)
    print(f"   '{query}': {len(results)} relevant results")

# Test clinical reasoning
print("🏥 Testing clinical reasoning...")
test_patients = [
    {"age": 35, "cd4_count": 150, "symptoms": ["cough", "fever"]},
    {"age": 4, "who_stage": 3, "symptoms": []},
    {"age": 25, "cd4_count": 350, "tb_status": "positive"}
]

for i, patient in enumerate(test_patients):
    assessment = reasoning_engine.evaluate_patient_scenario(patient)
    print(f"   Patient {i+1}: {len(assessment['recommendations'])} recommendations")

print("🎉 ENHANCED PROCESSING COMPLETE!")
print(f"   Final document count: {len(kb_docs)}")
print(f"   Medical concepts: {len(medical_kb.concepts)}")
print(f"   Clinical rules: {len(reasoning_engine.rules)}")
print(f"   API keys used: {len(valid_keys)}")
print("   Start your enhanced app with: python app.py")