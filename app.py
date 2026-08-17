# app.py - Enhanced with Medical Knowledge & Clinical Reasoning + SOP Addition Feature
import os
import json
import math
import threading
import pickle
import time
import hashlib
import re
from typing import List, Dict, Any, Optional
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# -------------------------------------------------------------------------
# MEDICAL KNOWLEDGE STRUCTURES
# -------------------------------------------------------------------------

class MedicalConcept:
    def __init__(self, name: str, concept_type: str, definition: str, criteria: Dict, references: List[str]):
        self.name = name
        self.type = concept_type  # 'disease', 'procedure', 'diagnostic', 'medication'
        self.definition = definition
        self.criteria = criteria  # Diagnostic criteria, eligibility, etc.
        self.references = references

class ClinicalPathway:
    def __init__(self, name: str, steps: List[Dict], decision_points: List[Dict]):
        self.name = name
        self.steps = steps  # Sequential steps in the pathway
        self.decision_points = decision_points  # If/then logic points

class EnhancedMedicalKB:
    def __init__(self):
        self.concepts: Dict[str, MedicalConcept] = {}
        self.pathways: Dict[str, ClinicalPathway] = {}
        self.diagnostic_criteria: Dict[str, List] = {}
        self.medication_regimens: Dict[str, Dict] = {}
    
    def extract_medical_concepts(self, documents: List[Dict]):
        """Extract structured medical concepts from SOP documents"""
        print("🔍 Extracting medical concepts from documents...")
        
        for doc in documents:
            text = doc['text']
            source_id = doc['source_id']
            
            # Extract AHD definitions
            if 'advanced hiv disease' in text.lower() or 'ahd' in text.lower():
                self._extract_ahd_concept(text, source_id)
            
            # Extract diagnostic criteria
            if 'cd4' in text.lower() and 'cell count' in text.lower():
                self._extract_cd4_criteria(text, source_id)
            
            # Extract medication regimens
            if any(drug in text.lower() for drug in ['tdf', '3tc', 'dtg', 'art', 'arv', 'tenofovir', 'lamivudine', 'dolutegravir']):
                self._extract_medication_info(text, source_id)
            
            # Extract WHO staging
            if 'who clinical stage' in text.lower():
                self._extract_who_staging(text, source_id)
                
            # Extract TB screening criteria
            if 'tb screening' in text.lower() or 'tuberculosis' in text.lower():
                self._extract_tb_screening(text, source_id)
        
        print(f"✅ Extracted {len(self.concepts)} medical concepts")
    
    def _extract_ahd_concept(self, text: str, source_id: str):
        """Extract AHD definition and criteria"""
        try:
            # Use regex patterns to extract structured data
            cd4_pattern = r'CD4\+?\s*cell\s*count\s*[<]\s*(\d+)'
            who_pattern = r'WHO\s*clinical\s*stage\s*(\d+)'
            pediatric_pattern = r'children.*?(\d+).*?years.*?regardless'
            
            criteria = {}
            
            # CD4 criteria
            cd4_match = re.search(cd4_pattern, text, re.IGNORECASE)
            if cd4_match:
                criteria['cd4_threshold'] = cd4_match.group(1)
            
            # WHO staging
            who_matches = re.findall(who_pattern, text, re.IGNORECASE)
            if who_matches:
                criteria['who_stages'] = list(set(who_matches))
            
            # Pediatric criteria
            pediatric_match = re.search(pediatric_pattern, text, re.IGNORECASE)
            if pediatric_match:
                criteria['pediatric_age'] = pediatric_match.group(1)
            
            # Definition
            definition = "Advanced HIV Disease with immune suppression"
            if 'advanced hiv disease' in text.lower():
                def_match = re.search(r'Advanced HIV Disease[^.!]*[.!]', text)
                if def_match:
                    definition = def_match.group(0)
            
            self.concepts['ahd'] = MedicalConcept(
                name='Advanced HIV Disease',
                concept_type='disease',
                definition=definition,
                criteria=criteria,
                references=[source_id]
            )
        except Exception as e:
            print(f"⚠️ Error extracting AHD concept: {e}")
    
    def _extract_cd4_criteria(self, text: str, source_id: str):
        """Extract CD4 count criteria"""
        try:
            patterns = {
                'ahd_threshold': r'CD4.*?[<]\s*200',
                'prophylaxis_threshold': r'CD4.*?[<]\s*500',
                'monitoring_frequency': r'CD4.*?monitor.*?(\d+.*?(month|week))'
            }
            
            criteria = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    criteria[key] = match.group(0)
            
            if criteria:
                self.concepts['cd4_monitoring'] = MedicalConcept(
                    name='CD4 Monitoring',
                    concept_type='diagnostic',
                    definition='CD4+ T-cell count monitoring for immune status',
                    criteria=criteria,
                    references=[source_id]
                )
        except Exception as e:
            print(f"⚠️ Error extracting CD4 criteria: {e}")
    
    def _extract_medication_info(self, text: str, source_id: str):
        """Extract medication regimen information"""
        try:
            # Look for common regimens
            regimen_patterns = {
                'tdf_3tc_dtg': r'TDF.*?3TC.*?DTG',
                'first_line': r'first.line.*?regimen',
                'second_line': r'second.line.*?regimen',
                'art_initiation': r'ART.*?initiation.*?(\d+.*?(week|day|month))'
            }
            
            regimens = {}
            for name, pattern in regimen_patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    regimens[name] = match.group(0)
            
            if regimens:
                self.medication_regimens['art_regimens'] = regimens
        except Exception as e:
            print(f"⚠️ Error extracting medication info: {e}")
    
    def _extract_who_staging(self, text: str, source_id: str):
        """Extract WHO clinical staging information"""
        try:
            # Extract stage descriptions
            stage_pattern = r'Stage\s*(\d+)[^.]*\.'
            stages = re.findall(stage_pattern, text)
            
            if stages:
                self.concepts['who_staging'] = MedicalConcept(
                    name='WHO Clinical Staging',
                    concept_type='diagnostic',
                    definition='WHO HIV clinical staging system',
                    criteria={'stages_mentioned': stages},
                    references=[source_id]
                )
        except Exception as e:
            print(f"⚠️ Error extracting WHO staging: {e}")
    
    def _extract_tb_screening(self, text: str, source_id: str):
        """Extract TB screening criteria"""
        try:
            symptoms = []
            if 'cough' in text.lower():
                symptoms.append('cough')
            if 'fever' in text.lower():
                symptoms.append('fever')
            if 'weight loss' in text.lower():
                symptoms.append('weight_loss')
            if 'night sweats' in text.lower():
                symptoms.append('night_sweats')
            
            if symptoms:
                self.concepts['tb_screening'] = MedicalConcept(
                    name='TB Screening',
                    concept_type='screening',
                    definition='Tuberculosis screening protocol',
                    criteria={'symptoms': symptoms},
                    references=[source_id]
                )
        except Exception as e:
            print(f"⚠️ Error extracting TB screening: {e}")

