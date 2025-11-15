"""
Style guide enforcement for AccuDoc documentation.

Validates documentation against popular style guides including:
- Google Developer Documentation Style Guide
- Microsoft Writing Style Guide
- Plain Language guidelines
"""

import re
from typing import List, Dict, Optional, Set
from pathlib import Path
from abc import ABC, abstractmethod

from accudoc.doc_validator import ValidationRule, ValidationIssue


class StyleGuide(ABC):
    """Base class for style guides."""
    
    def __init__(self):
        """Initialize style guide."""
        self.rules: List[ValidationRule] = []
        self._initialize_rules()
    
    @abstractmethod
    def _initialize_rules(self):
        """Initialize style guide rules."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get style guide name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get style guide description."""
        pass
    
    def get_rules(self) -> List[ValidationRule]:
        """Get all rules in this style guide."""
        return self.rules


class GoogleStyleGuide(StyleGuide):
    """Google Developer Documentation Style Guide."""
    
    @property
    def name(self) -> str:
        return "Google Developer Documentation Style Guide"
    
    @property
    def description(self) -> str:
        return "Best practices from Google's technical writing guidelines"
    
    def _initialize_rules(self):
        """Initialize Google style guide rules."""
        
        # Avoid "please" in instructions
        self.rules.append(AvoidPleaseRule())
        
        # Use present tense
        self.rules.append(PreferPresentTenseRule())
        
        # Use active voice
        self.rules.append(PreferActiveVoiceRule())
        
        # Use second person (you) rather than first person (we)
        self.rules.append(UseSecondPersonRule())
        
        # Avoid exclamation marks
        self.rules.append(AvoidExclamationMarksRule())
        
        # Use contractions sparingly in formal docs
        self.rules.append(AvoidContractionsRule(severity='info'))


class MicrosoftStyleGuide(StyleGuide):
    """Microsoft Writing Style Guide."""
    
    @property
    def name(self) -> str:
        return "Microsoft Writing Style Guide"
    
    @property
    def description(self) -> str:
        return "Microsoft's style guidelines for technical documentation"
    
    def _initialize_rules(self):
        """Initialize Microsoft style guide rules."""
        
        # Be concise - avoid wordy phrases
        self.rules.append(AvoidWordyPhrasesRule())
        
        # Use positive phrasing
        self.rules.append(UsePositivePhrasingRule())
        
        # Avoid "should" in most contexts
        self.rules.append(AvoidShouldRule())
        
        # Use consistent terminology
        self.rules.append(ConsistentTerminologyRule())
        
        # Avoid culture-specific references
        self.rules.append(AvoidCultureSpecificRule())


class PlainLanguageGuide(StyleGuide):
    """Plain Language guidelines for clear communication."""
    
    @property
    def name(self) -> str:
        return "Plain Language Guidelines"
    
    @property
    def description(self) -> str:
        return "Federal Plain Language Guidelines for clear communication"
    
    def _initialize_rules(self):
        """Initialize Plain Language rules."""
        
        # Use short sentences
        self.rules.append(ShortSentencesRule())
        
        # Avoid jargon
        self.rules.append(AvoidJargonRule())
        
        # Use common words
        self.rules.append(UseCommonWordsRule())
        
        # Avoid nominalization
        self.rules.append(AvoidNominalizationRule())


# Rule implementations for Google Style Guide

