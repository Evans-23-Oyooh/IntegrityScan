# Plagiarism Detection System - Configuration Guide

## Overview

This guide explains how to configure and tune the HybridPlagiarismDetector for your specific needs.

## Configuration Parameters

### 1. Algorithm Weights

**Location:** `analyzer/hybrid_plagiarism_detector.py` → `_calculate_similarity()` method

**Current Configuration:**
```python
return (seq * 0.35) + (ngram * 0.30) + (word * 0.20) + (semantic * 0.15)
```

**Presets:**

#### Strict Detection (Catch More Plagiarism)
```python
# Emphasize exact matching
return (seq * 0.50) + (ngram * 0.30) + (word * 0.15) + (semantic * 0.05)
```
- Best for: Academic papers, formal documents
- Catches: Direct copying, minimal paraphrasing
- False positives: Low

#### Balanced Detection (Default)
```python
# Current configuration
return (seq * 0.35) + (ngram * 0.30) + (word * 0.20) + (semantic * 0.15)
```
- Best for: General use
- Catches: Most plagiarism types
- False positives: Moderate

#### Lenient Detection (Catch Less Plagiarism)
```python
# Emphasize semantic similarity
return (seq * 0.20) + (ngram * 0.25) + (word * 0.25) + (semantic * 0.30)
```
- Best for: Creative content, paraphrasing
- Catches: Obvious plagiarism only
- False positives: High

#### Semantic-Focused Detection
```python
# Emphasize meaning-based comparison
return (seq * 0.15) + (ngram * 0.20) + (word * 0.25) + (semantic * 0.40)
```
- Best for: Detecting paraphrased content
- Catches: Meaning-based plagiarism
- False positives: Moderate

### 2. Detection Thresholds

**Location:** `analyzer/views.py` → plagiarism_check() and plagiarism_removal()

**Current Configuration:**
```python
# Plagiarism check
results = detector.detect_plagiarism(text, documents, 0.25)

# Plagiarism removal
original_results = detector.detect_plagiarism(text, documents, 0.15)
```

**Threshold Presets:**

| Threshold | Use Case | Sensitivity | False Positives |
|-----------|----------|-------------|-----------------|
| 0.10 | Very Strict | Very High | Very High |
| 0.15 | Strict | High | High |
| 0.25 | Balanced (Default) | Medium | Medium |
| 0.35 | Lenient | Low | Low |
| 0.50 | Very Lenient | Very Low | Very Low |

**Recommended Thresholds by Use Case:**

```python
# Academic Papers
threshold = 0.20  # Strict

# Blog Posts
threshold = 0.30  # Moderate

# News Articles
threshold = 0.25  # Balanced

# Creative Writing
threshold = 0.40  # Lenient

# Technical Documentation
threshold = 0.15  # Very Strict
```

### 3. N-gram Size

**Location:** `analyzer/hybrid_plagiarism_detector.py` → `_ngram_similarity()` method

**Current Configuration:**
```python
def _ngram_similarity(self, text1, text2, n=4):
```

**N-gram Presets:**

| N-gram | Sensitivity | Use Case |
|--------|-------------|----------|
| 2 (bigrams) | Very High | Short texts, phrases |
| 3 (trigrams) | High | General use |
| 4 (4-grams) | Medium (Default) | Balanced |
| 5 (5-grams) | Low | Long texts |
| 6+ (6-grams) | Very Low | Very long texts |

**Configuration Examples:**

```python
# For short texts (tweets, comments)
def _ngram_similarity(self, text1, text2, n=2):

# For medium texts (paragraphs)
def _ngram_similarity(self, text1, text2, n=3):

# For long texts (articles, papers)
def _ngram_similarity(self, text1, text2, n=5):
```

### 4. Minimum Text Length

**Location:** `analyzer/hybrid_plagiarism_detector.py` → `__init__()` method

**Current Configuration:**
```python
self.min_text_length = 10
```

**Recommended Values:**

```python
# For short texts (tweets, comments)
self.min_text_length = 5

# For medium texts (paragraphs)
self.min_text_length = 20

# For long texts (articles, papers)
self.min_text_length = 50

# For very long texts (books, theses)
self.min_text_length = 100
```

## Configuration Scenarios

### Scenario 1: Academic Paper Plagiarism Detection

**Goal:** Catch all forms of plagiarism in academic papers

**Configuration:**
```python
# In hybrid_plagiarism_detector.py
def _calculate_similarity(self, text1, text2):
    seq = self._sequence_match(text1, text2)
    ngram = self._ngram_similarity(text1, text2, n=4)
    word = self._word_overlap(text1, text2)
    semantic = self._semantic_similarity(text1, text2)
    
    # Strict weights
    return (seq * 0.40) + (ngram * 0.35) + (word * 0.15) + (semantic * 0.10)

self.min_text_length = 50

# In views.py
results = detector.detect_plagiarism(text, documents, threshold=0.20)
```

### Scenario 2: Social Media Content Detection

**Goal:** Detect obvious plagiarism in short posts

**Configuration:**
```python
# In hybrid_plagiarism_detector.py
def _calculate_similarity(self, text1, text2):
    seq = self._sequence_match(text1, text2)
    ngram = self._ngram_similarity(text1, text2, n=2)
    word = self._word_overlap(text1, text2)
    semantic = self._semantic_similarity(text1, text2)
    
    # Lenient weights
    return (seq * 0.30) + (ngram * 0.25) + (word * 0.25) + (semantic * 0.20)

self.min_text_length = 5

# In views.py
results = detector.detect_plagiarism(text, documents, threshold=0.40)
```