# -------------------------------------------------------------------------
# CLINICAL REASONING ENGINE
# -------------------------------------------------------------------------

class ClinicalReasoningEngine:
    def __init__(self, medical_kb: EnhancedMedicalKB):
        self.kb = medical_kb
        self.rules = self._build_clinical_rules()
    
    def _build_clinical_rules(self):
        """Build clinical decision rules from SOP knowledge"""
        return {
            'ahd_screening': {
                'conditions': ['cd4 < 200', 'who_stage_3', 'who_stage_4', 'pediatric_under_5'],
                'actions': ['perform_tb_screening', 'test_for_cryptococcosis', 'initiate_ahd_package'],
                'priority': 'high'
            },
            'art_initiation_timing': {
                'conditions': {
                    'tb_positive': 'start_art_after_2_weeks',
                    'cryptococcal_meningitis': 'start_art_after_6_weeks', 
                    'no_ois': 'start_art_same_day'
                },
                'priority': 'medium'
            },
            'tb_screening': {
                'conditions': ['cough_2_weeks', 'fever', 'weight_loss', 'night_sweats', 'tb_contact'],
                'actions': ['perform_gene_xpert', 'chest_xray', 'tb_lam_if_ahd'],
                'priority': 'high'
            }
        }
    
    def evaluate_patient_scenario(self, patient_data: Dict) -> Dict:
        """Evaluate clinical scenario and provide recommendations"""
        recommendations = []
        
        # Check for AHD
        if self._meets_ahd_criteria(patient_data):
            recommendations.append({
                'type': 'screening',
                'message': 'Patient meets AHD criteria - initiate AHD package of care',
                'actions': self.rules['ahd_screening']['actions'],
                'priority': 'high',
                'confidence': 0.9
            })
        
        # Check TB screening need
        if self._needs_tb_screening(patient_data):
            recommendations.append({
                'type': 'screening',
                'message': 'Patient has TB symptoms - initiate TB screening',
                'actions': self.rules['tb_screening']['actions'],
                'priority': 'high',
                'confidence': 0.8
            })
        
        # Check ART initiation timing
        art_timing = self._determine_art_timing(patient_data)
        if art_timing:
            recommendations.append({
                'type': 'treatment',
                'message': f'ART initiation: {art_timing}',
                'actions': [f'plan_art_initiation_{art_timing}'],
                'priority': 'high',
                'confidence': 0.85
            })
        
        return {
            'recommendations': recommendations,
            'clinical_summary': self._generate_clinical_summary(patient_data),
            'concepts_applied': list(self._get_applied_concepts(patient_data))
        }
    
    def _meets_ahd_criteria(self, patient_data: Dict) -> bool:
        """Check if patient meets AHD criteria"""
        ahd_concept = self.kb.concepts.get('ahd')
        if not ahd_concept:
            return False
        
        cd4 = patient_data.get('cd4_count')
        who_stage = patient_data.get('who_stage')
        age = patient_data.get('age')
        
        # Check CD4 criteria
        if cd4 and cd4 < 200:
            return True
        
        # Check WHO staging
        if who_stage and who_stage in [3, 4]:
            return True
        
        # Check pediatric criteria
        if age and age <= 5:
            return True
        
        return False
    
    def _needs_tb_screening(self, patient_data: Dict) -> bool:
        """Check if patient needs TB screening"""
        symptoms = patient_data.get('symptoms', [])
        tb_contact = patient_data.get('tb_contact', False)
        
        # Check for TB symptoms
        tb_symptoms = ['cough', 'fever', 'weight_loss', 'night_sweats']
        if any(symptom in symptoms for symptom in tb_symptoms):
            return True
        
        # Check for TB contact
        if tb_contact:
            return True
        
        return False
    
    def _determine_art_timing(self, patient_data: Dict) -> str:
        """Determine appropriate ART initiation timing"""
        tb_status = patient_data.get('tb_status')
        cryptococcal_status = patient_data.get('cryptococcal_status')
        other_ois = patient_data.get('other_ois', [])
        
        if tb_status == 'positive':
            return '2_weeks_after_tb_treatment'
        elif cryptococcal_status == 'positive':
            return '6_weeks_after_cryptococcal_treatment'
        elif not other_ois:
            return 'same_day'
        
        return 'evaluate_further'
    
    def _generate_clinical_summary(self, patient_data: Dict) -> str:
        """Generate clinical summary based on patient data"""
        summary_parts = []
        
        if self._meets_ahd_criteria(patient_data):
            summary_parts.append("Meets AHD criteria")
        
        if self._needs_tb_screening(patient_data):
            summary_parts.append("Requires TB screening")
        
        art_timing = self._determine_art_timing(patient_data)
        summary_parts.append(f"ART timing: {art_timing}")
        
        return "; ".join(summary_parts) if summary_parts else "No immediate concerns identified"
    
    def _get_applied_concepts(self, patient_data: Dict) -> set:
        """Get medical concepts applied in this evaluation"""
        concepts = set()
        
        if self._meets_ahd_criteria(patient_data):
            concepts.add('ahd')
        
        if self._needs_tb_screening(patient_data):
            concepts.add('tb_screening')
        
        if patient_data.get('cd4_count'):
            concepts.add('cd4_monitoring')
        
        return concepts

# -------------------------------------------------------------------------
# SIMPLE CACHE SYSTEM
# -------------------------------------------------------------------------

