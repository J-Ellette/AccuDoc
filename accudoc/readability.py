"""
Readability metrics analyzer for AccuDoc.

Calculates various readability scores for documentation:
- Flesch Reading Ease
- Flesch-Kincaid Grade Level
- Gunning Fog Index
- SMOG Index
- Coleman-Liau Index
- Automated Readability Index (ARI)
"""

import re
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import math


class ReadabilityAnalyzer:
    """Analyzes readability of documentation."""
    
    def __init__(self):
        """Initialize readability analyzer."""
        self.logger = logging.getLogger('accudoc.readability')
        
    def _count_syllables(self, word: str) -> int:
        """
        Count syllables in a word using a simple heuristic.
        
        Args:
            word: Word to count syllables in
            
        Returns:
            Estimated syllable count
        """
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1
            
        return syllable_count
    
    def _extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Args:
            text: Text to extract sentences from
            
        Returns:
            List of sentences
        """
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        
        # Remove URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'[*_#\[\]()]', ' ', text)
        
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        
        # Filter out empty sentences and very short ones
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def _extract_words(self, text: str) -> List[str]:
        """
        Extract words from text.
        
        Args:
            text: Text to extract words from
            
        Returns:
            List of words
        """
        # Remove punctuation and split
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return [w.lower() for w in words if len(w) > 0]
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and calculate readability metrics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with readability metrics
        """
        sentences = self._extract_sentences(text)
        all_words = self._extract_words(text)
        
        if not sentences or not all_words:
            return {
                'error': 'Insufficient text for analysis',
                'sentences': 0,
                'words': 0
            }
        
        # Basic counts
        sentence_count = len(sentences)
        word_count = len(all_words)
        
        # Count syllables and complex words
        syllable_count = sum(self._count_syllables(word) for word in all_words)
        complex_word_count = sum(1 for word in all_words if self._count_syllables(word) >= 3)
        
        # Count characters (excluding spaces)
        char_count = sum(len(word) for word in all_words)
        
        # Calculate averages
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
        avg_chars_per_word = char_count / word_count if word_count > 0 else 0
        
        # Calculate readability scores
        scores = {}
        
        # Flesch Reading Ease (0-100, higher is easier)
        # Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        scores['flesch_reading_ease'] = max(0, min(100, 
            206.835 - 1.015 * avg_words_per_sentence - 84.6 * avg_syllables_per_word
        ))
        
        # Flesch-Kincaid Grade Level
        # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        scores['flesch_kincaid_grade'] = max(0,
            0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
        )
        
        # Gunning Fog Index
        # Formula: 0.4 * ((words/sentences) + 100 * (complex_words/words))
        complex_word_percentage = (complex_word_count / word_count * 100) if word_count > 0 else 0
        scores['gunning_fog'] = 0.4 * (avg_words_per_sentence + complex_word_percentage)
        
        # SMOG Index
        # Formula: 1.0430 * sqrt(polysyllable_count * (30/sentences)) + 3.1291
        if sentence_count >= 30:
            polysyllable_count = sum(1 for word in all_words if self._count_syllables(word) >= 3)
            scores['smog_index'] = 1.0430 * math.sqrt(polysyllable_count * (30 / sentence_count)) + 3.1291
        else:
            scores['smog_index'] = None  # SMOG requires at least 30 sentences
        
        # Coleman-Liau Index
        # Formula: 0.0588 * L - 0.296 * S - 15.8
        # L = average letters per 100 words, S = average sentences per 100 words
        L = (char_count / word_count) * 100 if word_count > 0 else 0
        S = (sentence_count / word_count) * 100 if word_count > 0 else 0
        scores['coleman_liau'] = 0.0588 * L - 0.296 * S - 15.8
        
        # Automated Readability Index (ARI)
        # Formula: 4.71 * (chars/words) + 0.5 * (words/sentences) - 21.43
        scores['ari'] = 4.71 * avg_chars_per_word + 0.5 * avg_words_per_sentence - 21.43
        
        return {
            'statistics': {
                'sentences': sentence_count,
                'words': word_count,
                'syllables': syllable_count,
                'complex_words': complex_word_count,
                'characters': char_count,
                'avg_words_per_sentence': avg_words_per_sentence,
                'avg_syllables_per_word': avg_syllables_per_word,
                'avg_chars_per_word': avg_chars_per_word
            },
            'scores': scores
        }
    
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Analyze readability of a documentation file.
        
        Args:
            filepath: Path to file
            
        Returns:
            Readability analysis
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            result = self.analyze_text(content)
            result['file'] = str(filepath)
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {filepath}: {e}")
            return {'file': str(filepath), 'error': str(e)}
    
    def analyze_directory(self, dirpath: Path, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze readability of all documentation files in a directory.
        
        Args:
            dirpath: Directory path
            extensions: File extensions to analyze (default: .md, .txt, .rst)
            
        Returns:
            List of analysis results
        """
        if extensions is None:
            extensions = ['.md', '.txt', '.rst', '.markdown']
        
        results = []
        for ext in extensions:
            for filepath in dirpath.rglob(f'*{ext}'):
                result = self.analyze_file(filepath)
                if 'error' not in result or 'statistics' in result:
                    results.append(result)
        
        return results
    
    def interpret_score(self, score_name: str, score_value: float) -> str:
        """
        Interpret a readability score.
        
        Args:
            score_name: Name of the score
            score_value: Score value
            
        Returns:
            Human-readable interpretation
        """
        if score_name == 'flesch_reading_ease':
            if score_value >= 90:
                return "Very Easy (5th grade)"
            elif score_value >= 80:
                return "Easy (6th grade)"
            elif score_value >= 70:
                return "Fairly Easy (7th grade)"
            elif score_value >= 60:
                return "Standard (8th-9th grade)"
            elif score_value >= 50:
                return "Fairly Difficult (10th-12th grade)"
            elif score_value >= 30:
                return "Difficult (College)"
            else:
                return "Very Difficult (College graduate)"
        
        elif score_name in ['flesch_kincaid_grade', 'gunning_fog', 'smog_index', 'coleman_liau', 'ari']:
            grade = int(score_value)
            if grade <= 6:
                return f"Elementary (Grade {grade})"
            elif grade <= 8:
                return f"Middle School (Grade {grade})"
            elif grade <= 12:
                return f"High School (Grade {grade})"
            elif grade <= 16:
                return f"College (Year {grade - 12})"
            else:
                return "Graduate Level"
        
        return "Unknown"
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate markdown report from readability analysis.
        
        Args:
            results: List of analysis results
            
        Returns:
            Markdown formatted report
        """
        if not results:
            return "# Readability Report\n\nNo documentation files analyzed."
        
        md = []
        md.append("# Documentation Readability Report\n")
        
        # Overall statistics
        total_words = sum(r['statistics']['words'] for r in results if 'statistics' in r)
        total_sentences = sum(r['statistics']['sentences'] for r in results if 'statistics' in r)
        
        md.append(f"**Files analyzed**: {len(results)}")
        md.append(f"**Total words**: {total_words:,}")
        md.append(f"**Total sentences**: {total_sentences:,}\n")
        
        # Calculate average scores
        avg_scores = {}
        score_names = ['flesch_reading_ease', 'flesch_kincaid_grade', 'gunning_fog', 'coleman_liau', 'ari']
        
        for score_name in score_names:
            scores = [r['scores'][score_name] for r in results if 'scores' in r and score_name in r['scores'] and r['scores'][score_name] is not None]
            if scores:
                avg_scores[score_name] = sum(scores) / len(scores)
        
        # Overall readability assessment
        md.append("## Overall Readability\n")
        
        if 'flesch_reading_ease' in avg_scores:
            fre = avg_scores['flesch_reading_ease']
            interpretation = self.interpret_score('flesch_reading_ease', fre)
            md.append(f"**Flesch Reading Ease**: {fre:.1f} - {interpretation}")
        
        if 'flesch_kincaid_grade' in avg_scores:
            fkg = avg_scores['flesch_kincaid_grade']
            interpretation = self.interpret_score('flesch_kincaid_grade', fkg)
            md.append(f"**Flesch-Kincaid Grade**: {fkg:.1f} - {interpretation}")
        
        if 'gunning_fog' in avg_scores:
            gf = avg_scores['gunning_fog']
            interpretation = self.interpret_score('gunning_fog', gf)
            md.append(f"**Gunning Fog Index**: {gf:.1f} - {interpretation}")
        
        md.append("")
        
        # Per-file analysis
        if len(results) > 1:
            md.append("## File-by-File Analysis\n")
            md.append("| File | Words | Flesch RE | Grade Level |")
            md.append("|------|-------|-----------|-------------|")
            
            for result in sorted(results, key=lambda x: x.get('statistics', {}).get('words', 0), reverse=True)[:10]:
                if 'statistics' not in result:
                    continue
                
                filename = Path(result['file']).name
                words = result['statistics']['words']
                fre = result['scores'].get('flesch_reading_ease', 0)
                grade = result['scores'].get('flesch_kincaid_grade', 0)
                
                md.append(f"| {filename} | {words} | {fre:.0f} | {grade:.1f} |")
            
            md.append("")
        
        # Recommendations
        md.append("## Recommendations\n")
        
        if avg_scores.get('flesch_reading_ease', 100) < 60:
            md.append("- ⚠️ Documentation may be difficult to read")
            md.append("- Consider simplifying complex sentences")
            md.append("- Use shorter words where possible")
        else:
            md.append("- ✓ Documentation readability is good")
        
        if avg_scores.get('flesch_kincaid_grade', 0) > 12:
            md.append("- ⚠️ Grade level is quite high (college+)")
            md.append("- Target 8th-10th grade level for broader accessibility")
        
        md.append("\n**Note**: Technical documentation naturally scores lower due to specialized terminology.")
        md.append("Focus on clarity and organization rather than achieving perfect readability scores.\n")
        
        return '\n'.join(md)
