#!/usr/bin/env python3
import argparse
import sys
from plagiarism_detector import PlagiarismDetector
from plagiarism_corrector import PlagiarismCorrector

def main():
    parser = argparse.ArgumentParser(description='Advanced Plagiarism Detector & Corrector')
    parser.add_argument('--text', '-t', help='Text to check/correct')
    parser.add_argument('--file', '-f', help='File containing text to check/correct')
    parser.add_argument('--mode', '-m', choices=['detect', 'correct', 'both'], default='both', help='Operation mode')
    parser.add_argument('--threshold', type=float, default=0.7, help='Plagiarism detection threshold')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--add-doc', help='Add document to database (format: title:content)')
    
    args = parser.parse_args()
    
    detector = PlagiarismDetector()
    corrector = PlagiarismCorrector()
    
    # Add document to database
    if args.add_doc:
        try:
            title, content = args.add_doc.split(':', 1)
            detector.add_document(title.strip(), content.strip())
            print(f"✅ Document '{title}' added to database")
            return
        except ValueError:
            print("❌ Error: Use format 'title:content' for --add-doc")
            return
    
    # Get text input
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{args.file}' not found")
            return
    else:
        print("Enter text to analyze (press Ctrl+D when done):")
        text = sys.stdin.read()
    
    if not text.strip():
        print("❌ Error: No text provided")
        return
    
    results = {}
    
    # Detection
    if args.mode in ['detect', 'both']:
        print("🔍 Detecting plagiarism...")
        detection_results = detector.comprehensive_check(text)
        
        db_scores = [r['similarity'] for r in detection_results['database_results']]
        web_scores = [r['similarity'] for r in detection_results['web_results']]
        all_scores = db_scores + web_scores
        overall_score = max(all_scores) if all_scores else 0.0
        
        results['detection'] = {
            'plagiarism_detected': overall_score > args.threshold,
            'overall_score': overall_score,
            'database_matches': detection_results['database_results'],
            'web_matches': detection_results['web_results']
        }
        
        print(f"\n📊 DETECTION RESULTS:")
        print(f"Overall Score: {overall_score:.1%}")
        print(f"Status: {'⚠️  PLAGIARISM DETECTED' if overall_score > args.threshold else '✅ NO PLAGIARISM'}")
        
        if detection_results['database_matches']:
            print(f"\n📚 Database Matches ({len(detection_results['database_matches'])}):")
            for i, match in enumerate(detection_results['database_matches'][:3], 1):
                print(f"  {i}. {match['source']} - {match['similarity']:.1%}")
        
        if detection_results['web_matches']:
            print(f"\n🌐 Web Matches ({len(detection_results['web_matches'])}):")
            for i, match in enumerate(detection_results['web_matches'][:3], 1):
                print(f"  {i}. {match['url']} - {match['similarity']:.1%}")
    
    # Correction
    if args.mode in ['correct', 'both']:
        print("\n🔧 Generating corrections...")
        corrections = corrector.correct_plagiarism(text)
        results['corrections'] = corrections
        
        print(f"\n📝 CORRECTION SUGGESTIONS:")
        for method, corrected_text in corrections.items():
            print(f"\n{method.upper().replace('_', ' ')}:")
            print(f"  {corrected_text[:200]}{'...' if len(corrected_text) > 200 else ''}")
    
    # Save results
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to {args.output}")

if __name__ == '__main__':
    main()