class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, question: str) -> Optional[Dict]:
        """Get cached response for question"""
        key = question.lower().strip()
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, question: str, response: Dict):
        """Cache a response"""
        key = question.lower().strip()
        self.cache[key] = response
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'size': len(self.cache)
        }

# -------------------------------------------------------------------------
# ENHANCED LLM BACKENDS WITH MULTI-KEY FALLBACK
# -------------------------------------------------------------------------

class LLMClient:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        # New official SDK (google-genai) — the legacy google.generativeai
        # package is deprecated and no longer supported by Google.
        from google import genai
        from google.genai import types
        if not api_key:
            raise RuntimeError("API key not provided for Gemini backend.")
        
        self.api_key = api_key
        self._client = genai.Client(api_key=api_key)

        # Try preferred models in order (current generation only)
        # NOTE: gemini-2.5-* returns 404 for new users — must use 3.x models
        preferred_models = [
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash",
            "gemini-flash-latest",
        ]
        if model_name:
            preferred_models.insert(0, model_name.replace("models/", ""))

        # Find first available model
        chosen_model = None
        try:
            available = set()
            for m in self._client.models.list():
                actions = getattr(m, "supported_actions", None) or []
                if "generateContent" in actions:
                    available.add(m.name.replace("models/", ""))
            for model in preferred_models:
                if model in available:
                    chosen_model = model
                    break
            if not chosen_model and available:
                chosen_model = sorted(available)[0]
            elif not chosen_model:
                raise RuntimeError("No Gemini models available")
        except Exception:
            # If listing fails, use the default current model
            chosen_model = "gemini-3.6-flash"

        self.model_name = chosen_model
        self._types = types

    def generate(self, prompt: str) -> str:
        import time
        for attempt in range(3):
            try:
                resp = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self._types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=1024,
                    ),
                )
                return (resp.text or "").strip()
            except Exception as e:
                if attempt == 2:
                    raise e
                time.sleep(2)

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        from openai import OpenAI
        if not api_key:
            raise RuntimeError("API key not provided for OpenAI backend.")
        self._client = OpenAI(api_key=api_key)
        self._model = model_name

    def generate(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return (resp.choices[0].message.content or "").strip()

class OfflineClient(LLMClient):
    """Fallback client that works entirely offline using KB search"""
    def __init__(self, kb_provider):
        self.kb = kb_provider
    
    def generate(self, prompt: str) -> str:
        # Extract the question from the prompt (simple heuristic)
        if "USER QUESTION:" in prompt:
            question = prompt.split("USER QUESTION:")[1].split("\n")[0].strip()
        else:
            # Fallback: use the last line as question
            lines = prompt.strip().split('\n')
            question = lines[-1].replace("Answer:", "").strip()
        
        # Search for relevant content
        hits = self.kb.search(question, top_k=5)
        
        if not hits:
            return "I couldn't find specific information about this in the SOP documents. The knowledge base contains HIV care procedures, but this specific question may not be covered."
        
        # Build answer from search results
        context_parts = []
        for hit in hits[:3]:
            context_parts.append(hit["text"])
        
        context = "\n\n".join(context_parts)
        
        return f"""Based on the SOP documents:

{context}

*Note: This answer is generated from pre-processed SOP documents using offline search.*"""

class MultiKeyLLMClient(LLMClient):
    """Client that tries multiple API keys with fallback to offline mode"""
    def __init__(self, kb_provider):
        self.kb = kb_provider
        self.clients = []
        self.current_client_index = 0
        self.offline_client = OfflineClient(kb_provider)
        self.used_offline_fallback = False
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all available API clients"""
        # Gemini API keys (add as many as you have)
        gemini_keys = [
            os.getenv("GOOGLE_API_KEY"),       # Your primary key
            os.getenv("GOOGLE_API_KEY_2"),     # Friend's backup key
            os.getenv("GOOGLE_API_KEY_3"), 
            os.getenv("GOOGLE_API_KEY_4"), 
            os.getenv("GOOGLE_API_KEY_5"),
            os.getenv("GOOGLE_API_KEY_6"),
            os.getenv("GOOGLE_API_KEY_7"),
            os.getenv("GOOGLE_API_KEY_8"),
            os.getenv("GOOGLE_API_KEY_9"),
        ]
        
        # Filter out None keys
        gemini_keys = [key for key in gemini_keys if key]
        
        # Create Gemini clients for each valid key
        for api_key in gemini_keys:
            try:
                client = GeminiClient(api_key)
                self.clients.append({
                    'client': client,
                    'key_id': f"gemini_{hashlib.md5(api_key.encode()).hexdigest()[:8]}",
                    'type': 'gemini'
                })
                print(f"✅ Gemini client initialized: {client.model_name}")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini client: {e}")
        
        # OpenAI fallback (if available)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                client = OpenAIClient(openai_key)
                self.clients.append({
                    'client': client,
                    'key_id': f"openai_{hashlib.md5(openai_key.encode()).hexdigest()[:8]}",
                    'type': 'openai'
                })
                print(f"✅ OpenAI client initialized: {client._model}")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}")
        
        print(f"🔑 Total API clients available: {len(self.clients)}")
        if len(self.clients) == 0:
            print("💡 No API clients available - running in offline mode only")
    
    def generate(self, prompt: str) -> str:
        self.used_offline_fallback = False
        # If no API clients, use offline mode immediately
        if not self.clients:
            self.used_offline_fallback = True
            return self.offline_client.generate(prompt)
        
        # Try each client in order
        for i in range(len(self.clients)):
            client_info = self.clients[self.current_client_index]
            client = client_info['client']
            
            try:
                result = client.generate(prompt)
                print(f"✅ Success with {client_info['key_id']} ({client_info['type']})")
                return result
            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Client {client_info['key_id']} failed: {error_str}")
                
                # Check if it's a quota error (429)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"🔁 Quota exceeded for {client_info['key_id']}, rotating to next client...")
                    # Move to next client
                    self.current_client_index = (self.current_client_index + 1) % len(self.clients)
                    continue
                else:
                    # Other error, try next client
                    self.current_client_index = (self.current_client_index + 1) % len(self.clients)
                    continue
        
        # All API clients failed, fall back to offline mode
        print("🔌 All API clients exhausted, falling back to offline mode")
        self.used_offline_fallback = True
        return self.offline_client.generate(prompt)

def build_llm(kb_provider) -> LLMClient:
    """Build LLM with multi-key fallback support"""
    return MultiKeyLLMClient(kb_provider)

# -------------------------------------------------------------------------
# KNOWLEDGE BASE - YOUR ORIGINAL CODE
# -------------------------------------------------------------------------

class InMemoryKB:
    def __init__(self):
        self._docs: List[Dict[str, Any]] = []
        self._idf: Dict[str, float] = {}
        self._avg_len = 1.0

    def index(self, docs: List[Dict[str, Any]]) -> None:
        import re
        df: Dict[str, int] = {}
        self._docs = []
        lengths = []
        for d in docs:
            text = (d.get("text") or "").strip()
            if not text:
                continue
            sid = d.get("source_id", "sop")
            tokens = [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2]
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self._docs.append({"text": text, "source_id": sid, "tf": tf, "len": len(tokens)})
            lengths.append(len(tokens))
            for t in tf:
                df[t] = df.get(t, 0) + 1
        N = max(1, len(self._docs))
        self._idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
        self._avg_len = sum(lengths) / len(lengths) if lengths else 1.0

    def search(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        import re
        if not self._docs:
            return []
        q_tokens = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]
        k1, b = 1.5, 0.75
        scores = []
        for d in self._docs:
            score = 0.0
            dl = d["len"]
            for t in q_tokens:
                tf = d["tf"].get(t, 0)
                if tf == 0:
                    continue
                idf = self._idf.get(t, 0.0)
                denom = tf + k1 * (1 - b + b * (dl / self._avg_len))
                score += idf * ((tf * (k1 + 1)) / denom)
            if score > 0:
                scores.append((score, d))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [
            {"text": d["text"], "source_id": d["source_id"], "score": s / 10.0}
            for s, d in scores[:top_k]
        ]

# -------------------------------------------------------------------------
# ENHANCED CHAT ENGINE WITH CLINICAL REASONING
# -------------------------------------------------------------------------

class ChatResponse:
    def __init__(self, answer: str, confidence: float, sources_used: List[str], meta: Dict[str, Any]):
        self.answer = answer
        self.confidence = confidence
        self.sources_used = sources_used
        self.meta = meta

class EnhancedChatEngine:
    def __init__(self, kb_provider, llm_client, medical_kb: EnhancedMedicalKB, reasoning_engine: ClinicalReasoningEngine, max_context_chars: int = 15000):
        self.kb = kb_provider
        self.llm = llm_client
        self.medical_kb = medical_kb
        self.reasoning_engine = reasoning_engine
        self.max_context_chars = max_context_chars
        self.cache = SimpleCache()

    def answer(self, user_question: str, patient_context: Dict = None) -> ChatResponse:
        start_time = time.time()
        
        # CHECK CACHE FIRST
        cache_key = f"{user_question}_{json.dumps(patient_context) if patient_context else 'no_context'}"
        cached = self.cache.get(cache_key)
        if cached:
            cached['meta']['cached'] = True
            cached['meta']['response_time'] = 0.01
            return ChatResponse(**cached)
        
        # Search for relevant content
        hits = self.kb.search(user_question, top_k=8)
        
        # Build context from top hits
        context_parts = []
        total_chars = 0
        for hit in hits:
            text = hit["text"]
            # Clean the text by removing reference markers
            cleaned_text = self._clean_context_text(text)
            if total_chars + len(cleaned_text) > self.max_context_chars:
                break
            context_parts.append(cleaned_text)
            total_chars += len(cleaned_text)
        
        context = "\n\n".join(context_parts)
        
        # ENHANCED: Add clinical reasoning for patient-specific questions
        if patient_context and self._is_clinical_question(user_question):
            clinical_recommendations = self.reasoning_engine.evaluate_patient_scenario(patient_context)
            context += f"\n\nCLINICAL ASSESSMENT:\n{json.dumps(clinical_recommendations, indent=2)}"
        
        # ENHANCED: Add structured medical concepts to context
        medical_context = self._get_medical_context(user_question)
        if medical_context:
            context += f"\n\nMEDICAL KNOWLEDGE:\n{medical_context}"
        
        # Enhanced prompt for clinical reasoning
        prompt = self._build_enhanced_prompt(context, user_question, patient_context)
        
        try:
            answer = self.llm.generate(prompt)
            
            # Enhanced response cleaning for clean, natural style
            answer = self._clean_response_formatting(answer)
            
            # Extract meaningful source names
            source_names = self._extract_source_names(hits[:3])
            
            # Calculate confidence based on search results
            top_scores = [h.get("score", 0) for h in hits[:3]]
            avg_score = sum(top_scores) / len(top_scores) if top_scores else 0
            confidence = min(0.95, max(0.3, avg_score))
            
            # Check if we're in offline mode (honest reporting)
            is_offline = isinstance(self.llm, OfflineClient) or bool(
                getattr(self.llm, 'used_offline_fallback', False)
            )
            
            response_data = {
                'answer': answer,
                'confidence': round(confidence, 2),
                'sources_used': source_names,
                'meta': {
                    'hits_considered': len(hits), 
                    'context_chars': total_chars,
                    'response_time': round(time.time() - start_time, 2),
                    'cached': False,
                    'offline_mode': is_offline,
                    'clinical_context_used': patient_context is not None
                }
            }
            
            # CACHE THE RESPONSE
            self.cache.set(cache_key, response_data)
            
            return ChatResponse(**response_data)
            
        except Exception as e:
            return ChatResponse(
                answer="😔 I'm having trouble accessing the information right now. Please try again in a moment!",
                confidence=0.1,
                sources_used=[],
                meta={"error": str(e), "response_time": round(time.time() - start_time, 2), "cached": False, "offline_mode": True}
            )

    def _is_clinical_question(self, question: str) -> bool:
        """Check if question is clinical in nature"""
        clinical_keywords = [
            'patient', 'cd4', 'viral load', 'symptoms', 'diagnosis', 'treatment',
            'medication', 'regimen', 'stage', 'screening', 'test', 'result',
            'age', 'years old', 'pregnant', 'tb', 'tuberculosis', 'cryptococcal',
            'art', 'arv', 'initiation', 'therapy'
        ]
        return any(keyword in question.lower() for keyword in clinical_keywords)

    def _get_medical_context(self, question: str) -> str:
        """Get relevant medical concepts for the question"""
        relevant_concepts = []
        
        # Map question keywords to medical concepts
        keyword_to_concept = {
            'ahd': ['ahd', 'advanced hiv', 'cd4', 'who stage'],
            'tb': ['tb', 'tuberculosis', 'cough', 'screening'],
            'art': ['art', 'arv', 'regimen', 'medication'],
            'cd4': ['cd4', 'cell count', 'immune'],
            'viral load': ['viral load', 'vl', 'suppression']
        }
        
        question_lower = question.lower()
        for concept_name, keywords in keyword_to_concept.items():
            if any(keyword in question_lower for keyword in keywords):
                concept = self.medical_kb.concepts.get(concept_name)
                if concept:
                    relevant_concepts.append(f"{concept.name}: {concept.definition}")
        
        return "\n".join(relevant_concepts) if relevant_concepts else ""

    def _build_enhanced_prompt(self, context: str, question: str, patient_context: Dict = None) -> str:
        base_prompt = f"""You are SOPIA, an expert clinical decision support system for HIV care. You have deep knowledge of medical protocols and can reason through complex clinical scenarios.

MEDICAL CONTEXT:
{context}

"""
        
        if patient_context:
            base_prompt += f"""
PATIENT CONTEXT:
{json.dumps(patient_context, indent=2)}

"""
        
        base_prompt += f"""
USER QUESTION: {question}

CLINICAL REASONING APPROACH:
1. First analyze any clinical data provided
2. Apply relevant diagnostic criteria from the SOP
3. Consider appropriate treatment pathways
4. Identify any contraindications or special considerations
5. Provide clear, actionable recommendations

CRITICAL AGE DEFINITION - NEVER FORGET:
• Paediatric: 0-14 years (≤14 years)
• Adult: 15+ years (>14 years) 
• These definitions are ABSOLUTE and NON-NEGOTIABLE
• Never use any other age categorizations
• Always apply this logic: if age ≤14 = paediatric, if age >14 = adult

RESPONSE REQUIREMENTS:
- Use clinical terminology appropriately
- Reference specific diagnostic criteria when applicable
- Suggest next steps in patient management
- Highlight critical actions or warnings
- Maintain warm, professional tone
- Use bullet points (•) for lists and key information
- Only use numbered lists for actual step-by-step procedures
- Keep paragraphs short and scannable
- Use simple emojis occasionally to make it friendly 😊
- Speak as if you're explaining directly to a healthcare colleague
- Focus on clear, practical information they can use immediately

Answer:"""
        
        return base_prompt

    def _clean_context_text(self, text: str) -> str:
        """Remove reference markers and clean context text"""
        # Remove [para_XXXX], [term_XXXX], [table_XXXX] etc.
        text = re.sub(r'\[(para|term|table|analysis)_\d+\]', '', text)
        # Remove any remaining bracketed references
        text = re.sub(r'\[\w+\]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _clean_response_formatting(self, answer: str) -> str:
        """Clean up response formatting to be natural and reference-free"""
        # Remove all markdown formatting
        answer = re.sub(r'\*\*(.*?)\*\*', r'\1', answer)  # Remove bold
        answer = re.sub(r'\*(.*?)\*', r'\1', answer)      # Remove italics
        answer = re.sub(r'_(.*?)_', r'\1', answer)        # Remove underscores
        
        # Remove numbered lists that aren't actual steps
        lines = answer.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove "1.", "2.", "3." etc. from the beginning of lines unless it's a procedure
            if re.match(r'^\d+\.\s+', line) and not any(step_word in line.lower() for step_word in ['step', 'procedure', 'process']):
                line = re.sub(r'^\d+\.\s*', '• ', line)
            
            # Remove formal headers and make more conversational
            line = re.sub(r'^(Key points|Important considerations|Steps|Conclusion|Note):\s*', '', line)
            
            # Ensure bullet points are consistent
            line = re.sub(r'^[-*]\s*', '• ', line)
            
            # Remove any remaining document references
            line = re.sub(r'\[(para|term|table|analysis)_\d+\]', '', line)
            line = re.sub(r'\[\w+\]', '', line)
            
            # Remove phrases that reference documents
            line = re.sub(r'(according to|based on|as mentioned in|per|following).*?(sop|document|procedure|guideline)', '', line, flags=re.IGNORECASE)
            
            cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Ensure the response starts conversationally
        if not cleaned_text.startswith(('Great question', 'Sure', 'Absolutely', 'Hi', 'Hello', 'Hey', '😊', '👋', 'Thanks', 'Thank you')):
            # Add a conversational starter if missing
            conversational_starters = [
                "Great question! ",
                "I'd be happy to explain! ",
                "Sure thing! ",
                "Absolutely! ",
                "Let me break this down for you! ",
                "Thanks for asking! "
            ]
            import random
            starter = random.choice(conversational_starters)
            cleaned_text = starter + cleaned_text
        
        # Clean up excessive line breaks
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text.strip()

    def _extract_source_names(self, hits: List[Dict]) -> List[str]:
        """Extract meaningful source names from source IDs"""
        source_names = []
        
        for hit in hits:
            source_id = hit.get("source_id", "")
            
            # Map source IDs to meaningful names
            if source_id.startswith('analysis_'):
                source_names.append("AI Analysis")
            elif source_id.startswith('para_'):
                source_names.append("SOP Procedures")
            elif source_id.startswith('table_'):
                source_names.append("Clinical Tables")
            elif source_id.startswith('term_'):
                source_names.append("Medical Definitions")
            elif 'art' in source_id.lower():
                source_names.append("ART Guidelines")
            elif 'ahd' in source_id.lower():
                source_names.append("AHD Protocol")
            elif 'tb' in source_id.lower():
                source_names.append("TB Management")
            elif 'lab' in source_id.lower():
                source_names.append("Laboratory SOP")
            elif 'pharmacy' in source_id.lower():
                source_names.append("Pharmacy SOP")
            else:
                source_names.append("SOP Document")
        
        # Remove duplicates and limit to 3
        unique_sources = list(dict.fromkeys(source_names))[:3]
        return unique_sources

# -------------------------------------------------------------------------
# APP SETUP - ENHANCED WITH MEDICAL KNOWLEDGE
# -------------------------------------------------------------------------

app = Flask(__name__, template_folder="templates", static_folder="templates")
CORS(app)

# Bump this when you deploy a notable change — shown in /health so you can
# always verify which build is actually running on Render.
DEPLOY_VERSION = "2026-08-17.4"  # google-genai SDK + gemini-3.6-flash + faster responses

# Global state
_kb: Optional[InMemoryKB] = None
_llm: Optional[LLMClient] = None
_chat: Optional[EnhancedChatEngine] = None
_medical_kb: Optional[EnhancedMedicalKB] = None
_reasoning_engine: Optional[ClinicalReasoningEngine] = None
_last_stats: Dict[str, Any] = {}
_initialized: bool = False

def _load_preprocessed_kb() -> bool:
    """Load sopia_kb.pkl if present."""
    global _kb, _last_stats, _medical_kb
    if not os.path.exists("sopia_kb.pkl"):
        return False
    try:
        with open("sopia_kb.pkl", "rb") as f:
            payload = pickle.load(f)
        _kb = payload.get("kb")
        _last_stats = payload.get("stats", {})
        
        # Try to load medical KB if available
        _medical_kb = payload.get("medical_kb")
        
        if _kb and hasattr(_kb, 'search'):
            print(f"✅ Preprocessed KB loaded with {len(getattr(_kb, '_docs', []))} documents")
            if _medical_kb:
                print(f"✅ Medical KB loaded with {len(_medical_kb.concepts)} concepts")
            return True
        else:
            print("⚠️ KB loaded but invalid format")
            return False
    except Exception as e:
        print(f"⚠️ Failed to load preprocessed KB: {e}")
        return False

def _init_if_needed():
    global _llm, _kb, _chat, _medical_kb, _reasoning_engine, _initialized
    if _initialized:
        return

    # Try to load preprocessed KB
    kb_loaded = _load_preprocessed_kb()
    
    # Initialize LLM with multi-key fallback
    if kb_loaded:
        try:
            _llm = build_llm(_kb)  # Pass KB for offline fallback
            print(f"✅ Multi-key LLM initialized")
        except Exception as e:
            print(f"❌ LLM failed: {e}")
            _llm = None
    else:
        _llm = None

    # Initialize medical knowledge base if not loaded
    if not _medical_kb and _kb:
        _medical_kb = EnhancedMedicalKB()
        _medical_kb.extract_medical_concepts(_kb._docs)
        print(f"✅ Medical KB created with {len(_medical_kb.concepts)} concepts")
    
    # Initialize clinical reasoning engine
    if _medical_kb:
        _reasoning_engine = ClinicalReasoningEngine(_medical_kb)
        print(f"✅ Clinical reasoning engine initialized")

    # Initialize enhanced chat engine if all available
    if _kb and _llm and _medical_kb and _reasoning_engine:
        _chat = EnhancedChatEngine(_kb, _llm, _medical_kb, _reasoning_engine)
        _initialized = True
        print("✅ Enhanced chat engine ready with clinical reasoning - System fully initialized")
    elif _kb and _llm:
        # Fallback to basic chat engine
        from app import ChatEngine
        _chat = ChatEngine(_kb, _llm)
        _initialized = True
        print("✅ Basic chat engine ready - Medical features limited")
    else:
        print("⚠️ System partially initialized")

# Initialize on startup
_init_if_needed()

# -------------------------------------------------------------------------
# ROUTES - ENHANCED WITH CLINICAL FEATURES + SOP ADDITION
# -------------------------------------------------------------------------

@app.route("/")
def index():
    """Main landing page — uses the sleek chat UI"""
    return render_template("chat_demo.html")

@app.route("/demo")
def demo():
    """Demo chat interface (same as homepage)"""
    return render_template("chat_demo.html")

@app.route("/health")
def health():
    try:
        _init_if_needed()
        cache_stats = _chat.cache.get_stats() if _chat else {}
        
        # Get API status
        api_status = "unknown"
        gemini_model = None
        if _llm and hasattr(_llm, 'clients'):
            api_status = f"{len(_llm.clients)} clients available"
            if _llm.clients:
                try:
                    gemini_model = _llm.clients[0]['client'].model_name
                except Exception:
                    gemini_model = "unknown"
        elif _llm and isinstance(_llm, OfflineClient):
            api_status = "offline_only"
        elif not _llm:
            api_status = "no_llm"
        
        # Get medical features status
        medical_status = "available" if _medical_kb else "unavailable"
        reasoning_status = "available" if _reasoning_engine else "unavailable"
        
        return jsonify({
            "ok": True, 
            "message": "SOPiA backend healthy",
            "initialized": _initialized,
            "has_kb": _kb is not None,
            "has_llm": _llm is not None,
            "has_medical_kb": _medical_kb is not None,
            "has_reasoning_engine": _reasoning_engine is not None,
            "api_status": api_status,
            "gemini_model": gemini_model,
            "deploy_version": DEPLOY_VERSION,
            "medical_features": medical_status,
            "clinical_reasoning": reasoning_status,
            "cache_stats": cache_stats
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/initialize", methods=["POST", "GET"])
def initialize():
    """Initialize or return current status"""
    try:
        _init_if_needed()
        
        if _initialized:
            stats = _last_stats or {
                "kb_passages_indexed": len(getattr(_kb, '_docs', [])),
                "total_documents": 1,
                "extraction_method": "preprocessed"
            }
            
            cache_stats = _chat.cache.get_stats() if _chat else {}
            
            response_data = {
                "success": True,
                "message": "System ready with preprocessed knowledge",
                "stats": stats,
                "cache_stats": cache_stats,
                "preprocessed": True
            }
            
            # Add medical features info
            if _medical_kb:
                response_data["medical_concepts"] = len(_medical_kb.concepts)
                response_data["clinical_pathways"] = len(_medical_kb.pathways)
            
            return jsonify(response_data)
        else:
            return jsonify({
                "success": False,
                "error": "System not fully initialized - check KB and API keys"
            }), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/debug-state")
def debug_state():
    state = {
        "initialized": _initialized,
        "kb_loaded": _kb is not None,
        "llm_loaded": _llm is not None,
        "chat_ready": _chat is not None,
        "medical_kb_loaded": _medical_kb is not None,
        "reasoning_engine_loaded": _reasoning_engine is not None,
    }
    
    if _kb:
        state["kb_docs"] = len(getattr(_kb, '_docs', []))
        state["kb_type"] = str(type(_kb))
    
    if _llm:
        if hasattr(_llm, 'clients'):
            state["api_clients"] = len(_llm.clients)
            state["current_client_index"] = _llm.current_client_index
        state["llm_type"] = str(type(_llm))
        
    if _medical_kb:
        state["medical_concepts"] = len(_medical_kb.concepts)
        state["medication_regimens"] = len(_medical_kb.medication_regimens)
    
    if _chat:
        state["cache_stats"] = _chat.cache.get_stats()
        
    return jsonify(state)

@app.route("/stats")
def stats():
    if not _initialized:
        return jsonify({"ok": False, "error": "System not initialized"}), 400
        
    stats_data = _last_stats or {
        "qa_pairs": len(getattr(_kb, '_docs', [])),
        "kb_passages_indexed": len(getattr(_kb, '_docs', [])),
        "total_documents": 1
    }
    
    cache_stats = _chat.cache.get_stats() if _chat else {}
    stats_data["cache"] = cache_stats
    
    # Add medical stats
    if _medical_kb:
        stats_data["medical_concepts"] = len(_medical_kb.concepts)
        stats_data["clinical_pathways"] = len(_medical_kb.pathways)
        stats_data["medication_regimens"] = len(_medical_kb.medication_regimens)
    
    return jsonify({"ok": True, "stats": stats_data})

@app.route("/ask", methods=["POST"])
@app.route("/chat", methods=["POST"])
def ask():
    try:
        _init_if_needed()
        
        if not _chat:
            return jsonify({"error": "System not ready. Check KB and API keys.", "ok": False}), 400

        data = request.get_json() or {}
        question = data.get("question") or data.get("query") or ""
        patient_context = data.get("patient_context")  # New: clinical context
        
        if not question:
            return jsonify({"error": "No question provided", "ok": False}), 400

        resp = _chat.answer(question, patient_context)
        return jsonify({
            "ok": True,
            "answer": resp.answer,
            "confidence": resp.confidence,
            "sources_used": resp.sources_used,
            "meta": resp.meta
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "ok": False}), 500

# NEW ROUTE: ADD SOP CONTENT WITHOUT RETRAINING
@app.route("/add-sop-text", methods=["POST"])
def add_sop_text():
    """Add new SOP content from text without retraining"""
    try:
        _init_if_needed()
        
        if not _kb:
            return jsonify({"error": "Knowledge base not initialized", "ok": False}), 400

        data = request.get_json() or {}
        text_content = data.get("text", "")
        source_id = data.get("source_id", f"new_sop_{int(time.time())}")
        
        if not text_content:
            return jsonify({"error": "No text content provided", "ok": False}), 400
        
        print(f"📥 Adding new SOP content: {source_id}")
        
        # Create new document entry
        new_doc = {
            "text": text_content,
            "source_id": source_id
        }
        
        # Get current documents and add new one
        current_docs = _kb._docs.copy()
        current_docs.append(new_doc)
        
        # Re-index with new content
        _kb.index(current_docs)
        
        # Update medical KB with new content
        if _medical_kb:
            _medical_kb.extract_medical_concepts([new_doc])
            print(f"✅ Medical KB updated with new concepts")
        
        # Also create granular chunks for better search
        granular_chunks = _create_granular_chunks(text_content, source_id)
        for chunk in granular_chunks:
            chunk_doc = {
                "text": chunk["text"],
                "source_id": chunk["source_id"]
            }
            current_docs.append(chunk_doc)
        
        # Final re-index with all chunks
        _kb.index(current_docs)
        
        print(f"✅ New SOP content added successfully: {source_id}")
        print(f"📊 Total documents now: {len(_kb._docs)}")
        
        return jsonify({
            "ok": True,
            "message": "SOP content added successfully",
            "source_id": source_id,
            "total_documents": len(_kb._docs),
            "medical_concepts": len(_medical_kb.concepts) if _medical_kb else 0,
            "chunks_created": len(granular_chunks)
        })
        
    except Exception as e:
        print(f"❌ Error adding SOP content: {e}")
        return jsonify({"error": str(e), "ok": False}), 500

def _create_granular_chunks(text: str, source_id: str) -> List[Dict]:
    """Break new SOP into multiple searchable chunks"""
    chunks = []
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]  # Meaningful sentences only
    
    for i, sentence in enumerate(sentences):
        chunks.append({
            "text": sentence,
            "source_id": f"{source_id}_sent_{i+1}"
        })
    
    # Also add the full text as a document
    chunks.append({
        "text": text,
        "source_id": f"{source_id}_full"
    })
    
    # Extract key medical terms
    medical_terms = _extract_medical_terms(text)
    for term, context in medical_terms:
        chunks.append({
            "text": f"MEDICAL TERM: {term} - {context}",
            "source_id": f"{source_id}_term_{len(chunks)+1}"
        })
    
    return chunks

def _extract_medical_terms(text: str) -> List[tuple]:
    """Extract medical terms and their context"""
    medical_keywords = [
        'ART', 'ARV', 'HTS', 'AHD', 'CD4', 'VL', 'viral load', 'TB', 
        'tuberculosis', 'prophylaxis', 'regimen', 'DTG', 'TDF', '3TC',
        'cryptococcal', 'meningitis', 'OI', 'opportunistic infection',
        'PEP', 'PrEP', 'IPT', 'STI', 'screening', 'diagnosis', 'treatment',
        'monitoring', 'adherence', 'counseling', 'testing', 'clinical stage',
        'WHO stage', 'immune reconstitution', 'IRIS', 'antiretroviral'
    ]
    
    terms_found = []
    lines = text.split('\n')
    
    for line in lines:
        for term in medical_keywords:
            if term.lower() in line.lower() and len(line) < 500:
                terms_found.append((term, line.strip()))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_terms = []
    for term, context in terms_found:
        if (term, context) not in seen:
            seen.add((term, context))
            unique_terms.append((term, context))
    
    return unique_terms[:20]  # Limit to top 20 unique terms

@app.route("/clinical-assessment", methods=["POST"])
def clinical_assessment():
    """Perform clinical assessment based on patient data"""
    try:
        data = request.get_json() or {}
        patient_data = data.get("patient_data", {})
        
        if not _reasoning_engine:
            return jsonify({"error": "Clinical reasoning engine not available"}), 400
        
        assessment = _reasoning_engine.evaluate_patient_scenario(patient_data)
        return jsonify({"ok": True, "assessment": assessment})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/medical-concepts")
def medical_concepts():
    """Get available medical concepts"""
    if not _medical_kb:
        return jsonify({"error": "Medical KB not available"}), 400
    
    concepts = {name: {
        "type": concept.type,
        "definition": concept.definition,
        "criteria": concept.criteria,
        "references": concept.references
    } for name, concept in _medical_kb.concepts.items()}
    
    return jsonify({"ok": True, "concepts": concepts})

@app.route("/treatment-pathways")
def treatment_pathways():
    """Get available clinical pathways"""
    if not _medical_kb:
        return jsonify({"error": "Medical KB not available"}), 400
    
    pathways = {name: {
        "steps": pathway.steps,
        "decision_points": pathway.decision_points
    } for name, pathway in _medical_kb.pathways.items()}
    
    return jsonify({"ok": True, "pathways": pathways})

@app.route("/clear-cache", methods=["POST"])
def clear_cache():
    """Clear the response cache"""
    if _chat:
        _chat.cache = SimpleCache()
        return jsonify({"ok": True, "message": "Cache cleared"})
    return jsonify({"ok": False, "error": "Chat engine not available"})

@app.route("/api-status")
def api_status():
    """Get detailed API status"""
    status = {
        "total_clients": 0,
        "available_clients": 0,
        "current_client": None,
        "mode": "unknown"
    }
    
    if _llm:
        if hasattr(_llm, 'clients'):
            status["total_clients"] = len(_llm.clients)
            status["available_clients"] = len(_llm.clients)
            status["current_client_index"] = _llm.current_client_index
            if _llm.clients:
                current_client = _llm.clients[_llm.current_client_index]
                status["current_client"] = {
                    "type": current_client['type'],
                    "key_id": current_client['key_id']
                }
            status["mode"] = "multi_key"
        elif isinstance(_llm, OfflineClient):
            status["mode"] = "offline"
    
    return jsonify(status)

@app.route("/topics")
def topics():
    return jsonify({
        "topics": [
            "ART Initiation", "AHD Screening", "TB Diagnosis",
            "Laboratory Tests", "Patient Monitoring", "Medication Adherence",
            "Viral Load", "CD4 Count", "Clinical Staging", "Drug Regimens"
        ]
    })
    
@app.route("/sop-sections")
def sop_sections():
    """Get actual SOP sections from the knowledge base"""
    sections = set()
    
    if _kb and hasattr(_kb, '_docs'):
        for doc in _kb._docs:
            text = doc.get('text', '')
            source_id = doc.get('source_id', '')
            
            # Extract SOP sections from content
            if 'SOP' in text and 'Standard Operating Procedure' in text:
                # Look for SOP titles
                sop_match = re.search(r'([A-Z][^.!?]*SOP[^.!?]*[.!?])', text)
                if sop_match:
                    sections.add(sop_match.group(1))
            
            # Also check source IDs for section clues
            if 'sop' in source_id.lower():
                sections.add(source_id.replace('_', ' ').title())
    
    # Fallback to known SOP sections if none found
    if not sections:
        sections = {
            "Advanced HIV Disease (AHD) SOP",
            "ART Initiation Protocol", 
            "TB Diagnosis and Management",
            "Laboratory Testing Procedures",
            "Pharmacy and Drug Management",
            "Patient Monitoring Guidelines",
            "Viral Load Monitoring",
            "CD4 Count Assessment", 
            "Clinical Staging Criteria",
            "Infection Prevention Control",
            "Referral Services Protocol",
            "Client Tracking System",
            "Adolescent Transition Care",
            "Gender-Based Violence Response",
            "HIV Testing Services (HTS)",
            "Index Case Testing",
            "Waste Management SOP",
            "Cervical Cancer Screening"
        }
    
    return jsonify({"sections": sorted(list(sections))})

@app.route("/suggestions")
def suggestions():
    return jsonify({
        "questions": [
            "What is AHD and how is it diagnosed?",
            "When should ART be started for TB patients?",
            "What are the CD4 count criteria for different treatments?",
            "How do you monitor patients on ART?",
            "What is the procedure for viral load testing?"
        ],
        "clinical_scenarios": [
            "35-year-old with CD4 150 and cough - what tests?",
            "Patient with WHO stage 3 and no OIs - when to start ART?",
            "Child age 4 with HIV - what monitoring needed?",
            "Pregnant woman with viral load 5000 - what management?"
        ]
    })

if __name__ == "__main__":
    print("🚀 Starting Enhanced SOPiA Server with Clinical Reasoning...")
    print(f"📚 Knowledge Base: {'Loaded' if _kb else 'Not loaded'}")
    print(f"🧠 Medical KB: {'Loaded' if _medical_kb else 'Not loaded'}")
    print(f"🔬 Clinical Reasoning: {'Available' if _reasoning_engine else 'Unavailable'}")
    
    if _llm:
        if hasattr(_llm, 'clients'):
            print(f"🔑 API Clients: {len(_llm.clients)} available")
        elif isinstance(_llm, OfflineClient):
            print(f"💡 Mode: OFFLINE ONLY")
    
    print(f"💬 Chat Engine: {'Ready' if _chat else 'Not ready'}")
    print(f"💾 Caching: {'Enabled' if _chat else 'Disabled'}")
    print(f"📥 SOP Addition API: /add-sop-text - Ready for new content!")
    
    # Production-ready startup:
    # - Render injects the PORT env var; default to 5050 for local dev
    # - DEBUG is controlled via env (off by default in production)
    port = int(os.getenv("PORT", 5050))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    print(f"🌐 Web Interface: http://0.0.0.0:{port}  (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)