### Scenario 3: Paraphrasing Detection

**Goal:** Detect paraphrased content

**Configuration:**
```python
# In hybrid_plagiarism_detector.py
def _calculate_similarity(self, text1, text2):
    seq = self._sequence_match(text1, text2)
    ngram = self._ngram_similarity(text1, text2, n=3)
    word = self._word_overlap(text1, text2)
    semantic = self._semantic_similarity(text1, text2)
    
    # Semantic-focused weights
    return (seq * 0.15) + (ngram * 0.25) + (word * 0.25) + (semantic * 0.35)

self.min_text_length = 30

# In views.py
results = detector.detect_plagiarism(text, documents, threshold=0.35)
```

### Scenario 4: News Article Detection

**Goal:** Detect copied news articles

**Configuration:**
```python
# In hybrid_plagiarism_detector.py
def _calculate_similarity(self, text1, text2):
    seq = self._sequence_match(text1, text2)
    ngram = self._ngram_similarity(text1, text2, n=4)
    word = self._word_overlap(text1, text2)
    semantic = self._semantic_similarity(text1, text2)
    
    # Balanced weights
    return (seq * 0.35) + (ngram * 0.30) + (word * 0.20) + (semantic * 0.15)

self.min_text_length = 100

# In views.py
results = detector.detect_plagiarism(text, documents, threshold=0.25)
```

## Performance Tuning

### Optimize for Speed

```python
# Reduce algorithm complexity
def _calculate_similarity(self, text1, text2):
    # Use only fast algorithms
    seq = self._sequence_match(text1, text2)
    ngram = self._ngram_similarity(text1, text2, n=5)  # Larger n = faster
    
    # Skip semantic analysis
    return (seq * 0.60) + (ngram * 0.40)
```

### Optimize for Accuracy

```python
# Use all algorithms with balanced weights
def _calculate_similarity(self, text1, text2):
    seq = self._sequence_match(text1, text2)
    ngram = self._ngram_similarity(text1, text2, n=3)  # Smaller n = more accurate
    word = self._word_overlap(text1, text2)
    semantic = self._semantic_similarity(text1, text2)
    
    return (seq * 0.25) + (ngram * 0.25) + (word * 0.25) + (semantic * 0.25)
```

### Optimize for Memory

```python
# Reduce stored data
# Use fingerprints instead of full text
fingerprint = detector.get_fingerprint(text)
# Store fingerprint instead of text
```

## Monitoring and Adjustment

### Track Metrics

```python
# Log detection results
import logging

logger = logging.getLogger(__name__)

results = detector.detect_plagiarism(text, documents)
max_similarity = max([r['similarity'] for r in results], default=0)

logger.info(f"Plagiarism check: {max_similarity:.2%}")
```

### Adjust Based on Results

```python
# If too many false positives
threshold = 0.30  # Increase threshold

# If missing plagiarism
threshold = 0.20  # Decrease threshold

# If too slow
n = 5  # Increase n-gram size

# If not accurate enough
n = 3  # Decrease n-gram size
```

## Best Practices

### 1. Start with Defaults
```python
# Use default configuration first
detector = HybridPlagiarismDetector()
results = detector.detect_plagiarism(text, documents, 0.25)
```

### 2. Test with Your Data
```python
# Test with representative samples
test_texts = [
    "Original text",
    "Identical copy",
    "Paraphrased version",
    "Completely different"
]

for text in test_texts:
    results = detector.detect_plagiarism(text, documents)
    print(f"Similarity: {max([r['similarity'] for r in results], default=0):.2%}")
```

### 3. Adjust Gradually
```python
# Make small adjustments
# Test after each change
# Document changes
```

### 4. Monitor Performance
```python
# Track detection accuracy
# Monitor response times
# Collect user feedback
```

### 5. Document Configuration
```python
# Keep notes on why settings were changed
# Document threshold adjustments
# Record performance improvements
```

## Troubleshooting Configuration

### Problem: Too Many False Positives

**Solution:**
1. Increase threshold: `0.25 → 0.30`
2. Reduce semantic weight: `0.15 → 0.05`
3. Increase n-gram size: `4 → 5`

### Problem: Missing Plagiarism

**Solution:**
1. Decrease threshold: `0.25 → 0.20`
2. Increase semantic weight: `0.15 → 0.25`
3. Decrease n-gram size: `4 → 3`

### Problem: Slow Performance

**Solution:**
1. Increase n-gram size: `4 → 5`
2. Skip semantic analysis
3. Reduce reference documents
4. Implement caching

### Problem: Low Accuracy

**Solution:**
1. Decrease n-gram size: `4 → 3`
2. Increase semantic weight: `0.15 → 0.25`
3. Add more reference documents
4. Adjust threshold

## Configuration Checklist

- [ ] Determine use case (academic, social media, etc.)
- [ ] Select appropriate algorithm weights
- [ ] Set detection threshold
- [ ] Configure n-gram size
- [ ] Set minimum text length
- [ ] Test with sample data
- [ ] Monitor performance
- [ ] Document configuration
- [ ] Train team on settings
- [ ] Set up monitoring/logging

## Support

For configuration help:
1. Review this guide
2. Check `PLAGIARISM_DETECTION_GUIDE.md`
3. Run `test_hybrid_detector.py`
4. Contact development team
