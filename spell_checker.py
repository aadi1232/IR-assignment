import re
import string

def damerau_levenshtein_distance(s1, s2):
    """Calculate Damerau-Levenshtein distance with insertion, deletion, substitution, transposition."""
    len1, len2 = len(s1), len(s2)
    
    # Create a dictionary for character mapping
    da = {}
    for char in s1 + s2:
        da[char] = 0
    
    # Create the distance matrix
    max_dist = len1 + len2
    H = [[max_dist for _ in range(len2 + 2)] for _ in range(len1 + 2)]
    
    H[0][0] = max_dist
    for i in range(0, len1 + 1):
        H[i + 1][0] = max_dist
        H[i + 1][1] = i
    for j in range(0, len2 + 1):
        H[0][j + 1] = max_dist
        H[1][j + 1] = j
    
    for i in range(1, len1 + 1):
        db = 0
        for j in range(1, len2 + 1):
            k = da[s2[j - 1]]
            l = db
            cost = 1
            if s1[i - 1] == s2[j - 1]:
                cost = 0
                db = j
            
            H[i + 1][j + 1] = min(
                H[i][j] + cost,  # substitution
                H[i + 1][j] + 1,  # insertion
                H[i][j + 1] + 1,  # deletion
                H[k][l] + (i - k - 1) + 1 + (j - l - 1)  # transposition
            )
        
        da[s1[i - 1]] = i
    
    return H[len1 + 1][len2 + 1]

def tokenize_text(text):
    """Tokenize text properly, removing punctuation and preserving Gujarati words."""
    # Remove punctuation but preserve word boundaries
    # Use Unicode word boundaries to handle Gujarati properly
    import unicodedata
    
    # Remove common punctuation marks
    punctuation = '।,.!?;:"()[]{}॥'
    for p in punctuation:
        text = text.replace(p, ' ')
    
    # Split on whitespace and filter empty strings
    words = [word.strip() for word in text.split() if word.strip()]
    
    # Additional filtering for meaningful words (length > 1 for Gujarati)
    meaningful_words = []
    for word in words:
        # Keep words that are longer than 1 character OR are common single characters
        if len(word) > 1 or word in ['આ', 'એ', 'ઓ', 'અ', 'ઇ', 'ઈ', 'ઉ', 'ઊ', 'ઋ', 'એ', 'ઐ', 'ઓ', 'ઔ']:
            meaningful_words.append(word)
    
    return meaningful_words

def get_candidates(word, freq_dict, max_dist=2):
    """Get candidate corrections within max_dist, ranked by smart scoring."""
    candidates = []
    word_lower = word.lower()
    
    for correct_word in freq_dict:
        correct_lower = correct_word.lower()
        
        # Skip exact matches (case insensitive)
        if word_lower == correct_lower:
            continue
            
        dist = damerau_levenshtein_distance(word_lower, correct_lower)
        if dist <= max_dist and dist > 0:
            frequency = freq_dict[correct_word]
            
            # Smart scoring: prioritize high-frequency words for same distance
            # Score = distance penalty - frequency bonus
            # Lower score = better candidate
            score = dist * 100 - min(frequency, 3000) / 10
            
            candidates.append((correct_word, dist, frequency, score))
    
    # Sort by score (ascending) - lower score is better
    candidates.sort(key=lambda x: x[3])
    return [cand[0] for cand in candidates[:10]]  # Top 10

def is_misspelled(word, freq_dict):
    """Check if a word is misspelled (not in dictionary)."""
    word_lower = word.lower()
    return not any(word_lower == w.lower() for w in freq_dict)

def check_text(text, freq_dict):
    """Check text for misspelled words and suggest corrections."""
    words = tokenize_text(text)
    results = {}
    
    for word in words:
        if is_misspelled(word, freq_dict):
            candidates = get_candidates(word, freq_dict)
            if candidates:
                results[word] = candidates
    
    return results

def suggest_corrections(text, freq_dict):
    """Return text with suggestions."""
    results = check_text(text, freq_dict)
    if not results:
        return "No misspellings found."
    
    output = "Misspelled words and suggestions:\n"
    for word, sugg in results.items():
        output += f"'{word}' -> {', '.join(sugg[:5])}\n"  # Show top 5
    return output

def correct_text_interactive(text, freq_dict):
    """Interactively correct text with user choices."""
    results = check_text(text, freq_dict)
    if not results:
        return text, "No misspellings found."
    
    corrected_text = text
    corrections_made = []
    
    for misspelled_word, candidates in results.items():
        print(f"\nMisspelled word: '{misspelled_word}'")
        print("Suggestions:")
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"{i}. {candidate}")
        print("0. Keep original")
        
        while True:
            try:
                choice = input(f"Choose correction for '{misspelled_word}' (0-{min(5, len(candidates))}): ")
                choice_num = int(choice)
                if choice_num == 0:
                    break
                elif 1 <= choice_num <= min(5, len(candidates)):
                    replacement = candidates[choice_num - 1]
                    corrected_text = corrected_text.replace(misspelled_word, replacement, 1)
                    corrections_made.append(f"'{misspelled_word}' -> '{replacement}'")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
    
    correction_summary = "Corrections made:\n" + "\n".join(corrections_made) if corrections_made else "No corrections made."
    return corrected_text, correction_summary

def auto_correct_text(text, freq_dict, confidence_threshold=2):
    """Automatically correct text using smart confidence scoring."""
    results = check_text(text, freq_dict)
    if not results:
        return text, "No misspellings found."
    
    corrected_text = text
    corrections_made = []
    
    for misspelled_word, candidates in results.items():
        if candidates:
            top_candidate = candidates[0]
            edit_dist = damerau_levenshtein_distance(misspelled_word.lower(), top_candidate.lower())
            
            # Get candidate frequency
            candidate_freq = freq_dict.get(top_candidate, 0)
            
            # Auto-correct if:
            # 1. Edit distance is 1 (very likely correction)
            # 2. Edit distance is 2 AND candidate has high frequency (>= 2000)
            should_correct = (
                edit_dist == 1 or 
                (edit_dist == 2 and candidate_freq >= 2000) or
                (edit_dist <= confidence_threshold and candidate_freq >= 3000)
            )
            
            if should_correct:
                corrected_text = corrected_text.replace(misspelled_word, top_candidate, 1)
                corrections_made.append(f"'{misspelled_word}' -> '{top_candidate}'")
    
    correction_summary = "Auto-corrections made:\n" + "\n".join(corrections_made) if corrections_made else "No auto-corrections made."
    return corrected_text, correction_summary