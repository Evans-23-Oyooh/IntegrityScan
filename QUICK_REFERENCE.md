# Quick Reference Guide - Plagiarism Detection

## Basic Usage

### Import
```python
from analyzer.hybrid_plagiarism_detector import HybridPlagiarismDetector
from analyzer.models import Document
```

### Initialize
```python
detector = HybridPlagiarismDetector()
```

### Detect Plagiarism
```python
# Get all reference documents
documents = Document.objects.all()

# Detect with default threshold (0.25)
results = detector.detect_plagiarism(text, documents)

# Detect with custom threshold
results = detector.detect_plagiarism(text, documents, threshold=0.3)
```

### Process Results
```python
for result in results:
    print(f"Title: {result['title']}")
    print(f"Similarity: {result['similarity']:.2%}")
    print(f"Sequence Match: {result['details']['sequence_match']:.2%}")
    print(f"N-gram Match: {result['details']['ngram_match']:.2%}")
    print(f"Word Overlap: {result['details']['word_overlap']:.2%}")
    print(f"Semantic: {result['details']['semantic_similarity']:.2%}")
```

## Advanced Usage

### Get Detailed Report
```python
report = detector.get_detailed_report(text, documents)

# Report structure:
# {
#     'status': 'clean' | 'suspicious' | 'plagiarized',
#     'plagiarism_percentage': float,
#     'matches': [list of results],
#     'recommendation': str
# }

print(f"Status: {report['status']}")
print(f"Plagiarism: {report['plagiarism_percentage']:.1f}%")
print(f"Recommendation: {report['recommendation']}")
```

### Generate Fingerprint
```python
fingerprint = detector.get_fingerprint(text)
# Use for fast comparison or storage
```

### Individual Algorithm Scores
```python
seq = detector._sequence_match(text1, text2)
ngram = detector._ngram_similarity(text1, text2)
word = detector._word_overlap(text1, text2)
semantic = detector._semantic_similarity(text1, text2)

print(f"Sequence: {seq:.2%}")
print(f"N-gram: {ngram:.2%}")
print(f"Word: {word:.2%}")
print(f"Semantic: {semantic:.2%}")
```

## Score Interpretation

| Score | Interpretation | Action |
|-------|-----------------|--------|
| 0.00 - 0.25 | Original | Accept |
| 0.25 - 0.50 | Suspicious | Review |
| 0.50 - 0.75 | Likely Plagiarized | Investigate |
| 0.75 - 1.00 | Highly Plagiarized | Reject |

## Common Scenarios

### Scenario 1: Check Single Text
```python
detector = HybridPlagiarismDetector()
documents = Document.objects.all()
results = detector.detect_plagiarism(user_text, documents, 0.25)

if results and results[0]['similarity'] > 0.5:
    print("Plagiarism detected!")
else:
    print("Text appears original")
```

### Scenario 2: Batch Processing
```python
detector = HybridPlagiarismDetector()
documents = Document.objects.all()

texts = [text1, text2, text3]
for text in texts:
    results = detector.detect_plagiarism(text, documents, 0.25)
    print(f"Similarity: {max([r['similarity'] for r in results], default=0):.2%}")
```

### Scenario 3: Compare Two Texts
```python
detector = HybridPlagiarismDetector()

# Create temporary document
from analyzer.models import Document
temp_doc = Document(title="Reference", content=reference_text)

results = detector.detect_plagiarism(test_text, [temp_doc], 0.0)
similarity = results[0]['similarity'] if results else 0

print(f"Similarity: {similarity:.2%}")
```

### Scenario 4: Get Detailed Analysis
```python
detector = HybridPlagiarismDetector()
documents = Document.objects.all()

results = detector.detect_plagiarism(text, documents, 0.25)

if results:
    top_match = results[0]
    print(f"Match: {top_match['title']}")
    print(f"Overall: {top_match['similarity']:.2%}")
    print(f"Breakdown:")
    for algo, score in top_match['details'].items():
        print(f"  {algo}: {score:.2%}")
```

## Configuration

### Change Default Threshold
```python
# In views.py
detector = HybridPlagiarismDetector()
results = detector.detect_plagiarism(text, documents, 0.30)  # 30% threshold
```

### Adjust Algorithm Weights
```python
# In hybrid_plagiarism_detector.py
def _calculate_similarity(self, text1, text2):
    seq = self._sequence_match(text1, text2)
    ngram = self._ngram_similarity(text1, text2)
    word = self._word_overlap(text1, text2)
    semantic = self._semantic_similarity(text1, text2)
    
    # Modify weights (must sum to 1.0)
    return (seq * 0.40) + (ngram * 0.30) + (word * 0.20) + (semantic * 0.10)
```

