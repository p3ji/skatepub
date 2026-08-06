import os
import re
import unittest
from bs4 import BeautifulSoup

class TestCanSkateCalendar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html_path = os.path.join('docs', 'calendar', 'unzipped_docx', 'CanSkate202627Calendar.docx.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
        cls.tables = cls.soup.find_all('table')

    def test_month_count_and_headers(self):
        """Verify all 7 months exist, use 2026/2027 Season, and carry no stale 2025/2026 headers."""
        self.assertEqual(len(self.tables), 7, "Must contain exactly 7 monthly calendar tables.")
        expected_months = [
            "September 2026", "October 2026", "November 2026",
            "December 2026", "January 2027", "February 2027", "March 2027"
        ]
        self.assertNotIn("2025/2026", self.html_content, "Calendar must not contain stale 2025/2026 references.")
        
        for idx, expected in enumerate(expected_months):
            tbl_text = self.tables[idx].get_text()
            self.assertIn(expected, tbl_text, f"Table {idx} must contain {expected}")
            self.assertIn("2026/2027 Season", tbl_text, f"Table {idx} must bear 2026/2027 Season header")

    def test_session_counts_per_day_of_week(self):
        """Verify exact session counts for Sunday(24), Monday(26), Wednesday(24), Friday(24), Saturday(24)."""
        counts = {'Sunday': 0, 'Monday': 0, 'Wednesday': 0, 'Friday': 0, 'Saturday': 0}
        last_sessions = {'Sunday': None, 'Monday': None, 'Wednesday': None, 'Friday': None, 'Saturday': None}

        # DOW column index mapping: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        dow_names = {0: 'Sunday', 1: 'Monday', 3: 'Wednesday', 5: 'Friday', 6: 'Saturday'}

        for tbl in self.tables:
            rows = tbl.find_all('tr')[2:] # skip title and DOW header rows
            for r in rows:
                cells = r.find_all(['td', 'th'])
                for c_idx, cell in enumerate(cells):
                    if c_idx in dow_names:
                        txt = cell.get_text(' ', strip=True)
                        m = re.search(r'Session\s*#(\d+)', txt)
                        if m:
                            s_num = int(m.group(1))
                            counts[dow_names[c_idx]] += 1
                            if 'Last Session' in txt:
                                last_sessions[dow_names[c_idx]] = s_num

        self.assertEqual(counts['Sunday'], 24, "Sunday must have 24 active sessions.")
        self.assertEqual(counts['Monday'], 27, "Monday must have 27 active sessions.")
        self.assertEqual(counts['Wednesday'], 24, "Wednesday must have 24 active sessions.")
        self.assertEqual(counts['Friday'], 24, "Friday must have 24 active sessions.")
        self.assertEqual(counts['Saturday'], 24, "Saturday must have 24 active sessions.")

        self.assertEqual(last_sessions['Sunday'], 24, "Sunday Last Session must be #24.")
        self.assertEqual(last_sessions['Monday'], 27, "Monday Last Session must be #27.")
        self.assertEqual(last_sessions['Wednesday'], 24, "Wednesday Last Session must be #24.")
        self.assertEqual(last_sessions['Friday'], 24, "Friday Last Session must be #24.")
        self.assertEqual(last_sessions['Saturday'], 24, "Saturday Last Session must be #24.")

    def test_no_skating_dates(self):
        """Verify no-skating dates carry NO SKATING and no session numbers."""
        no_skate_dates = [
            ("December 2026", 20), ("December 2026", 21), ("December 2026", 23),
            ("December 2026", 25), ("December 2026", 26), ("December 2026", 27),
            ("December 2026", 28), ("December 2026", 30), ("January 2027", 1), ("January 2027", 2)
        ]

        for m_name, d_num in no_skate_dates:
            found = False
            for tbl in self.tables:
                if m_name in tbl.get_text():
                    rows = tbl.find_all('tr')[2:]
                    for r in rows:
                        for cell in r.find_all(['td', 'th']):
                            txt = cell.get_text(' ', strip=True)
                            tokens = txt.split()
                            if tokens and tokens[0] == str(d_num):
                                self.assertIn("NO SKATING", txt, f"{m_name} {d_num} must state NO SKATING")
                                self.assertNotIn("Session #", txt, f"{m_name} {d_num} must not contain a Session number")
                                found = True
                                break
            self.assertTrue(found, f"Could not locate date {m_name} {d_num}")

    def test_no_max_registration_capacity(self):
        """Verify max registration capacities (e.g. Max: 60, 30, 8, etc.) are excluded."""
        for tbl in self.tables:
            rows = tbl.find_all('tr')[2:]
            for r in rows:
                for cell in r.find_all(['td', 'th']):
                    txt = cell.get_text(' ', strip=True)
                    if "Session #" in txt:
                        self.assertNotIn("Max Registration", txt)
                        self.assertNotIn("Max:", txt)
                        self.assertNotIn("Max ", txt)

if __name__ == '__main__':
    unittest.main()