class AvoidPleaseRule(ValidationRule):
    """Avoid using 'please' in instructions (Google style)."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True, 
                 config: Optional[Dict] = None):
        super().__init__('avoid-please', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Avoid using 'please' in instructions (Google style)"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith('```') or line.strip().startswith('    '):
                continue
            
            if re.search(r'\bplease\b', line, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=self.severity,
                    category='custom',
                    message='Avoid "please" in instructions (Google style: be direct)',
                    line_number=line_num,
                    context=line.strip(),
                    rule_id=self.rule_id
                ))
        
        return issues


class PreferPresentTenseRule(ValidationRule):
    """Prefer present tense over future tense."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('prefer-present-tense', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Prefer present tense (e.g., 'returns' not 'will return')"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        # Common future tense patterns
        future_patterns = [
            (r'\bwill\s+\w+', 'will + verb'),
            (r'\bgoing\s+to\s+\w+', 'going to + verb'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks and headers
            if line.strip().startswith(('```', '    ', '#')):
                continue
            
            for pattern, description in future_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Consider using present tense instead of "{description}"',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
                    break
        
        return issues


class PreferActiveVoiceRule(ValidationRule):
    """Prefer active voice over passive voice."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('prefer-active-voice', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Prefer active voice over passive voice"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        # Common passive voice patterns
        passive_patterns = [
            r'\bis\s+\w+ed\b',
            r'\bare\s+\w+ed\b',
            r'\bwas\s+\w+ed\b',
            r'\bwere\s+\w+ed\b',
            r'\bbeen\s+\w+ed\b',
            r'\bbe\s+\w+ed\b',
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            for pattern in passive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message='Consider using active voice instead of passive voice',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
                    break
        
        return issues


class UseSecondPersonRule(ValidationRule):
    """Use second person (you) rather than first person (we)."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('use-second-person', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Use second person (you) rather than first person (we)"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks and headers
            if line.strip().startswith(('```', '    ', '#')):
                continue
            
            # Look for first person plural
            if re.search(r'\b(we|our|us)\b', line, re.IGNORECASE):
                # Skip if it's in a quote or example
                if '"' in line or "'" in line:
                    continue
                
                issues.append(ValidationIssue(
                    severity=self.severity,
                    category='custom',
                    message='Consider using second person (you) instead of first person (we)',
                    line_number=line_num,
                    context=line.strip()[:100],
                    rule_id=self.rule_id
                ))
        
        return issues


class AvoidExclamationMarksRule(ValidationRule):
    """Avoid excessive exclamation marks in formal documentation."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('avoid-exclamation-marks', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Avoid exclamation marks in formal documentation"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            if '!' in line:
                count = line.count('!')
                if count >= 2:
                    issues.append(ValidationIssue(
                        severity='warning',
                        category='custom',
                        message=f'Excessive exclamation marks ({count}) - keep documentation professional',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
                else:
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message='Avoid exclamation marks in formal documentation',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
        
        return issues


class AvoidContractionsRule(ValidationRule):
    """Avoid contractions in formal documentation."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('avoid-contractions', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Avoid contractions in formal documentation"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        contractions = [
            "don't", "doesn't", "didn't", "won't", "wouldn't", "shouldn't",
            "can't", "couldn't", "isn't", "aren't", "wasn't", "weren't",
            "hasn't", "haven't", "hadn't", "it's", "that's", "there's",
            "you're", "they're", "we're", "i'm"
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            lower_line = line.lower()
            for contraction in contractions:
                if contraction in lower_line:
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Avoid contraction "{contraction}" in formal documentation',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
                    break
        
        return issues


# Rule implementations for Microsoft Style Guide

class AvoidWordyPhrasesRule(ValidationRule):
    """Avoid wordy phrases - be concise."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('avoid-wordy-phrases', severity, enabled, config)
        
        # Wordy phrases and their concise alternatives
        self.wordy_phrases = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'for the purpose of': 'to',
            'at this point in time': 'now',
            'with the exception of': 'except',
            'in the event that': 'if',
            'make use of': 'use',
            'prior to': 'before',
            'subsequent to': 'after',
        }
    
    @property
    def description(self) -> str:
        return "Avoid wordy phrases - be concise (Microsoft style)"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            lower_line = line.lower()
            for wordy, concise in self.wordy_phrases.items():
                if wordy in lower_line:
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Replace "{wordy}" with "{concise}" for conciseness',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
        
        return issues


class UsePositivePhrasingRule(ValidationRule):
    """Use positive phrasing rather than negative."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('use-positive-phrasing', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Use positive phrasing rather than negative"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        negative_patterns = [
            (r'\bdoesn\'t\s+work\b', 'fails'),
            (r'\bdon\'t\s+use\b', 'avoid'),
            (r'\bnot\s+recommended\b', 'avoid'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            for pattern, _ in negative_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message='Consider using positive phrasing',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
                    break
        
        return issues


class AvoidShouldRule(ValidationRule):
    """Avoid 'should' - be more direct."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('avoid-should', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Avoid 'should' - use 'must' or 'can' instead"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks and headers
            if line.strip().startswith(('```', '    ', '#')):
                continue
            
            if re.search(r'\bshould\b', line, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=self.severity,
                    category='custom',
                    message='Replace "should" with "must" (required) or "can" (optional)',
                    line_number=line_num,
                    context=line.strip()[:100],
                    rule_id=self.rule_id
                ))
        
        return issues


class ConsistentTerminologyRule(ValidationRule):
    """Use consistent terminology throughout documentation."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('consistent-terminology', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Use consistent terminology (e.g., don't mix 'user' and 'person')"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        
        # Check for inconsistent terms
        inconsistent_pairs = [
            (['username', 'user name'], 'username or user name'),
            (['email', 'e-mail'], 'email or e-mail'),
            (['login', 'log in', 'log-in'], 'login/log in'),
        ]
        
        content_lower = content.lower()
        for terms, description in inconsistent_pairs:
            found_terms = [term for term in terms if term in content_lower]
            if len(found_terms) > 1:
                issues.append(ValidationIssue(
                    severity=self.severity,
                    category='custom',
                    message=f'Inconsistent terminology: {description} - choose one',
                    line_number=None,
                    context=f'Found: {", ".join(found_terms)}',
                    rule_id=self.rule_id
                ))
        
        return issues


class AvoidCultureSpecificRule(ValidationRule):
    """Avoid culture-specific references for global audience."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('avoid-culture-specific', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Avoid culture-specific references for global audience"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        # Examples of culture-specific references
        culture_specific = [
            'thanksgiving', 'christmas', 'fourth of july',
            'football' # Ambiguous - American vs soccer
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            lower_line = line.lower()
            for term in culture_specific:
                if term in lower_line:
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Avoid culture-specific reference "{term}" for global audience',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
        
        return issues


# Rule implementations for Plain Language

class ShortSentencesRule(ValidationRule):
    """Keep sentences short for clarity."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('short-sentences', severity, enabled, config)
        self.max_words = self.config.get('max_words', 25) if config else 25
    
    @property
    def description(self) -> str:
        return f"Keep sentences under {self.max_words} words for clarity"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks and headers
            if line.strip().startswith(('```', '    ', '#', '-', '*')):
                continue
            
            # Split by sentence-ending punctuation
            sentences = re.split(r'[.!?]+\s+', line)
            for sentence in sentences:
                word_count = len(sentence.split())
                if word_count > self.max_words:
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Long sentence ({word_count} words) - consider breaking into shorter sentences',
                        line_number=line_num,
                        context=sentence[:100] + '...' if len(sentence) > 100 else sentence,
                        rule_id=self.rule_id
                    ))
        
        return issues


class AvoidJargonRule(ValidationRule):
    """Avoid technical jargon when possible."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('avoid-jargon', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Avoid unnecessary jargon - use plain language"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        # Common jargon that could be simplified
        jargon_terms = {
            'utilize': 'use',
            'implement': 'add' or 'create',
            'leverage': 'use',
            'facilitate': 'help',
            'utilize': 'use',
        }
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            lower_line = line.lower()
            for jargon, simple in jargon_terms.items():
                if re.search(r'\b' + jargon + r'\b', lower_line):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Consider simpler term: "{simple}" instead of "{jargon}"',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
        
        return issues


class UseCommonWordsRule(ValidationRule):
    """Use common words instead of complex ones."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('use-common-words', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Use common words instead of complex ones"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        # Complex words and simpler alternatives
        complex_words = {
            'commence': 'start',
            'terminate': 'end',
            'endeavor': 'try',
            'ascertain': 'find out',
            'obtain': 'get',
            'purchase': 'buy',
            'sufficient': 'enough',
            'demonstrate': 'show',
        }
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith(('```', '    ')):
                continue
            
            lower_line = line.lower()
            for complex_word, simple in complex_words.items():
                if re.search(r'\b' + complex_word + r'\b', lower_line):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Use simpler word: "{simple}" instead of "{complex_word}"',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
        
        return issues


class AvoidNominalizationRule(ValidationRule):
    """Avoid nominalization - use verbs instead of nouns."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True,
                 config: Optional[Dict] = None):
        super().__init__('avoid-nominalization', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Avoid nominalization - use verbs instead of nouns"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        # Nominalizations and their verb forms
        nominalizations = {
            'implementation': 'implement',
            'utilization': 'use',
            'configuration': 'configure',
            'validation': 'validate',
            'verification': 'verify',
            'determination': 'determine',
        }
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks and headers
            if line.strip().startswith(('```', '    ', '#')):
                continue
            
            lower_line = line.lower()
            for noun, verb in nominalizations.items():
                if re.search(r'\b' + noun + r'\b', lower_line):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Consider using verb "{verb}" instead of noun "{noun}"',
                        line_number=line_num,
                        context=line.strip()[:100],
                        rule_id=self.rule_id
                    ))
        
        return issues


# Style guide registry
STYLE_GUIDES = {
    'google': GoogleStyleGuide,
    'microsoft': MicrosoftStyleGuide,
    'plain-language': PlainLanguageGuide,
}


def get_style_guide(name: str) -> Optional[StyleGuide]:
    """
    Get a style guide by name.
    
    Args:
        name: Style guide name (google, microsoft, plain-language)
        
    Returns:
        StyleGuide instance or None
    """
    guide_class = STYLE_GUIDES.get(name.lower())
    if guide_class:
        return guide_class()
    return None


def list_style_guides() -> List[Dict[str, str]]:
    """
    List available style guides.
    
    Returns:
        List of style guide information
    """
    guides = []
    for name, guide_class in STYLE_GUIDES.items():
        guide = guide_class()
        guides.append({
            'name': name,
            'title': guide.name,
            'description': guide.description,
            'rule_count': len(guide.get_rules())
        })
    return guides
