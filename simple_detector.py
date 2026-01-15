import re
import hashlib
import sqlite3
from difflib import SequenceMatcher
from collections import Counter
import json
import os

class SimplePlagiarismDetector:
    def __init__(self):
        self.init_database()
        
    def init_database(self):
        self.conn = sqlite3.connect('plagiarism_db.sqlite')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                fingerprint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def preprocess_text(self, text):
        # Simple preprocessing
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        return ' '.join([word for word in words if word not in stop_words])
    
    def generate_fingerprint(self, text):
        return hashlib.md5(self.preprocess_text(text).encode()).hexdigest()
    
    def n_gram_similarity(self, text1, text2, n=3):
        def get_ngrams(text, n):
            words = text.split()
            return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        
        ngrams1 = set(get_ngrams(self.preprocess_text(text1), n))
        ngrams2 = set(get_ngrams(self.preprocess_text(text2), n))
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        return intersection / union if union > 0 else 0.0
    
    def sequence_similarity(self, text1, text2):
        return SequenceMatcher(None, text1, text2).ratio()
    
    def word_overlap_similarity(self, text1, text2):
        words1 = set(self.preprocess_text(text1).split())
        words2 = set(self.preprocess_text(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0
    
    def detect_plagiarism(self, text, threshold=0.7):
        results = []
        
        cursor = self.conn.execute("SELECT title, content FROM documents")
        for title, content in cursor.fetchall():
            similarities = {
                'ngram': self.n_gram_similarity(text, content),
                'sequence': self.sequence_similarity(text, content),
                'word_overlap': self.word_overlap_similarity(text, content)
            }
            
            # Weighted average
            overall_similarity = (
                similarities['ngram'] * 0.4 +
                similarities['sequence'] * 0.3 +
                similarities['word_overlap'] * 0.3
            )
            
            if overall_similarity > threshold:
                results.append({
                    'source': title,
                    'similarity': overall_similarity,
                    'details': similarities,
                    'plagiarized_content': content[:200] + "..."
                })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def add_document(self, title, content):
        fingerprint = self.generate_fingerprint(content)
        self.conn.execute(
            "INSERT INTO documents (title, content, fingerprint) VALUES (?, ?, ?)",
            (title, content, fingerprint)
        )
        self.conn.commit()
        print(f"✅ Document '{title}' added successfully!")
    
    def simple_synonym_replace(self, text):
        # Basic synonym replacement
        synonyms = {
            'good': 'excellent', 'bad': 'poor', 'big': 'large', 'small': 'tiny',
            'fast': 'quick', 'slow': 'gradual', 'happy': 'joyful', 'sad': 'melancholy',
            'important': 'significant', 'easy': 'simple', 'hard': 'difficult',
            'beautiful': 'attractive', 'ugly': 'unattractive', 'smart': 'intelligent'
        }
        
        words = text.split()
        new_words = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in synonyms:
                new_words.append(synonyms[clean_word])
            else:
                new_words.append(word)
        
        return ' '.join(new_words)

def main():
    print("🔍 Simple Plagiarism Detector")
    print("=" * 40)
    
    detector = SimplePlagiarismDetector()
    
    # Add sample documents
    sample_docs = [
        ("Academic Paper 1", "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed for every task."),
        ("Research Article", "Natural language processing involves the interaction between computers and human language, enabling machines to understand, interpret, and generate human text."),
        ("Technical Doc", "Deep learning neural networks consist of multiple layers that can automatically learn hierarchical representations of data through backpropagation.")
    ]
    
    print("Adding sample documents...")
    for title, content in sample_docs:
        detector.add_document(title, content)
    
    while True:
        print("\n" + "=" * 40)
        print("1. Check text for plagiarism")
        print("2. Add new document")
        print("3. Simple text correction")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            text = input("\nEnter text to check: ").strip()
            if text:
                threshold = float(input("Enter threshold (0.1-1.0, default 0.7): ") or "0.7")
                
                print("\n🔍 Checking for plagiarism...")
                results = detector.detect_plagiarism(text, threshold)
                
                if results:
                    print(f"\n⚠️  PLAGIARISM DETECTED! Found {len(results)} matches:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. Source: {result['source']}")
                        print(f"   Similarity: {result['similarity']:.1%}")
                        print(f"   Content: {result['plagiarized_content']}")
                else:
                    print("\n✅ No plagiarism detected!")
        
        elif choice == '2':
            title = input("\nEnter document title: ").strip()
            content = input("Enter document content: ").strip()
            if title and content:
                detector.add_document(title, content)
        
        elif choice == '3':
            text = input("\nEnter text to correct: ").strip()
            if text:
                corrected = detector.simple_synonym_replace(text)
                print(f"\nOriginal: {text}")
                print(f"Corrected: {corrected}")
        
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice!")

if __name__ == '__main__':
    main()