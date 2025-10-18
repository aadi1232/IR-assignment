import re
from collections import Counter
import pickle
import os

def load_titles(file_path):
    """Load titles from a file, skipping headers if present."""
    titles = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('page_title'):  # Skip header
                # For tab-separated, take the title part
                parts = line.split('\t')
                if len(parts) > 1:
                    title = parts[1]
                else:
                    title = parts[0]
                titles.append(title)
    return titles

def tokenize_titles(titles):
    """Tokenize titles into words, handling Gujarati and English."""
    words = []
    for title in titles:
        # Replace underscores with spaces, remove special chars
        title = title.replace('_', ' ')
        # Better tokenization for Gujarati and English
        # Remove parentheses and their contents
        title = re.sub(r'\([^)]*\)', '', title)
        # Split on spaces and punctuation, keep only word characters
        tokens = re.findall(r'[\w]+', title)
        # Filter out very short tokens and numbers-only
        tokens = [token for token in tokens if len(token) > 1 and not token.isdigit()]
        words.extend(tokens)
    return words

def add_common_words():
    """Add comprehensive Gujarati and English words that might not be in Wikipedia titles."""
    common_gujarati = [
        # Pronouns and basic words
        'હું', 'હુ', 'તું', 'તુ', 'આ', 'એ', 'તે', 'તેઓ', 'આપણે', 'તમે', 'અમે', 'તેમ',
        'મને', 'તમને', 'તેમને', 'મારું', 'મારા', 'મારી', 'તમારું', 'તમારા', 'તમારી',
        
        # Verbs and auxiliaries
        'છે', 'છો', 'છીએ', 'છન', 'હતા', 'હતી', 'હતું', 'હતાં', 'થયું', 'થયા', 'થયી',
        'કરે', 'કરી', 'કર્યું', 'કર્યા', 'કર્યો', 'કરશે', 'કરતા', 'કરતી', 'કરતું',
        'કહે', 'કહેવું', 'કહ્યું', 'કહેશે', 'કહેતા', 'કહેતી',
        'જાય', 'જવું', 'ગયા', 'ગયો', 'ગયી', 'જશે', 'જતા', 'જતી', 'જતું',
        'આવે', 'આવવું', 'આવ્યા', 'આવ્યો', 'આવ્યી', 'આવશે', 'આવતા', 'આવતી',
        'થાય', 'થવું', 'થશે', 'થતું', 'થતા', 'થતી',
        'રહે', 'રહેવું', 'રહ્યા', 'રહ્યો', 'રહ્યી', 'રહેશે', 'રહેતા', 'રહેતી',
        'લે', 'લેવું', 'લીધું', 'લીધા', 'લીધી', 'લેશે', 'લેતા', 'લેતી',
        'દે', 'દેવું', 'દીધું', 'દીધા', 'દીધી', 'દેશે', 'દેતા', 'દેતી',
        'જુએ', 'જોવું', 'જોયું', 'જોયા', 'જોયી', 'જોશે', 'જોતા', 'જોતી',
        'સુને', 'સાંભળવું', 'સાંભળ્યું', 'સાંભળ્યા', 'સાંભળ્યી', 'સાંભળશે',
        'ખાય', 'ખાવું', 'ખાધું', 'ખાધા', 'ખાધી', 'ખાશે', 'ખાતા', 'ખાતી',
        'પીએ', 'પીવું', 'પીધું', 'પીધા', 'પીધી', 'પીશે', 'પીતા', 'પીતી',
        'સૂએ', 'સૂવું', 'સૂતા', 'સૂતી', 'સૂશે',
        'બેસે', 'બેસવું', 'બેઠા', 'બેઠી', 'બેસશે', 'બેસતા', 'બેસતી',
        'ઊભું', 'ઊભા', 'ઊભી', 'ઊભે',
        'ચાલે', 'ચાલવું', 'ચાલ્યા', 'ચાલ્યી', 'ચાલશે', 'ચાલતા', 'ચાલતી',
        'દોડે', 'દોડવું', 'દોડ્યા', 'દોડ્યી', 'દોડશે', 'દોડતા', 'દોડતી',
        'રમે', 'રમવું', 'રમ્યા', 'રમ્યી', 'રમશે', 'રમતા', 'રમતી',
        'ગમે', 'ગમવું', 'ગમ્યું', 'ગમ્યા', 'ગમ્યી', 'ગમશે', 'ગમતું', 'ગમતા', 'ગમતી',
        'મળે', 'મળવું', 'મળ્યા', 'મળ્યી', 'મળશે', 'મળતા', 'મળતી',
        'જઈશ', 'જઇશ', 'આવીશ', 'કરીશ', 'રમીશ', 'રમિશ',
        
        # Connectives and particles
        'ને', 'અને', 'તથા', 'કે', 'જો', 'પણ', 'પરંતુ', 'અથવા', 'કિંવા',
        'માટે', 'થી', 'સુધી', 'વિના', 'સાથે', 'સામે', 'પાસે', 'પર', 'મા', 'માં',
        'ઉપર', 'નીચે', 'અંદર', 'બહાર', 'આગળ', 'પાછળ', 'બાજુ', 'વચ્ચે',
        'પહેલાં', 'પછી', 'દરમિયાન', 'સમયે', 'વખતે',
        
        # Interrogatives
        'શું', 'કોણ', 'શુ', 'કયું', 'કયા', 'કયાં', 'કયારે', 'ક્યાં', 'ક્યારે', 'કેમ', 'કેવું', 'કેવા', 'કેવી',
        'કેટલું', 'કેટલા', 'કેટલી', 'કઈ', 'કોઈ', 'કંઈ', 'કઇ',
        
        # Numbers
        'એક', 'બે', 'ત્રણ', 'ચાર', 'પાંચ', 'છ', 'સાત', 'આઠ', 'નવ', 'દસ',
        'અગિયાર', 'બાર', 'તેર', 'ચૌદ', 'પંદર', 'સોળ', 'સત્તર', 'અઢાર', 'ઓગણીસ', 'વીસ',
        'પચીસ', 'ત્રીસ', 'પેંતાળીસ', 'પચાસ', 'સાઠ', 'સિત્તેર', 'એંસી', 'નેવું', 'સો', 'હજાર',
        
        # Time expressions  
        'આજ', 'આજે', 'કાલે', 'ગઈકાલે', 'પરસાં', 'અવારનવાર', 'હમેશા', 'કદી', 'ક્યારેય',
        'વાર', 'દિવસ', 'રાત', 'સવાર', 'બપોર', 'સાંજ', 'મધ્યરાત્રિ',
        'અઠવાડિયું', 'મહિનો', 'વર્ષ', 'વખત', 'સમય', 'ક્ષણ',
        
        # Common adjectives
        'સારું', 'સારા', 'સારી', 'સરસ', 'ખરાબ', 'નરસ', 'સુંદર', 'ભયાનક',
        'મોટું', 'મોટા', 'મોટી', 'નાનું', 'નાના', 'નાની', 'મધ્યમ',
        'લાંબું', 'લાંબા', 'લાંબી', 'ટૂંકું', 'ટૂંકા', 'ટૂંકી',
        'જાડું', 'જાડા', 'જાડી', 'પાતળું', 'પાતળા', 'પાતળી',
        'ઊંચું', 'ઊંચા', 'ઊંચી', 'નીચું', 'નીચા', 'નીચી',
        'જૂનું', 'જૂના', 'જૂની', 'નવું', 'નવા', 'નવી',
        'ગરમ', 'ઠંડું', 'ઠંડા', 'ઠંડી', 'ગરમા', 'ગરમી',
        'મીઠું', 'મીઠા', 'મીઠી', 'ખારું', 'ખારા', 'ખારી', 'કડવું', 'ખાટું',
        
        # Colors
        'લાલ', 'લાલું', 'લાલા', 'લાલી', 'વાદળી', 'નીલું', 'પીળું', 'પીળા', 'પીળી',
        'લીલું', 'લીલા', 'લીલી', 'સફેદ', 'કાળું', 'કાળા', 'કાળી', 'ભૂરું', 'ભૂરા', 'ભૂરી',
        'ગુલાબી', 'જાંબુડી', 'નારંગી', 'ધૂસર',
        
        # Family and people
        'માણસ', 'સ્ત્રી', 'પુરુષ', 'છોકરો', 'છોકરી', 'બાળક', 'વૃદ્ધ', 'યુવાન',
        'મા', 'મમ્મી', 'માતા', 'બાપ', 'પપ્પા', 'પિતા', 'દીકરો', 'દીકરી', 'ભાઈ', 'બહેન',
        'દાદા', 'દાદી', 'નાના', 'નાની', 'કાકા', 'કાકી', 'મામા', 'મામી', 'ફૂઆ', 'મોસી',
        'પત્ની', 'પતિ', 'સાસુ', 'સાસરા', 'સસરા', 'સસરી',
        'મિત્ર', 'મિત્રો', 'મીત્ર', 'સાથી', 'દોસ્ત', 'સખી',
        
        # Body parts
        'માથું', 'વાળ', 'આંખ', 'આંખો', 'કાન', 'નાક', 'મોં', 'દાંત', 'જીભ',
        'ગળું', 'હાથ', 'પગ', 'પેટ', 'પીઠ', 'છાતી', 'ખભા', 'ઘૂંટણ', 'આંગળી',
        
        # Common objects
        'કામ', 'કાર્ય', 'વસ્તુ', 'ચીજ', 'ખુરશી', 'ટેબલ', 'પલંગ', 'દરવાજો', 'બારી',
        'કાગળ', 'કિતાબ', 'પુસ્તક', 'પેન', 'પેન્સિલ', 'બેગ', 'કપડાં', 'જૂતા',
        'પાણી', 'દૂધ', 'ચા', 'કોફી', 'ભાત', 'રોટલી', 'શાક', 'દાળ', 'મીઠું',
        
        # Places
        'ઘર', 'મકાન', 'બિલ્ડિંગ', 'ફ્લેટ', 'શાળા', 'કોલેજ', 'યુનિવર્સિટી', 'ઑફિસ',
        'હોસ્પિટલ', 'દવાખાનું', 'દુકાન', 'બજાર', 'મંદિર', 'મસ્જિદ', 'ચર્ચ',
        'બગીચો', 'પાર્ક', 'રસ્તો', 'ગલી', 'શેરી', 'ગામ', 'શહેર', 'દેશ',
        
        # Abstract concepts
        'પ્રેમ', 'મમતા', 'ક્રોધ', 'ગુસ્સો', 'સુખ', 'દુઃખ', 'આનંદ', 'ઉદાસી',
        'ભય', 'ડર', 'શાંતિ', 'તકલીફ', 'સમસ્યા', 'મુશ્કેલી', 'સહાય', 'મદદ',
        'માહિતી', 'સમાચાર', 'વાત', 'વાર્તા', 'કથા', 'ગીત', 'સંગીત',
        'ભાષા', 'ગુજરાતી', 'અંગ્રેજી', 'હિન્દી', 'ઉર્દૂ', 'બંગાળી', 'મરાઠી',
        
        # Professions
        'શિક્ષક', 'ઉપાધ્યાય', 'વિદ્યાર્થી', 'ડૉક્ટર', 'નર્સ', 'એન્જિનિયર', 'વકીલ',
        'પોલીસ', 'સૈનિક', 'ખેડૂત', 'બિઝનેસમેન', 'કારીગર', 'મજૂર', 'અધ્યાપક',
        
        # Weather and nature
        'હવા', 'પવન', 'વરસાદ', 'વરખા', 'વીજળી', 'વાદળ', 'સૂર્ય', 'સૂરજ', 'ચંદ્ર', 'ચાંદ',
        'તારા', 'આકાશ', 'પૃથ્વી', 'જમીન', 'માટી', 'ધૂળ', 'પથ્થર', 'પર્વત', 'પહાડ',
        'સમુદ્ર', 'દરિયો', 'નદી', 'તળાવ', 'કૂવો', 'વૃક્ષ', 'ઝાડ', 'ફૂલ', 'ફળ',
        
        # Common expressions
        'જરૂર', 'જરૂરી', 'અવશ્ય', 'જરૂરીયાત', 'જોઈએ', 'લાગે', 'લાગતું', 'લાગશે',
        'હા', 'ના', 'હોય', 'નહીં', 'જ', 'તો', 'ખરું', 'ખોટું', 'સાચું', 'ખરેખર',
        'કદાચ', 'શક્ય', 'અશક્ય', 'મુશ્કિલ', 'સરળ', 'સહેલું',
        'ખૂબ', 'બહુ', 'થોડું', 'ઓછું', 'વધુ', 'બધું', 'બધા', 'બધી', 'બધાં',
        'કોઈ', 'કંઈ', 'કોઈપણ', 'કંઈપણ', 'બીજું', 'બીજા', 'બીજી', 'બીજાં',
        'આવા', 'આવી', 'આવું', 'તેવા', 'તેવી', 'તેવું', 'જેવા', 'જેવી', 'જેવું',
        
        # Miscellaneous essential words
        'શાળાએ', 'શાળામાં', 'ઘરે', 'ઘરમાં', 'કામે', 'કામમાં', 'વિશે', 'બાબતે',
        'પ્રમાણે', 'અનુસાર', 'મુજબ', 'સિવાય', 'ઉપરાંત', 'વધારે', 'ઓછા',
        'દરેક', 'દરેકે', 'દરેકને', 'બધાને', 'બધાએ', 'બધામાં',
        'કેટલાક', 'અમુક', 'કેટલીક', 'ઘણા', 'ઘણી', 'ઘણું', 'ઘણાં',
        'આખું', 'આખા', 'આખી', 'આખાં', 'આખો', 'સમગ્ર', 'આખા',
        'મુખ્ય', 'ખાસ', 'અહેવાલ', 'રિપોર્ટ', 'પત્ર', 'પત્રિકા', 'અખબાર'
    ]
    
    common_english = [
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'can', 'this', 'that', 'these', 'those', 'he', 'she',
        'it', 'they', 'we', 'you', 'I', 'me', 'him', 'her', 'them', 'us',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'here', 'there',
        'where', 'when', 'why', 'how', 'what', 'who', 'which', 'all', 'any',
        'some', 'many', 'much', 'few', 'little', 'more', 'most', 'good', 'bad',
        'big', 'small', 'new', 'old', 'first', 'last', 'next', 'other', 'same'
    ]
    
    return common_gujarati + common_english

def build_frequency_dict(words):
    """Build a frequency dictionary from words with enhanced common words."""
    # Count words from titles
    freq_dict = Counter(words)
    
    # Add common words with very high frequency if not present
    common_words = add_common_words()
    for word in common_words:
        if word not in freq_dict:
            # Give very high frequency to common words not in titles
            freq_dict[word] = 1000
        else:
            # Boost frequency of common words that appear in titles
            freq_dict[word] += 500
    
    return freq_dict

def save_index(freq_dict, file_path='index.pkl'):
    """Save the frequency dictionary to disk."""
    with open(file_path, 'wb') as f:
        pickle.dump(freq_dict, f)

def load_index(file_path='index.pkl'):
    """Load the frequency dictionary from disk."""
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return {}

if __name__ == '__main__':
    # Load from both files
    titles1 = load_titles('guwiki-latest-all-titles')
    titles2 = load_titles('guwiki-latest-all-titles-in-ns0')
    all_titles = titles1 + titles2

    words = tokenize_titles(all_titles)
    freq_dict = build_frequency_dict(words)
    save_index(freq_dict)
    print(f"Index built with {len(freq_dict)} unique words.")