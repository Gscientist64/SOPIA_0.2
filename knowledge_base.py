# knowledge_base.py
# v3.9 — Fixed directory creation and enhanced logging

import os
import pickle
import logging
import time
from datetime import datetime
from tqdm import tqdm
from document_processor import DocumentProcessor
from config import CACHE_FILE, CACHE_ENABLED

# -----------------------------
# Configure console logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("SOPKnowledgeBase")


class SOPKnowledgeBase:
    """Handles document processing, embeddings, and caching for the SOP assistant."""

    def __init__(self, embedding_model=None, storage_path=None):
        self.embedding_model = embedding_model
        self.storage_path = storage_path or os.path.join(os.getcwd(), "data", "sop_vectors.pkl")
        self.knowledge_base = {}
        self.doc_path = os.path.join(os.getcwd(), "ACE5_SOP.docx")

        log.info(f"🧠 KnowledgeBase initialized — storage path: {self.storage_path}")

    # ------------------------------------------------------------
    # MAIN INITIALIZATION
    # ------------------------------------------------------------
    def initialize_knowledge_base(self, llm_client=None):
        """Initialize or rebuild the knowledge base if updated or missing."""
        start_time = time.time()
        log.info("🚀 Initializing Knowledge Base...")

        if not CACHE_ENABLED or self._is_rebuild_needed():
            log.info("📄 Document updated or cache disabled — rebuilding knowledge base.")
            self._build_knowledge_base(llm_client)
            log.info(f"✅ Build complete in {time.time() - start_time:.2f}s.")
            return True
        else:
            log.info("💾 Loading cached knowledge base (no updates detected)...")
            self._load_cached_knowledge_base()
            log.info(f"✅ Loaded in {time.time() - start_time:.2f}s.")
            return False

    # ------------------------------------------------------------
    # CORE BUILD LOGIC
    # ------------------------------------------------------------
    def _build_knowledge_base(self, llm_client=None):
        """Extract, embed, and cache knowledge base data."""
        total_start = time.time()

        doc_path = self.doc_path
        if not os.path.exists(doc_path):
            log.error(f"❌ SOP document not found: {doc_path}")
            return

        log.info(f"🔍 Extracting text from SOP document: {os.path.basename(doc_path)}")

        try:
            processor = DocumentProcessor(sop_path=doc_path, llm_client=llm_client)
            result = processor.process()
        except Exception as e:
            log.error(f"❌ Failed to process document: {e}")
            return

        if not result:
            log.error("❌ Document processing failed — no content extracted.")
            return

        chunks = result.get("chunks", [])
        stats = result.get("stats", {})

        log.info(f"🧩 Processing {len(chunks)} chunks...")

        embedded_data = []
        for chunk in tqdm(chunks, desc="🔢 Processing Progress", ncols=80):
            raw_text = chunk.get("raw_text", "").strip()
            analysis = chunk.get("analysis", "").strip()
            
            if raw_text:
                try:
                    # Simulate embedding (replace with your model call if needed)
                    embedding = f"vector_{len(raw_text)}"
                    embedded_data.append({
                        "text": raw_text,
                        "analysis": analysis,
                        "embedding": embedding,
                        "chunk_id": chunk.get("chunk_id", 0)
                    })
                except Exception as e:
                    log.error(f"⚠️ Failed to process raw chunk: {e}")

        # Store all data
        self.knowledge_base = {
            "title": result.get("title", "Unknown SOP"),
            "chunks": embedded_data,
            "stats": stats,
            "file_path": doc_path,
            "file_hash": self._get_file_hash(doc_path),
            "last_updated": datetime.now().isoformat(),
        }

        # Cache knowledge base
        try:
            self.save()  # Use the fixed save method
            log.info("💾 Knowledge base cached successfully!")
        except Exception as e:
            log.error(f"❌ Error saving cache: {e}")

        total_time = time.time() - total_start
        log.info(f"🏁 Build complete in {total_time:.2f}s.")
        self._print_summary()

    # ------------------------------------------------------------
    # CACHE LOADING
    # ------------------------------------------------------------
    def _load_cached_knowledge_base(self):
        """Load previously cached knowledge base."""
        try:
            with open(self.storage_path, "rb") as f:
                self.knowledge_base = pickle.load(f)
            log.info("✅ Cached knowledge base loaded successfully.")
            self._print_summary()
        except Exception as e:
            log.error(f"❌ Cache load failed: {e}")
            log.warning("🔄 Rebuilding instead...")
            self._build_knowledge_base()

    # ------------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------------
    def _print_summary(self):
        """Console summary of key stats."""
        if not self.knowledge_base:
            log.warning("⚠️ No knowledge base available for summary.")
            return

        stats = self.knowledge_base.get("stats", {})
        log.info("\n" + "=" * 60)
        log.info("📊 KNOWLEDGE BASE SUMMARY")
        log.info("=" * 60)
        log.info(f"📘 SOP Title:     {self.knowledge_base.get('title', 'Unknown')}")
        log.info(f"📄 Chunks:        {stats.get('chunks_created', 'N/A')}")
        log.info(f"🧠 Elements:      {stats.get('total_elements', 'N/A')}")
        log.info(f"📊 Tables:        {stats.get('tables_extracted', 'N/A')}")
        log.info(f"🕒 Last Updated:  {self.knowledge_base.get('last_updated', 'N/A')}")
        log.info("=" * 60 + "\n")

    def _is_rebuild_needed(self):
        """Check if rebuild is necessary."""
        if not os.path.exists(self.storage_path):
            return True
        if not os.path.exists(self.doc_path):
            return True
        cache_mtime = os.path.getmtime(self.storage_path)
        doc_mtime = os.path.getmtime(self.doc_path)
        return doc_mtime > cache_mtime

    def _get_file_hash(self, file_path):
        """Simple hash for file change detection."""
        import hashlib
        with open(file_path, "rb") as f:
            data = f.read()
        return hashlib.md5(data).hexdigest()

    # ------------------------------------------------------------
    # PUBLIC METHODS
    # ------------------------------------------------------------
    def clear_all(self):
        """Clear existing embeddings."""
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
            log.info("🧹 Old embedding cache removed.")

    def add_document_chunk(self, source_id, text):
        """Add a chunk manually (for preprocess_sop.py)."""
        if "chunks" not in self.knowledge_base:
            self.knowledge_base["chunks"] = []
        self.knowledge_base["chunks"].append({
            "source": source_id,
            "text": text,
            "embedding": f"vector_{len(text)}"
        })

    def save(self):
        """Save current state with directory creation."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, "wb") as f:
                pickle.dump(self.knowledge_base, f)
            log.info("💾 Knowledge base saved successfully.")
        except Exception as e:
            log.error(f"❌ Failed to save: {e}")