### Change N-gram Size
```python
# In hybrid_plagiarism_detector.py
def _ngram_similarity(self, text1, text2, n=5):  # Changed from 4 to 5
    # Larger n = less sensitive
    # Smaller n = more sensitive
```

## Performance Tips

1. **Cache Results**
   ```python
   from django.core.cache import cache
   
   cache_key = f"plagiarism_{fingerprint}"
   results = cache.get(cache_key)
   if not results:
       results = detector.detect_plagiarism(text, documents)
       cache.set(cache_key, results, 3600)  # Cache for 1 hour
   ```

2. **Batch Processing**
   ```python
   # Process multiple texts efficiently
   documents = Document.objects.all()
   for text in texts:
       results = detector.detect_plagiarism(text, documents, 0.25)
   ```

3. **Limit Reference Documents**
   ```python
   # Use only relevant documents
   documents = Document.objects.filter(category=user_category)
   results = detector.detect_plagiarism(text, documents)
   ```

## Troubleshooting

### Issue: No Results Returned
```python
# Check if text is long enough
if len(text.strip()) < 10:
    print("Text too short")

# Check threshold
results = detector.detect_plagiarism(text, documents, 0.0)  # Lower threshold
```

### Issue: All Texts Match
```python
# Increase threshold
results = detector.detect_plagiarism(text, documents, 0.5)  # Higher threshold

# Check reference documents
print(f"Documents: {Document.objects.count()}")
```

### Issue: Slow Performance
```python
# Reduce documents
documents = Document.objects.filter(category=category)[:100]
results = detector.detect_plagiarism(text, documents)

# Use fingerprints for pre-filtering
fingerprint = detector.get_fingerprint(text)
```

## Testing

### Run Tests
```bash
python test_hybrid_detector.py
```

### Manual Test
```python
from analyzer.hybrid_plagiarism_detector import HybridPlagiarismDetector

detector = HybridPlagiarismDetector()

# Test identical text
text = "The quick brown fox jumps over the lazy dog"
similarity = detector._calculate_similarity(text, text)
print(f"Identical: {similarity:.2%}")  # Should be ~1.0

# Test different text
text1 = "The quick brown fox"
text2 = "Machine learning is great"
similarity = detector._calculate_similarity(text1, text2)
print(f"Different: {similarity:.2%}")  # Should be ~0.0
```

## API Reference

### HybridPlagiarismDetector

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `detect_plagiarism()` | text, documents, threshold | list | Detect plagiarism |
| `get_detailed_report()` | text, documents | dict | Get comprehensive report |
| `get_fingerprint()` | text | str | Generate document fingerprint |
| `_calculate_similarity()` | text1, text2 | float | Calculate weighted similarity |
| `_sequence_match()` | text1, text2 | float | Sequence matching score |
| `_ngram_similarity()` | text1, text2, n | float | N-gram similarity score |
| `_word_overlap()` | text1, text2 | float | Word overlap score |
| `_semantic_similarity()` | text1, text2 | float | Semantic similarity score |

## Examples

### Example 1: Simple Check
```python
from analyzer.hybrid_plagiarism_detector import HybridPlagiarismDetector
from analyzer.models import Document

detector = HybridPlagiarismDetector()
documents = Document.objects.all()
results = detector.detect_plagiarism("Your text here", documents)

if results and results[0]['similarity'] > 0.5:
    print("Plagiarism detected!")
```

### Example 2: Detailed Analysis
```python
detector = HybridPlagiarismDetector()
documents = Document.objects.all()
report = detector.get_detailed_report("Your text", documents)

print(f"Status: {report['status']}")
print(f"Plagiarism: {report['plagiarism_percentage']:.1f}%")
for match in report['matches'][:3]:
    print(f"  - {match['title']}: {match['similarity']:.2%}")
```

### Example 3: Comparison
```python
detector = HybridPlagiarismDetector()

text1 = "Original text here"
text2 = "Original text here"  # Identical

similarity = detector._calculate_similarity(text1, text2)
print(f"Similarity: {similarity:.2%}")  # ~1.0
```

## Support

For issues or questions:
1. Check `PLAGIARISM_DETECTION_GUIDE.md`
2. Review test results: `python test_hybrid_detector.py`
3. Check algorithm details in source code
4. Contact development team
