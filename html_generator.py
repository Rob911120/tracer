from datetime import datetime
from typing import List, Dict, Optional
import os
import tempfile
import webbrowser


class HierarchicalHTMLGenerator:
    """Generate professional HTML report with hierarchical structure optimized for browser viewing and printing"""
    
    def __init__(self):
        # Hierarchy settings matching PDF generator
        self.level_spacing = 15  # Same as PDF generator
    
    def generate_report(self, data: List[Dict], output_path: str = None, project_info: Optional[Dict] = None):
        """Generate the hierarchical HTML report and optionally open in browser"""
        
        # Generate HTML content
        html_content = self._generate_html(data, project_info)
        
        # If no output path specified, create a temporary file
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.html', 
                delete=False, 
                encoding='utf-8',
                prefix='tracer_report_',
                errors='replace'
            )
            output_path = temp_file.name
            temp_file.write(html_content)
            temp_file.close()
        else:
            # Write to specified path with explicit UTF-8 encoding
            try:
                with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(html_content)
            except Exception as e:
                print(f"Error writing HTML file: {e}")
                raise
        
        return output_path
    
    def open_in_browser(self, file_path: str):
        """Open the HTML file in the default web browser"""
        webbrowser.open(f'file://{os.path.abspath(file_path)}')
    
    def _generate_html(self, data: List[Dict], project_info: Optional[Dict] = None) -> str:
        """Generate the complete HTML document"""
        
        # Generate dynamic styles based on data hierarchy levels
        dynamic_styles = self._generate_dynamic_styles(data)
        
        # Generate rows
        table_rows = self._generate_table_rows(data)
        
        # Project info
        project_number = ""
        if project_info and 'project_number' in project_info:
            project_number = project_info['project_number']
        
        # Current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        
        # Calculate statistics
        total_items = len(data)
        
        html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <meta name="description" content="Spårbarhetsrapport genererad från Excel-filer">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="robots" content="noindex, nofollow">
    <title>Spårbarhetsrapport{' - ' + project_number if project_number else ''}</title>
    <style>
        /* Cross-browser compatibility and performance optimizations */
        html {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            text-size-adjust: 100%;
        }}
        
        * {{
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            box-sizing: border-box;
        }}
        
        /* Fix for min-height stretch compatibility */
        .container {{
            min-height: -webkit-fill-available;
            min-height: stretch;
            min-height: 100vh;
        }}
        
        {dynamic_styles}
        @media print {{
            @page {{
                size: A4 landscape;
                margin: 10mm 10mm 15mm 10mm;
            }}
            
            * {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
            
            html, body {{
                width: 297mm !important;
                height: 210mm !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            body {{
                font-size: 9pt !important;
                line-height: 1.3 !important;
                padding: 0 !important;
            }}
            
            .container {{
                padding: 10mm !important;
                box-shadow: none !important;
                border-radius: 0 !important;
            }}
            
            .no-print {{
                display: none !important;
            }}
            
            table {{
                page-break-inside: auto;
                font-size: 8pt !important;
            }}
            
            tr {{
                page-break-inside: avoid;
                page-break-after: auto;
            }}
            
            thead {{
                display: table-header-group;
            }}
            
            .header {{
                page-break-after: avoid;
                margin-bottom: 10px !important;
                padding-bottom: 10px !important;
            }}
            
            h1 {{
                font-size: 14pt !important;
                margin: 5px 0 !important;
            }}
            
            .info-section {{
                margin: 5px 0 !important;
            }}
            
            th {{
                font-size: 8pt !important;
                padding: 4px 6px !important;
            }}
            
            td {{
                font-size: 8pt !important;
                padding: 3px 6px !important;
            }}
            
            /* Dynamic styles will handle indentation in print */
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #000;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .header {{
            border-bottom: 1px solid #ddd;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        
        h1 {{
            font-size: 16pt;
            font-weight: 600;
            color: #000;
            text-align: center;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }}
        
        .info-section {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0 5px 0;
            font-size: 9pt;
            color: #666;
        }}
        
        .project-info {{
            font-weight: 500;
        }}
        
        .date-time {{
            text-align: right;
        }}
        
        /* Small statistics bar */
        .stats-bar {{
            font-size: 8pt;
            color: #999;
            text-align: center;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 9pt;
            border: 1px solid #ddd;
        }}
        
        thead {{
            background: #333;
            color: white;
        }}
        
        th {{
            padding: 8px 10px;
            text-align: left;
            font-weight: 500;
            font-size: 9pt;
            letter-spacing: 0.2px;
            border-right: 1px solid #555;
        }}
        
        th:last-child {{
            border-right: none;
        }}
        
        tbody tr {{
            border-bottom: 1px solid #eee;
        }}
        
        tbody tr:hover {{
            background: #fafafa;
        }}
        
        td {{
            padding: 6px 10px;
            font-size: 9pt;
            vertical-align: middle;
            border-right: 1px solid #f5f5f5;
        }}
        
        td:last-child {{
            border-right: none;
        }}
        
        /* Base hierarchy styles - will be overridden by dynamic styles */
        .level-0 {{
            font-weight: 600;
            background: #fafafa;
        }}
        
        /* Separator row styling */
        .separator-row {{
            background: transparent !important;
        }}
        
        .separator-row:hover {{
            background: transparent !important;
        }}
        
        .separator-row td {{
            border: none !important;
            padding: 0 !important;
        }}
        
        /* Batch and charge number cells */
        .batch-cell, .charge-cell {{
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 8pt;
            color: #555;
        }}
        
        /* Quantity alignment */
        .quantity {{
            text-align: right;
            font-weight: 500;
        }}
        
        /* Print/Export buttons */
        .actions {{
            margin: 20px 0;
            text-align: center;
        }}
        
        .btn {{
            background: #fff;
            color: #333;
            border: 1px solid #ddd;
            padding: 8px 20px;
            font-size: 10pt;
            border-radius: 4px;
            cursor: pointer;
            margin: 0 5px;
            transition: all 0.2s;
        }}
        
        .btn:hover {{
            background: #f5f5f5;
            border-color: #999;
        }}
        
        .btn-primary {{
            background: #333;
            color: white;
            border-color: #333;
        }}
        
        .btn-primary:hover {{
            background: #555;
            border-color: #555;
        }}
        
        /* Column widths - adjusted without grundtyp column */
        .col-artikel {{
            width: 30%;
        }}
        
        .col-artikeltyp {{
            width: 10%;
            text-align: center;
        }}
        
        .col-benamning {{
            width: 35%;
        }}
        
        .col-kvantitet {{
            width: 8%;
            text-align: right;
        }}
        
        .col-batch {{
            width: 8%;
        }}
        
        .col-charge {{
            width: 9%;
        }}
        
        /* Footer */
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #eee;
            text-align: center;
            font-size: 8pt;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SPÅRBARHETSRAPPORT</h1>
            
            <div class="info-section">
                <div class="project-info">
                    {f'Projekt: {project_number}' if project_number else 'Projekt: Ej angivet'}
                </div>
                <div class="date-time">
                    {current_date} {current_time}
                </div>
            </div>
            
            <div class="stats-bar">
                {total_items} artiklar
            </div>
        </div>
        
        <div class="actions no-print">
            <button class="btn btn-primary" onclick="window.print()" title="Skriv ut eller spara som PDF" aria-label="Skriv ut eller spara som PDF">Skriv ut / Spara som PDF</button>
            <button class="btn" onclick="window.close()" title="Stäng fönstret" aria-label="Stäng fönstret">Stäng</button>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th class="col-artikel">Artikel/Operation</th>
                    <th class="col-artikeltyp">Köpt/Tillverkad</th>
                    <th class="col-benamning">Benämning</th>
                    <th class="col-kvantitet">Kvantitet</th>
                    <th class="col-batch">Batchnummer</th>
                    <th class="col-charge">Chargenummer</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        
        <div class="footer no-print">
            <p>Spårbarhetsprogram | {current_date}</p>
        </div>
    </div>
    
    <script>
        // Add keyboard shortcut for printing
        document.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {{
                e.preventDefault();
                window.print();
            }}
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def _get_max_levels(self, data: List[Dict]) -> int:
        """Get maximum number of levels in the document"""
        return max([row.get('Nivå', 0) for row in data]) if data else 0
    
    def _get_style_mapping(self, max_levels: int) -> Dict[int, int]:
        """Map actual levels to master style levels for consistent appearance"""
        if max_levels <= 2:
            return {0: 0, 1: 2}              # 2 levels → use master styles 0,2
        elif max_levels == 3:
            return {0: 0, 1: 1, 2: 3}        # 3 levels → use master styles 0,1,3
        elif max_levels == 4:
            return {0: 0, 1: 1, 2: 2, 3: 4}  # 4 levels → use master styles 0,1,2,4
        elif max_levels == 5:
            return {0: 0, 1: 1, 2: 2, 3: 3, 4: 5}  # 5 levels → use master styles 0,1,2,3,5
        else:
            return {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}  # 6+ levels → use all master styles
    
    def _get_master_styles(self) -> Dict[int, Dict[str, any]]:
        """Master styling table with 6-level typographic hierarchy"""
        return {
            0: {"font_size": 16, "font_weight": 700, "color": "#000000", "text_transform": "uppercase", "font_style": "normal"},
            1: {"font_size": 13, "font_weight": 500, "color": "#000000", "text_transform": "none", "font_style": "normal"},
            2: {"font_size": 11, "font_weight": 400, "color": "#000000", "text_transform": "none", "font_style": "normal"},
            3: {"font_size": 10, "font_weight": 400, "color": "#000000", "text_transform": "none", "font_style": "normal"},
            4: {"font_size": 9, "font_weight": 400, "color": "#000000", "text_transform": "none", "font_style": "normal"},
            5: {"font_size": 8, "font_weight": 400, "color": "#666666", "text_transform": "none", "font_style": "normal"}
        }
    
    def _generate_dynamic_styles(self, data: List[Dict]) -> str:
        """Generate dynamic CSS styles based on hierarchy levels in data"""
        max_levels = self._get_max_levels(data)
        style_mapping = self._get_style_mapping(max_levels)
        master_styles = self._get_master_styles()
        
        css_rules = []
        
        # Generate styles for each level present in data
        for level in range(max_levels + 1):
            master_level = style_mapping.get(level, 4)
            style = master_styles[master_level]
            
            # Create CSS rule for this level
            css_rules.append(f"""
        .level-{level} {{
            font-size: {style['font_size']}pt;
            font-weight: {style['font_weight']};
            color: {style['color']};
        }}
        
        .level-{level} td:first-child {{
            font-size: {style['font_size']}pt;
            font-weight: {style['font_weight']};
            color: {style['color']};
            text-transform: {style['text_transform']};
            font-style: {style['font_style']};
        }}
        
        .indent-{level} {{
            margin-left: {level * 20}px;
            padding-left: 10px;
            text-indent: {level * 15}px;
            -webkit-text-indent: {level * 15}px;
            -moz-text-indent: {level * 15}px;
        }}
        
        .indent-{level}::before {{
            content: "{' ' * (level * 2)}";
            white-space: pre;
            font-family: monospace;
            display: inline;
        }}
        
        @media print {{
            .level-{level} td:first-child {{
                font-size: {style['font_size']}pt !important;
                font-weight: {style['font_weight']} !important;
                color: {style['color']} !important;
                text-transform: {style['text_transform']} !important;
                font-style: {style['font_style']} !important;
            }}
            
            .indent-{level} {{
                margin-left: {level * 20}px !important;
                padding-left: 10px !important;
                text-indent: {level * 15}px !important;
            }}
            
            .indent-{level}::before {{
                content: "{' ' * (level * 2)}" !important;
                white-space: pre !important;
                font-family: monospace !important;
            }}
        }}""")
        
        return '\n'.join(css_rules)
    
    def _generate_table_rows(self, data: List[Dict]) -> str:
        """Generate table rows from data"""
        rows = []
        
        for i, item in enumerate(data):
            level = item.get('Nivå', 0)
            artikeltyp_raw = item.get('Artikeltyp/Operation', '')
            
            # Förkorta artikeltyp
            if 'köpt' in artikeltyp_raw.lower():
                artikeltyp = 'Kpt'
            elif 'tillverkad' in artikeltyp_raw.lower():
                artikeltyp = 'Tlv'
            else:
                artikeltyp = artikeltyp_raw[:3] if artikeltyp_raw else ''
            
            artikel = item.get('Artikel/Operation', '').strip()
            benamning = item.get('Benämning', '')
            kvantitet = item.get('Kvantitet', '')
            batch = item.get('Batchnummer', '')
            charge = item.get('Chargenummer', '')
            
            # Add separator row before new level 0 items (except for the first item)
            if level == 0 and i > 0:
                separator_row = f"""
                <tr class="separator-row">
                    <td colspan="6" style="height: 15px; background: transparent; border: none;"></td>
                </tr>"""
                rows.append(separator_row)
            
            # Create cell with multiple indentation methods for cross-browser compatibility  
            indent_spaces = "&nbsp;" * (level * 4)  # Non-breaking spaces
            indent_style = f"margin-left: {level * 20}px; padding-left: 10px;"
            artikel_cell = f'<span class="indent-{level}" style="{indent_style}">{indent_spaces}{artikel}</span>'
            
            row = f"""
                <tr class="level-{level}">
                    <td>{artikel_cell}</td>
                    <td style="text-align: center;">{artikeltyp}</td>
                    <td>{benamning}</td>
                    <td class="quantity">{kvantitet}</td>
                    <td class="batch-cell">{batch}</td>
                    <td class="charge-cell">{charge}</td>
                </tr>"""
            
            rows.append(row)
        
        return ''.join(rows)