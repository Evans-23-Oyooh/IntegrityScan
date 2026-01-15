#!/usr/bin/env python
"""Test AI detection on AI-generated content"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'textanalyzer.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from analyzer.advanced_hybrid_detector import AdvancedHybridDetector

def test_ai_detection():
    """Test AI detection on various content types"""
    detector = AdvancedHybridDetector()
    
    test_cases = [
        {
            'name': 'AI-Generated Content (Formal)',
            'text': '''The implementation of advanced technological systems has become increasingly prevalent in contemporary society. 
            Furthermore, the integration of artificial intelligence into various sectors has demonstrated significant potential for optimization. 
            Moreover, the utilization of machine learning algorithms has proven to be instrumental in enhancing operational efficiency. 
            In conclusion, the adoption of these technologies is essential for maintaining competitive advantage in the modern marketplace.''',
            'expected': 'High AI Score (>60%)'
        },
        {
            'name': 'Human-Written Content (Casual)',
            'text': '''I really enjoyed the movie last night. It was funny and kept me entertained throughout. 
            The characters were relatable and the plot had some unexpected twists. I'd definitely recommend it to my friends. 
            Overall, it was a great way to spend the evening.''',
            'expected': 'Low AI Score (<30%)'
        },
        {
            'name': 'AI-Generated Content (Academic)',
            'text': '''The phenomenon of climate change represents one of the most pressing challenges confronting contemporary civilization. 
            Consequently, the implementation of sustainable practices has become increasingly imperative. 
            Additionally, the transition towards renewable energy sources demonstrates considerable promise in mitigating environmental degradation. 
            Ultimately, comprehensive policy interventions are requisite for addressing this multifaceted crisis.''',
            'expected': 'High AI Score (>60%)'
        },
        {
            'name': 'Human-Written Content (Personal)',
            'text': '''I woke up this morning feeling pretty tired. Had some coffee and toast for breakfast. 
            Then I went for a walk in the park - it was nice to get some fresh air. 
            Saw some birds and squirrels. Came back home and started working on my project. 
            It's going okay so far, but there's still a lot to do.''',
            'expected': 'Low AI Score (<30%)'
        }
    ]
    
    print("=" * 80)
    print("AI CONTENT DETECTION TEST")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 80)
        
        # Detect AI content
        ai_score = detector._detect_ai_content(test['text'])
        markers = detector._analyze_ai_markers(test['text'])
        
        print(f"Text: {test['text'][:100]}...")
        print(f"\nAI Detection Score: {ai_score:.2%}")
        print(f"Expected: {test['expected']}")
        print(f"Status: {'✓ PASS' if (ai_score > 0.6 and 'High' in test['expected']) or (ai_score < 0.3 and 'Low' in test['expected']) else '✗ FAIL'}")
        
        print(f"\nAI Markers Breakdown:")
        for marker, score in markers.items():
            print(f"  - {marker.replace('_', ' ').title()}: {score:.2%}")
        
        print(f"\nThreshold: 45% (AI if > 45%)")
        print(f"Result: {'AI-Generated' if ai_score > 0.45 else 'Human-Written'}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    test_ai_detection()
