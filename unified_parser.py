"""
Optimized Unified Parser for HALog
Streamlined for fast processing and reduced complexity
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Optional
import os


class UnifiedParser:
    """Optimized unified parser for LINAC logs and fault codes"""

    def __init__(self):
        self.fault_codes = {}
        self.parsing_stats = {"lines_processed": 0, "records_extracted": 0}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile essential regex patterns"""
        self.patterns = {
            "datetime": re.compile(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})"),
            "serial": re.compile(r"SN#?\s*(\d+)", re.IGNORECASE),
            "parameters": re.compile(
                r"([a-zA-Z][a-zA-Z0-9_\s]*[a-zA-Z0-9])"
                r"[:\s]*count\s*=\s*(\d+),?\s*"
                r"max\s*=\s*([\d.-]+),?\s*"
                r"min\s*=\s*([\d.-]+),?\s*"
                r"avg\s*=\s*([\d.-]+)",
                re.IGNORECASE
            )
        }

    def parse_linac_file(self, file_path: str, chunk_size: int = 1000,
                        progress_callback=None, cancel_callback=None) -> pd.DataFrame:
        """Parse LINAC file with optimized processing"""
        records = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()

            total_lines = len(lines)
            self.parsing_stats["lines_processed"] = 0

            for i, line in enumerate(lines):
                if cancel_callback and cancel_callback():
                    break

                parsed = self._parse_line(line.strip())
                if parsed:
                    records.extend(parsed)

                self.parsing_stats["lines_processed"] += 1

                # Update progress every 100 lines
                if i % 100 == 0 and progress_callback:
                    progress = (i / total_lines) * 100
                    progress_callback(progress)

            self.parsing_stats["records_extracted"] = len(records)

        except Exception as e:
            print(f"Error parsing file: {e}")

        return self._create_dataframe(records)

    def _parse_line(self, line: str) -> List[Dict]:
        """Parse single line for data"""
        records = []

        # Extract datetime
        dt_match = self.patterns["datetime"].search(line)
        if not dt_match:
            return records

        datetime_str = f"{dt_match.group(1)} {dt_match.group(2)}"

        # Extract serial
        serial_match = self.patterns["serial"].search(line)
        serial = serial_match.group(1) if serial_match else "Unknown"

        # Extract parameters
        param_match = self.patterns["parameters"].search(line)
        if param_match:
            param_name = param_match.group(1).strip()
            count = int(param_match.group(2))
            max_val = float(param_match.group(3))
            min_val = float(param_match.group(4))
            avg_val = float(param_match.group(5))

            # Create records for avg, min, max
            for stat_type, value in [("avg", avg_val), ("min", min_val), ("max", max_val)]:
                records.append({
                    'datetime': datetime_str,
                    'serial_number': serial,
                    'parameter_type': param_name,
                    'statistic_type': stat_type,
                    'value': value,
                    'count': count
                })

        return records

    def _create_dataframe(self, records: List[Dict]) -> pd.DataFrame:
        """Create and clean DataFrame"""
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        try:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.dropna(subset=['datetime'])
            df = df.sort_values('datetime')
            df = df.reset_index(drop=True)
        except Exception as e:
            print(f"Error creating DataFrame: {e}")

        return df

    # Fault code methods
    def load_fault_codes_from_uploaded_file(self, file_path: str) -> bool:
        """Load fault codes from file"""
        try:
            if not os.path.exists(file_path):
                return False

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Parse fault code line
                    match = re.match(r'^(\d+)\s*[:\-\s]+(.+)$', line)
                    if match:
                        code = match.group(1).strip()
                        description = match.group(2).strip()
                        self.fault_codes[code] = {
                            'description': description,
                            'source': 'uploaded',
                            'type': 'fault'
                        }

            print(f"Loaded {len(self.fault_codes)} fault codes")
            return True

        except Exception as e:
            print(f"Error loading fault codes: {e}")
            return False

    def search_fault_code(self, code: str) -> Dict:
        """Search for specific fault code"""
        code = str(code).strip()

        if code in self.fault_codes:
            return {
                'found': True,
                'code': code,
                'description': self.fault_codes[code]['description'],
                'source': self.fault_codes[code]['source'],
                'type': self.fault_codes[code]['type']
            }
        else:
            return {
                'found': False,
                'code': code,
                'description': 'Code not found',
                'source': 'none',
                'type': 'unknown'
            }

    def search_description(self, search_term: str) -> List:
        """Search fault codes by description"""
        results = []
        search_lower = search_term.lower()

        for code, data in self.fault_codes.items():
            if search_lower in data['description'].lower():
                results.append((code, data))

        return results[:20]  # Limit results

    def get_fault_code_statistics(self) -> Dict:
        """Get fault code statistics"""
        return {
            'total_codes': len(self.fault_codes),
            'sources': list(set(info['source'] for info in self.fault_codes.values()))
        }

    def get_parsing_stats(self) -> Dict:
        """Get parsing statistics"""
        return self.parsing_stats.copy()