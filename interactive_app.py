# interactive_app.py - Full interactive chat application
import os
import sys
from knowledge_base import SOPKnowledgeBase
from chat_engine import SOPChatEngine
from config import GOOGLE_API_KEY, SOP_FILE_PATH

class InteractiveSOPAssistant:
    def __init__(self):
        self.kb = SOPKnowledgeBase()
        self.chat_engine = None
        self.initialized = False
    
    def initialize(self):
        """Initialize the knowledge base and chat engine"""
        print("🚀 Initializing ACE 5 SOP Assistant...")
        self.kb.initialize_knowledge_base()
        self.chat_engine = SOPChatEngine(self.kb)
        self.initialized = True
        print("✅ Assistant ready! You can now ask questions.")
    
    def display_welcome(self):
        """Display welcome message and available topics"""
        print("\n" + "="*70)
        print("🎯 ACE 5 SOP ASSISTANT - Interactive Chat")
        print("="*70)
        print("I can answer questions about HIV care procedures, guidelines, and protocols.")
        print("\n📋 AVAILABLE TOPICS:")
        
        topics = self.kb.get_available_topics()
        for i, topic in enumerate(topics[:15], 1):
            print(f"  {i}. {topic}")
        
        if len(topics) > 15:
            print(f"  ... and {len(topics) - 15} more topics")
        
        print("\n💡 SUGGESTED QUESTIONS:")
        suggested_questions = self.chat_engine.get_suggested_questions()
        for i, question in enumerate(suggested_questions, 1):
            print(f"  {i}. {question}")
        
        print("\n" + "="*70)
        print("Type 'quit' to exit, 'topics' to see all topics, 'help' for help")
        print("="*70)
    
    def chat_loop(self):
        """Main chat loop"""
        if not self.initialized:
            print("❌ Assistant not initialized. Run initialize() first.")
            return
        
        self.display_welcome()
        
        while True:
            try:
                user_input = input("\n🤔 QUESTION: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Thank you for using ACE 5 SOP Assistant!")
                    break
                
                elif user_input.lower() in ['topics', 'list']:
                    self._show_all_topics()
                
                elif user_input.lower() in ['help', '?']:
                    self._show_help()
                
                elif user_input.lower() in ['stats', 'status']:
                    self._show_stats()
                
                elif user_input:
                    # Process the question
                    print("🔄 Thinking...")
                    response = self.chat_engine.answer_question(user_input)
                    
                    print("\n📝 ANSWER:")
                    print("-" * 50)
                    print(response['answer'])
                    print("-" * 50)
                    
                    if response['sources_used']:
                        print("📚 Sources: " + ", ".join(response['sources_used']))
                    
                    print(f"🎯 Confidence: {response['confidence']}")
                    
                else:
                    print("Please enter a question or type 'help' for options.")
                    
            except KeyboardInterrupt:
                print("\n👋 Session ended by user.")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _show_all_topics(self):
        """Show all available topics"""
        topics = self.kb.get_available_topics()
        print("\n📚 ALL AVAILABLE TOPICS:")
        print("-" * 40)
        for i, topic in enumerate(topics, 1):
            print(f"{i:2d}. {topic}")
    
    def _show_help(self):
        """Show help information"""
        print("\n💡 HELP - Available Commands:")
        print("  [your question] - Ask any question about HIV care procedures")
        print("  topics          - Show all available topics")
        print("  stats           - Show knowledge base statistics")
        print("  help            - Show this help message")
        print("  quit            - Exit the application")
        print("\n💡 Example Questions:")
        print("  - What is the criteria for AHD?")
        print("  - When should I start ART for a client with TB?")
        print("  - How do I track a client who missed appointment?")
        print("  - What tests are needed for AHD screening?")
    
    def _show_stats(self):
        """Show knowledge base statistics"""
        kb_data = self.kb.get_knowledge_base()
        stats = kb_data.get('document_stats', {})
        
        print("\n📊 KNOWLEDGE BASE STATISTICS:")
        print("-" * 30)
        print(f"📚 Topics: {stats.get('topics_count', 'N/A')}")
        print(f"❓ Q&A Pairs: {kb_data.get('total_qa_pairs', 0)}")
        print(f"📊 Tables: {stats.get('tables_processed', 'N/A')}")
        print(f"🔄 Algorithms: {stats.get('algorithms_processed', 'N/A')}")
        print(f"📖 Glossary Terms: {stats.get('glossary_terms', 'N/A')}")
        print(f"🕒 Last Updated: {kb_data.get('last_updated', 'N/A')}")

def main():
    """Main function to run the interactive chat"""
    # Check prerequisites
    if not os.path.exists(SOP_FILE_PATH):
        print(f"❌ Error: SOP file not found at {SOP_FILE_PATH}")
        return
    
    if GOOGLE_API_KEY == "your_google_api_key_here":
        print("❌ Error: Please set your Gemini API key in config.py")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return
    
    # Initialize and run the assistant
    assistant = InteractiveSOPAssistant()
    assistant.initialize()
    assistant.chat_loop()

if __name__ == "__main__":
    main()