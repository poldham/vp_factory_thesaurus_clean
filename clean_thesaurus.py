import sys
import os
import json
import ollama
from tqdm import tqdm
from difflib import SequenceMatcher

def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def parse_the_file(file_path):
    """Parses .the file (UTF-16) into a dict of headers and their aliases."""
    groups = []
    current_group = None
    
    with open(file_path, 'r', encoding='utf-16') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('**'):
                if current_group:
                    groups.append(current_group)
                current_group = {'header': line[2:].strip(), 'aliases': []}
            elif line.startswith('0 1 ^') and current_group:
                # Extract content between ^ and $
                alias = line[5:].split('$')[0]
                current_group['aliases'].append(alias)
        
        if current_group:
            groups.append(current_group)
            
    return groups

import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleaning_progress.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

GENERIC_WORDS = {'pharma', 'biotechnology', 'corporation', 'limited', 'ltd', 'inc', 'corp', 'institute', 'university', 'univ', 'center', 'centre', 'development', 'research', 'technologies', 'technology', 'group', 'holdings', 'solutions'}

def is_generic_only(header, alias):
    """Checks if the only commonality is a single generic word."""
    h_words = set(header.lower().split())
    a_words = set(alias.lower().split())
    common = h_words.intersection(a_words)
    if len(common) == 1 and list(common)[0] in GENERIC_WORDS:
        # If the overlap is just one generic word, it's highly suspicious
        return True
    return False

def audit_group(agent_prompt, header, aliases, model_name='llama3.1'):
    """Sends a group to Ollama for review with enhanced logic."""
    if len(aliases) <= 1:
        return []

    # Pre-filtering suspicious entries to flag them for the LLM
    flagged = []
    for a in aliases:
        if is_generic_only(header, a):
            flagged.append(a)
        elif string_similarity(header, a) < 0.3:
            flagged.append(a)

    # Escape double quotes in aliases for the prompt to avoid JSON corruption
    safe_aliases = [a.replace('"', '\\"') for a in aliases]
    
    # Enhanced prompt with reasoning instruction
    prompt = (
        f"Header: {header}\n"
        f"Aliases: {json.dumps(safe_aliases)}\n\n"
        "Instructions:\n"
        "1. Analyze each alias for organizational and semantic alignment with the header.\n"
        "2. Pay special attention to 'one-word variance' where the only shared word is generic.\n"
        f"3. Suspicious entries detected by algorithm: {json.dumps(flagged)}\n\n"
        "Process each alias step-by-step mentally, then return the final list of false positives to remove in the required JSON format."
    )
    
    try:
        response = ollama.chat(
            model=model_name, 
            format='json', 
            messages=[
                {'role': 'system', 'content': agent_prompt},
                {'role': 'user', 'content': prompt},
            ],
            options={'num_predict': 1024, 'temperature': 0}
        )
        content = response['message']['content'].strip()
        data = json.loads(content)
        
        if isinstance(data, dict) and 'remove' in data:
            return data['remove']
        elif isinstance(data, list):
            return data
            
    except Exception as e:
        logging.error(f"Error auditing group {header}: {e}")
    return []

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--model', default='llama3.1', help='Ollama model to use (e.g. llama3.1, llama3.3, mistral-small)')
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = input_file.replace('.the', '_cleaned.the')
    
    with open('agents.md', 'r') as f:
        agent_prompt = f.read()
        
    print(f"Parsing {input_file}...")
    groups = parse_the_file(input_file)
    
    if args.limit:
        groups = groups[:args.limit]
        print(f"Limited to first {args.limit} groups.")
    
    print(f"Auditing {len(groups)} groups using model: {args.model}...")
    cleaned_groups = []
    
    for group in tqdm(groups):
        logging.info(f"Auditing group: {group['header']}")
        to_remove = audit_group(agent_prompt, group['header'], group['aliases'], args.model)
        cleaned_aliases = [a for a in group['aliases'] if a not in to_remove]
        
        if cleaned_aliases:
            cleaned_groups.append({
                'header': group['header'],
                'aliases': cleaned_aliases
            })

    print(f"Writing cleaned file to {output_file}...")
    with open(output_file, 'w', encoding='utf-16') as f:
        # Write headers found in original if needed (omitted for brevity)
        f.write("# Cleaned Thesaurus\n")
        for group in cleaned_groups:
            f.write(f"**{group['header']}\n")
            for alias in group['aliases']:
                f.write(f"0 1 ^{alias}$\n")

if __name__ == "__main__":
    main()
