import glob
import re
from bs4 import BeautifulSoup

def main():
    print("Parsing HTML calendar...")
    html_path = 'CanSkate202627Calendar.html'
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"Error reading {html_path}: {e}")
        return

    # Map HTML badge text to ICS SUMMARY text
    program_map = {
        'Adult CanSkate': 'Adult CanSkate',
        'Adv Edges & Skills': 'Advanced Edges and Skating Skills',
        'CanSkate': 'CanSkate',
        'PreCan': 'PreCan',
        'PreJunior': 'PreJunior',
        'Teen / Tween': 'Teen/Tween'
    }

    html_events = []
    months = soup.find_all('div', class_='month-card')
    for month_div in months:
        month_id = month_div.get('id', '')
        if not month_id: continue
        
        parts = month_id.split('-')
        m = int(parts[1])
        y = int(parts[2])
        
        cells = month_div.find_all('td', class_='session-active-cell')
        for cell in cells:
            date_div = cell.find(class_='day-number')
            if not date_div: continue
            
            # The date text might have a badge or extra spacing
            d_text = date_div.get_text(strip=True)
            # Find the first number in the text
            m_num = re.search(r'\d+', d_text)
            if not m_num: continue
            d = int(m_num.group(0))
            
            # Skip padding cells just in case
            if 'padding-cell' in cell.get('class', []): continue
            
            event_date = f"{y:04d}{m:02d}{d:02d}"
            
            slots = cell.find_all('div', class_='slot-item')
            for slot in slots:
                badge_span = slot.find('span', class_='slot-badge')
                if not badge_span: continue
                badge = badge_span.get_text(strip=True)
                ics_name = program_map.get(badge, badge)
                html_events.append((event_date, ics_name))

    print(f"Found {len(html_events)} session slots in HTML.")

    print("Parsing ICS files...")
    ics_events = []
    ics_files = glob.glob('*.ics')
    for fpath in ics_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            current_date = None
            current_summary = None
            for line in lines:
                line = line.strip()
                if line.startswith('DTSTART'):
                    match = re.search(r':(\d{8})T', line)
                    if match:
                        current_date = match.group(1)
                elif line.startswith('SUMMARY:'):
                    current_summary = line.split(':', 1)[1]
                elif line == 'END:VEVENT':
                    if current_date and current_summary:
                        ics_events.append((current_date, current_summary))
                    current_date = None
                    current_summary = None

    print(f"Found {len(ics_events)} events across {len(ics_files)} ICS files.")

    html_counts = {}
    for e in html_events:
        html_counts[e] = html_counts.get(e, 0) + 1

    ics_counts = {}
    for e in ics_events:
        ics_counts[e] = ics_counts.get(e, 0) + 1

    discrepancies = 0
    all_keys = set(html_counts.keys()).union(set(ics_counts.keys()))
    
    print("\n--- Comparison Results ---")
    for key in sorted(all_keys):
        h_count = html_counts.get(key, 0)
        i_count = ics_counts.get(key, 0)
        if h_count != i_count:
            print(f"DISCREPANCY -> Date: {key[0]} | Program: {key[1]} | HTML Count: {h_count} | ICS Count: {i_count}")
            discrepancies += 1

    if discrepancies == 0:
        print(f"\nSUCCESS: All {len(ics_events)} ICS events perfectly match the HTML calendar slots!")
    else:
        print(f"\nFailed: Found {discrepancies} discrepancies between HTML and ICS files.")

if __name__ == '__main__':
    main()
