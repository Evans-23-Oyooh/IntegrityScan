#!/usr/bin/env python
"""Test script for HybridPlagiarismDetector"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'textanalyzer.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from analyzer.hybrid_plagiarism_detector import HybridPlagiarismDetector
from analyzer.models import Document

def test_detector():
    """Test the plagiarism detector with various scenarios"""
    detector = HybridPlagiarismDetector()
    
    # Test cases
    test_cases = [
        {
            'name': 'Identical Text',
            'text1': 'The quick brown fox jumps over the lazy dog',
            'text2': 'The quick brown fox jumps over the lazy dog',
            'expected': 'High (>0.9)'
        },
        {
            'name': 'Completely Different',
            'text1': 'The quick brown fox jumps over the lazy dog',
            'text2': 'Machine learning is a subset of artificial intelligence',
            'expected': 'Low (<0.2)'
        },
        {
            'name': 'Paraphrased Text',
            'text1': 'The quick brown fox jumps over the lazy dog',
            'text2': 'A fast brown fox leaps across a sleeping dog',
            'expected': 'Medium (0.4-0.7)'
        },
        {
            'name': 'Partial Copy',
            'text1': 'The quick brown fox jumps over the lazy dog and runs away',
            'text2': 'The quick brown fox jumps over the lazy dog',
            'expected': 'High (>0.7)'
        }
    ]
    
    print("=" * 80)
    print("PLAGIARISM DETECTOR TEST SUITE")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 80)
        
        # Calculate similarity
        similarity = detector._calculate_similarity(test['text1'], test['text2'])
        
        # Get detailed breakdown
        seq = detector._sequence_match(test['text1'], test['text2'])
        ngram = detector._ngram_similarity(test['text1'], test['text2'])
        word = detector._word_overlap(test['text1'], test['text2'])
        semantic = detector._semantic_similarity(test['text1'], test['text2'])
        
        print(f"Text 1: {test['text1'][:50]}...")
        print(f"Text 2: {test['text2'][:50]}...")
        print(f"\nSimilarity Scores:")
        print(f"  - Sequence Match:      {seq:.2%}")
        print(f"  - N-gram Analysis:     {ngram:.2%}")
        print(f"  - Word Overlap:        {word:.2%}")
        print(f"  - Semantic Similarity: {semantic:.2%}")
        print(f"\nWeighted Score: {similarity:.2%}")
        print(f"Expected Range: {test['expected']}")
        print(f"Status: {'✓ PASS' if 0 <= similarity <= 1 else '✗ FAIL'}")
    
    print("\n" + "=" * 80)
    print("DATABASE COMPARISON TEST")
    print("=" * 80)
    
    # Test with database documents
    documents = Document.objects.all()
    if documents.exists():
        test_text = "Machine learning is a powerful technology for data analysis"
        results = detector.detect_plagiarism(test_text, documents, 0.25)
        
        print(f"\nTest Text: {test_text}")
        print(f"Documents in Database: {documents.count()}")
        print(f"Matches Found (threshold 0.25): {len(results)}")
        
        if results:
            print("\nTop Matches:")
            for i, result in enumerate(results[:3], 1):
                print(f"\n  {i}. {result['title']}")
                print(f"     Similarity: {result['similarity']:.2%}")
                print(f"     Details:")
                for key, val in result['details'].items():
                    if isinstance(val, (int, float)):
                        print(f"       - {key}: {val:.2%}")
    else:
        print("\nNo documents in database. Add some documents first.")
    
    print("\n" + "=" * 80)
    print("FINGERPRINT TEST")
    print("=" * 80)
    
    text = "The quick brown fox jumps over the lazy dog"
    fingerprint = detector.get_fingerprint(text)
    print(f"\nText: {text}")
    print(f"Fingerprint: {fingerprint}")
    print(f"Fingerprint Length: {len(fingerprint)} characters")
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80)

if __name__ == '__main__':
    test_detector()
