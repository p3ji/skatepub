import calendar
import datetime
import os
import copy
import shutil
from bs4 import BeautifulSoup

def generate_calendar():
    # Ensure images directory exists in both docs/calendar/images and docs/calendar/unzipped_docx/images
    src_images_dir = os.path.join('docs', 'calendar', 'unzipped_docx', 'images')
    dst_images_dir = os.path.join('docs', 'calendar', 'images')
    
    if os.path.exists(src_images_dir):
        os.makedirs(dst_images_dir, exist_ok=True)
        for img_file in os.listdir(src_images_dir):
            shutil.copy2(os.path.join(src_images_dir, img_file), os.path.join(dst_images_dir, img_file))

    # Define exact schedules based on docs/calendar/reference file for calendar.eml
    schedules = {
        0: { # Monday
            'start': datetime.date(2026, 9, 14),
            'end': datetime.date(2027, 3, 29),
            'no_skate': [datetime.date(2026, 12, 21), datetime.date(2026, 12, 28)],
            'label': 'Adult CanSkate 8:00-8:50 pm',
            'expected_count': 27
        },
        2: { # Wednesday
            'start': datetime.date(2026, 9, 16),
            'end': datetime.date(2027, 3, 10),
            'no_skate': [datetime.date(2026, 12, 23), datetime.date(2026, 12, 30)],
            'label': 'CanSkate 4:00-7:00 pm',
            'expected_count': 24
        },
        4: { # Friday
            'start': datetime.date(2026, 9, 18),
            'end': datetime.date(2027, 3, 12),
            'no_skate': [datetime.date(2026, 12, 25), datetime.date(2027, 1, 1)],
            'label': 'CanSkate 4:00-8:00 pm',
            'expected_count': 24
        },
        5: { # Saturday
            'start': datetime.date(2026, 9, 19),
            'end': datetime.date(2027, 3, 13),
            'no_skate': [datetime.date(2026, 12, 26), datetime.date(2027, 1, 2)],
            'label': 'CanSkate 12:00-2:00 pm',
            'expected_count': 24
        },
        6: { # Sunday
            'start': datetime.date(2026, 9, 13),
            'end': datetime.date(2027, 3, 7),
            'no_skate': [datetime.date(2026, 12, 20), datetime.date(2026, 12, 27)],
            'label': 'CanSkate / Adv Edges 2:00-3:50 pm',
            'expected_count': 24
        }
    }

    # Pre-calculate active session dates and numbers per day of week
    session_map = {} # date -> (session_number, is_last, label)
    for dow, sched in schedules.items():
        curr = sched['start']
        count = 0
        active_dates = []
        while curr <= sched['end']:
            if curr not in sched['no_skate']:
                count += 1
                active_dates.append((curr, count))
            curr += datetime.timedelta(days=7)
        
        last_date = active_dates[-1][0]
        for dt, s_num in active_dates:
            is_last = (dt == last_date)
            session_map[dt] = (s_num, is_last, sched['label'])

    # Special events, holidays, and associated image assets
    special_events = {
        datetime.date(2026, 9, 5): ('PA CLINIC', None),
        datetime.date(2026, 9, 7): ('LABOR DAY NO SKATING', None),
        datetime.date(2026, 10, 12): ('Thanksgiving', 'images/image4.gif'),
        datetime.date(2026, 10, 31): ('Halloween', 'images/image5.jpg'),
        datetime.date(2026, 11, 11): ('Remembrance Day', 'images/image2.jpg'),
        datetime.date(2026, 12, 20): ('NO SKATING', None),
        datetime.date(2026, 12, 21): ('NO SKATING', None),
        datetime.date(2026, 12, 23): ('NO SKATING', None),
        datetime.date(2026, 12, 24): ('Christmas Eve NO SKATING', 'images/image3.png'),
        datetime.date(2026, 12, 25): ('Christmas Day NO SKATING', 'images/image3.png'),
        datetime.date(2026, 12, 26): ('NO SKATING', None),
        datetime.date(2026, 12, 27): ('NO SKATING', None),
        datetime.date(2026, 12, 28): ('NO SKATING', None),
        datetime.date(2026, 12, 30): ('NO SKATING', None),
        datetime.date(2026, 12, 31): ('New Year\'s Eve NO SKATING', None),
        datetime.date(2027, 1, 1): ('New Year\'s Day NO SKATING', None),
        datetime.date(2027, 1, 2): ('NO SKATING', None),
        datetime.date(2027, 2, 15): ('Family Day', None),
    }

    # Load base HTML template
    template_path = os.path.join('docs', 'calendar', 'unzipped_docx', 'CanSkate202627Calendar.docx.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    months = [
        (2026, 9, "September 2026"),
        (2026, 10, "October 2026"),
        (2026, 11, "November 2026"),
        (2026, 12, "December 2026"),
        (2027, 1, "January 2027"),
        (2027, 2, "February 2027"),
        (2027, 3, "March 2027")
    ]

    tables = soup.find_all('table')
    
    for idx, (year, month, month_title) in enumerate(months):
        tbl = tables[idx]
        
        # 1. Update Title Header with Logo (images/image1.jpg)
        header_tr = tbl.find_all('tr')[0]
        header_td = header_tr.find('td')
        if header_td:
            header_td.clear()
            header_td['style'] = 'background-color:#7030a0; padding:12px; color:#ffffff;'
            logo_img = soup.new_tag('img', src='images/image1.jpg', style='height:48px; vertical-align:middle; margin-right:15px; border-radius:4px;')
            header_td.append(logo_img)
            title_span = soup.new_tag('span', style='font-weight:bold; font-size:15pt; color:#ffffff; vertical-align:middle;')
            title_span.string = f"MKSC CanSkate / Pre-Junior / Pre-CanSkate / Adult & Teens Calendar – 2026/2027 Season  |  {month_title}"
            header_td.append(title_span)

        # 2. Update Day-of-Week Headers Row (Sun, Mon, Tue...)
        dow_tr = tbl.find_all('tr')[1]
        for dow_td in dow_tr.find_all(['td', 'th']):
            dow_td['style'] = 'background-color:#7030a0; color:#ffffff; font-weight:bold; text-align:center; padding:6px; font-size:11pt;'

        # 3. Build month calendar grid weeks
        cal = calendar.Calendar(firstweekday=6) # 6 = Sunday start
        month_days = list(cal.itermonthdays2(year, month)) # list of (day_num, dow_idx)
        
        # Group into 7-day rows (Sun -> Sat)
        weeks = [month_days[i:i+7] for i in range(0, len(month_days), 7)]
        
        table_rows = tbl.find_all('tr')
        grid_tr_list = list(table_rows[2:])
        
        # Adjust table row count to match len(weeks) exactly
        while len(grid_tr_list) > len(weeks):
            extra_tr = grid_tr_list.pop()
            extra_tr.decompose()
            
        while len(grid_tr_list) < len(weeks):
            new_tr = copy.copy(grid_tr_list[-1])
            tbl.append(new_tr)
            grid_tr_list.append(new_tr)
        
        for w_idx, week in enumerate(weeks):
            tr = grid_tr_list[w_idx]
            tds = tr.find_all(['td', 'th'])
            
            for d_idx, (day_num, dow_idx) in enumerate(week):
                if d_idx >= len(tds):
                    break
                td = tds[d_idx]
                td.clear()
                
                # Set clean white background for all day cells
                td['style'] = 'background-color:#ffffff; vertical-align:top; padding:4px 6px; border:1px solid #cccccc; height:85px;'
                
                # Check if cell is outside current month
                if day_num == 0:
                    td['style'] = 'background-color:#f9f9f9; border:1px solid #e0e0e0;'
                    continue
                
                dt = datetime.date(year, month, day_num)
                
                # Day Number Header (Top Left)
                day_b = soup.new_tag('b', style='font-size:11pt; color:#333333;')
                day_b.string = str(day_num)
                td.append(day_b)
                
                # Check for Special Event / Holiday & Image Asset
                asset_img = None
                event_name = None
                if dt in special_events:
                    event_name, asset_src = special_events[dt]
                    if asset_src:
                        asset_img = soup.new_tag('img', src=asset_src, style='max-height:36px; float:right; margin:2px;')
                
                if asset_img:
                    td.append(asset_img)
                
                td.append(soup.new_tag('br'))
                
                # Build Cell Content Lines
                lines = []
                if event_name:
                    lines.append(event_name)
                
                if dt in session_map:
                    s_num, is_last, label = session_map[dt]
                    last_str = " Last Session" if is_last else ""
                    lines.append(f"Session #{s_num} {label}{last_str}")
                
                for line_idx, line in enumerate(lines):
                    if line_idx > 0:
                        td.append(soup.new_tag('br'))
                    span = soup.new_tag('span', style='font-size:8.5pt;')
                    if 'NO SKATING' in line:
                        span['style'] += ' color:#c00000; font-weight:bold;'
                    elif 'Last Session' in line:
                        span['style'] += ' font-weight:bold; color:#0070c0;'
                    elif 'Session #' in line:
                        span['style'] += ' color:#1f497d;'
                    elif 'PA CLINIC' in line or 'Halloween' in line or 'Remembrance Day' in line or 'Family Day' in line:
                        span['style'] += ' font-weight:bold; color:#595959;'
                    span.string = line
                    td.append(span)

    html_out = str(soup)
    
    out_path_unzipped = os.path.join('docs', 'calendar', 'unzipped_docx', 'CanSkate202627Calendar.docx.html')
    with open(out_path_unzipped, 'w', encoding='utf-8') as f:
        f.write(html_out)
        
    out_path_standalone = os.path.join('docs', 'calendar', 'CanSkate202627Calendar.html')
    with open(out_path_standalone, 'w', encoding='utf-8') as f:
        f.write(html_out)
    
    print(f"Successfully generated HTML calendar referencing docs/calendar/images at:\n  - {out_path_unzipped}\n  - {out_path_standalone}")

if __name__ == '__main__':
    generate_calendar()
