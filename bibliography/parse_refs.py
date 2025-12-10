#!/usr/bin/env python3
"""
Parse ACL-formatted references and output as HTML.
Format: Author1first Author1last, Author2first Author2last ... and AuthorNfirst, AuthorNlast. YYYY. Title. venue.
"""

import re
from typing import List, Tuple

def parse_reference(ref_text: str) -> Tuple[str, int, str, str, str]:
    """
    Parse a single reference.
    Returns: (first_author_last, year, authors_str, title, venue)
    """
    ref_text = ref_text.strip()
    if not ref_text:
        return None
    
    # Match pattern: Authors. Year. Rest
    # Look for a 4-digit year followed by a period
    year_match = re.search(r'\.\s+(\d{4})\.\s+', ref_text)
    
    if not year_match:
        print(f"Warning: Could not find year in: {ref_text[:100]}...")
        return None
    
    year = int(year_match.group(1))
    year_pos = year_match.start()
    
    # Authors are everything before the year
    authors_str = ref_text[:year_pos].strip()
    
    # Extract first author's last name
    # Handle patterns like: "FirstName LastName", "F. LastName", "FirstName Middle LastName"
    # Split by comma or "and" to get first author
    first_author_parts = re.split(r',|\s+and\s+', authors_str)[0].strip()
    
    # Match last word as last name (handles initials and middle names)
    name_parts = first_author_parts.split()
    if len(name_parts) >= 2:
        first_author_last = name_parts[-1].rstrip('.,')
    elif name_parts:
        first_author_last = name_parts[0].rstrip('.,')
    else:
        first_author_last = "Unknown"
    
    # Everything after the year
    after_year = ref_text[year_match.end():].strip()
    
    # Title is typically the first sentence after year
    # Venue starts with "In" or after the first period, or is a journal name
    
    # Try to find "In " which typically starts venue info
    in_match = re.search(r'\.\s+In\s+', after_year)
    
    if in_match:
        # Title is before "In"
        title = after_year[:in_match.start()].strip()
        venue = after_year[in_match.start()+1:].strip()  # Include the period
    else:
        # Look for the first period that likely ends the title
        # Title typically doesn't have "pages", "volume", journal abbreviations
        sentences = re.split(r'\.\s+', after_year, maxsplit=1)
        if len(sentences) >= 2:
            title = sentences[0].strip()
            venue = sentences[1].strip()
        else:
            title = after_year.strip()
            venue = ""
    
    # Clean up
    if title and not title.endswith('.'):
        title = title.rstrip('.')
    
    return (first_author_last, year, authors_str, title, venue)

def main():
    # Read input file
    with open('refs_2.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines
    raw_refs = content.split('\n\n')
    
    # Parse each reference
    parsed_refs = []
    for raw_ref in raw_refs:
        result = parse_reference(raw_ref)
        if result:
            parsed_refs.append(result)
    
    # Sort by first author last name, then year
    parsed_refs.sort(key=lambda x: (x[0].lower(), x[1]))
    
    # Generate HTML
    html_lines = ['<!DOCTYPE html>']
    html_lines.append('<html>')
    html_lines.append('<head>')
    html_lines.append('  <meta charset="utf-8">')
    html_lines.append('  <title>Bibliography</title>')
    html_lines.append('  <link rel="preconnect" href="https://fonts.googleapis.com">')
    html_lines.append('  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    html_lines.append('  <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">')
    html_lines.append('  <style>')
    html_lines.append('    body { font-family: "Times New Roman", serif; margin: 40px; line-height: 1.6; }')
    html_lines.append('    .reference { font-family: "Roboto", sans-serif; margin-bottom: 1em; text-indent: -2em; padding-left: 2em; }')
    html_lines.append('    .title { font-weight: bold; }')
    html_lines.append('    .venue { font-style: italic; }')
    html_lines.append('  </style>')
    html_lines.append('</head>')
    html_lines.append('<body>')
    html_lines.append('  <h1>Bibliography</h1>')
    
    for last_name, year, authors, title, venue in parsed_refs:
        html_lines.append('  <div class="reference">')
        
        # Authors. Year.
        html_lines.append(f'    {authors}. {year}. ')
        
        # Title (bolded)
        html_lines.append(f'<span class="title">{title}</span>. ')
        
        # Venue (italicized)
        if venue:
            html_lines.append(f'<span class="venue">{venue}</span>')
        
        html_lines.append('  </div>')
    
    html_lines.append('</body>')
    html_lines.append('</html>')
    
    # Write output
    with open('out.html', 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    
    print(f"Successfully parsed {len(parsed_refs)} references.")
    print("Output written to out.html")

if __name__ == '__main__':
    main()

