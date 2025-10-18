#!/usr/bin/env python3
"""
File-based Spell Checker
Processes input.txt and generates output.txt with spell check results
"""

from data_loader import load_index
from spell_checker import suggest_corrections, auto_correct_text, check_text
import time

def process_input_file(input_file='input.txt', output_file='output.txt'):
    """Process input file and generate output file with spell check results."""
    
    print("Loading spell checker dictionary...")
    freq_dict = load_index()
    if not freq_dict:
        print("Error: Dictionary not found. Run data_loader.py first.")
        return
    
    print(f"Dictionary loaded with {len(freq_dict)} words")
    
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print(f"Error: {input_file} is empty")
            return
            
        print(f"Processing {len(lines)} lines from {input_file}...")
        
        # Process each line and collect results
        results = []
        total_misspelled = 0
        total_corrections = 0
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            print(f"Processing line {i}: {line[:50]}...")
            
            # Check for misspellings
            start_time = time.time()
            misspelled_results = check_text(line, freq_dict)
            check_time = time.time() - start_time
            
            # Auto-correct
            start_time = time.time()
            corrected_text, correction_summary = auto_correct_text(line, freq_dict)
            correct_time = time.time() - start_time
            
            # Collect statistics
            misspelled_count = len(misspelled_results)
            total_misspelled += misspelled_count
            
            if "Auto-corrections made:" in correction_summary:
                corrections_made = len(correction_summary.split('\n')) - 1
                total_corrections += corrections_made
            
            # Store results
            result = {
                'line_number': i,
                'original': line,
                'corrected': corrected_text,
                'misspelled_words': list(misspelled_results.keys()),
                'suggestions': misspelled_results,
                'correction_summary': correction_summary,
                'processing_time': check_time + correct_time
            }
            results.append(result)
        
        # Write output file
        write_output_file(results, output_file, total_misspelled, total_corrections)
        
        print(f"\nProcessing completed!")
        print(f"Results written to: {output_file}")
        print(f"Total lines processed: {len(results)}")
        print(f"Total misspelled words found: {total_misspelled}")
        print(f"Total auto-corrections made: {total_corrections}")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
    except Exception as e:
        print(f"Error processing file: {e}")

def write_output_file(results, output_file, total_misspelled, total_corrections):
    """Write spell check results to output file."""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("GUJARATI SPELL CHECKER - OUTPUT RESULTS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Processing Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Lines Processed: {len(results)}\n")
        f.write(f"Total Misspelled Words: {total_misspelled}\n")
        f.write(f"Total Auto-corrections: {total_corrections}\n")
        f.write("=" * 60 + "\n\n")
        
        # Process each result
        for result in results:
            f.write(f"Line {result['line_number']}:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Original:  {result['original']}\n")
            f.write(f"Corrected: {result['corrected']}\n")
            
            if result['misspelled_words']:
                f.write(f"\nMisspelled Words ({len(result['misspelled_words'])}):\n")
                for word in result['misspelled_words']:
                    suggestions = result['suggestions'][word][:5]  # Top 5 suggestions
                    f.write(f"  '{word}' -> {', '.join(suggestions)}\n")
                
                f.write(f"\nCorrection Status:\n{result['correction_summary']}\n")
            else:
                f.write("\nNo misspelled words found.\n")
            
            f.write(f"Processing Time: {result['processing_time']:.3f} seconds\n")
            f.write("\n" + "=" * 60 + "\n\n")

def quick_spell_check(text, freq_dict, max_suggestions=3):
    """Optimized spell check for faster processing."""
    from spell_checker import tokenize_text, is_misspelled
    
    words = tokenize_text(text)
    results = {}
    
    for word in words:
        if is_misspelled(word, freq_dict):
            # Quick candidate search - limit to common patterns
            candidates = []
            word_lower = word.lower()
            
            # Check for exact case variations first
            for dict_word in freq_dict:
                if word_lower == dict_word.lower():
                    candidates.append(dict_word)
                    break
            
            # If no exact match, look for close matches (edit distance 1-2)
            if not candidates:
                for dict_word in freq_dict:
                    if abs(len(word) - len(dict_word)) <= 2:  # Length filter
                        # Simple similarity check
                        if len(set(word_lower) & set(dict_word.lower())) >= len(word_lower) - 2:
                            candidates.append(dict_word)
                            if len(candidates) >= max_suggestions:
                                break
            
            if candidates:
                # Sort by frequency
                candidates.sort(key=lambda x: freq_dict[x], reverse=True)
                results[word] = candidates[:max_suggestions]
    
    return results

if __name__ == '__main__':
    import sys
    
    input_file = 'input.txt'
    output_file = 'output.txt'
    
    # Check command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    process_input_file(input_file, output_file)