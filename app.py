from flask import Flask, render_template, request, jsonify
import json
from plagiarism_detector import PlagiarismDetector
from plagiarism_corrector import PlagiarismCorrector

app = Flask(__name__)
detector = PlagiarismDetector()
corrector = PlagiarismCorrector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_plagiarism():
    data = request.json
    text = data.get('text', '')
    threshold = float(data.get('threshold', 0.7))
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Comprehensive plagiarism check
    results = detector.comprehensive_check(text)
    
    # Calculate overall plagiarism score
    db_scores = [r['similarity'] for r in results['database_results']]
    web_scores = [r['similarity'] for r in results['web_results']]
    all_scores = db_scores + web_scores
    
    overall_score = max(all_scores) if all_scores else 0.0
    
    return jsonify({
        'plagiarism_detected': overall_score > threshold,
        'overall_score': overall_score,
        'database_matches': results['database_results'],
        'web_matches': results['web_results'],
        'fingerprint': results['fingerprint']
    })

@app.route('/correct', methods=['POST'])
def correct_plagiarism():
    data = request.json
    text = data.get('text', '')
    methods = data.get('methods', ['synonym', 'restructure', 'paraphrase'])
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # First detect plagiarism
    detection_results = detector.comprehensive_check(text)
    plagiarized_parts = detection_results['database_results'] + detection_results['web_results']
    
    # Generate corrections
    corrections = corrector.correct_plagiarism(text, methods)
    
    # Generate specific suggestions for plagiarized parts
    suggestions = corrector.suggest_improvements(text, plagiarized_parts[:3])  # Top 3 matches
    
    return jsonify({
        'original_text': text,
        'corrections': corrections,
        'specific_suggestions': suggestions,
        'plagiarism_score': max([p['similarity'] for p in plagiarized_parts]) if plagiarized_parts else 0.0
    })

@app.route('/add_document', methods=['POST'])
def add_document():
    data = request.json
    title = data.get('title', '')
    content = data.get('content', '')
    
    if not title or not content:
        return jsonify({'error': 'Title and content required'}), 400
    
    detector.add_document(title, content)
    return jsonify({'message': 'Document added successfully'})

@app.route('/batch_check', methods=['POST'])
def batch_check():
    data = request.json
    texts = data.get('texts', [])
    threshold = float(data.get('threshold', 0.7))
    
    results = []
    for i, text in enumerate(texts):
        result = detector.comprehensive_check(text)
        db_scores = [r['similarity'] for r in result['database_results']]
        web_scores = [r['similarity'] for r in result['web_results']]
        all_scores = db_scores + web_scores
        overall_score = max(all_scores) if all_scores else 0.0
        
        results.append({
            'index': i,
            'text_preview': text[:100] + "..." if len(text) > 100 else text,
            'plagiarism_detected': overall_score > threshold,
            'overall_score': overall_score,
            'matches_count': len(result['database_results']) + len(result['web_results'])
        })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    # Add some sample documents for testing
    sample_docs = [
        ("Sample Academic Paper", "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed."),
        ("Research Article", "Natural language processing involves the interaction between computers and human language, enabling machines to understand and interpret text."),
        ("Technical Documentation", "Deep learning neural networks consist of multiple layers that can automatically learn hierarchical representations of data.")
    ]
    
    for title, content in sample_docs:
        detector.add_document(title, content)
    
    app.run(debug=True, host='0.0.0.0', port=5000)