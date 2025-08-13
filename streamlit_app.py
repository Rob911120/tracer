# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import os
import sys
from datetime import datetime
from traceability_parser import TraceabilityParser
from traceability_model import TraceabilityDatabase
from html_generator import HierarchicalHTMLGenerator

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    import locale
    locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8' if 'sv_SE' in locale.locale_alias else 'en_US.UTF-8')

# Page config
st.set_page_config(
    page_title="Spårbarhetsrapport",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .upload-area {
        padding: 2rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 2rem;
    }
    h1 {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stats-box {
        background-color: #e5e7eb;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

def create_hierarchical_export_data(database):
    """Create hierarchical data for HTML export that preserves original Excel order"""
    rows = []
    
    # Check if we have hierarchical data (from nivålista)
    if database.all_items_in_order:
        # Use ALL items in order (including duplicates) to preserve exact original structure
        for item in database.all_items_in_order:
            # Get the article data for additional info (batch/charge)
            article = database.articles.get(item.artikelnummer)
            
            # Get batch and charge numbers from the article (aggregated)
            batch_numbers = list(article.get_unique_batch_numbers()) if article else []
            charge_numbers = list(article.get_unique_charge_numbers()) if article else []
            
            # Don't add indentation here - HTML generator handles it with CSS
            # Include Grundtyp if available
            row_data = {
                'Artikeltyp/Operation': item.artikeltyp or '',
                'Grundtyp': item.grundtyp or '' if hasattr(item, 'grundtyp') else '',
                'Artikel/Operation': item.artikelnummer,  # Clean article number without indentation
                'Benämning': item.artikelbenaming or '',
                'Kvantitet': str(item.kvantitet) if item.kvantitet else '',
                'Batchnummer': ', '.join(batch_numbers) if batch_numbers else '',
                'Chargenummer': ', '.join(charge_numbers) if charge_numbers else '',
                'Nivå': item.level  # Keep for HTML formatting - this is what HTML generator uses for styling
            }
            rows.append(row_data)
    else:
        # Fallback for non-hierarchical data (from lagerlogg or search files)
        for artikelnummer, article in database.articles.items():
            batch_numbers = list(article.get_unique_batch_numbers())
            charge_numbers = list(article.get_unique_charge_numbers())
            
            row_data = {
                'Artikeltyp/Operation': article.artikeltyp or '',
                'Grundtyp': '',
                'Artikel/Operation': article.artikelnummer,
                'Benämning': article.artikelbenaming or '',
                'Kvantitet': str(article.kvantitet) if article.kvantitet else '',
                'Batchnummer': ', '.join(batch_numbers) if batch_numbers else '',
                'Chargenummer': ', '.join(charge_numbers) if charge_numbers else '',
                'Nivå': 0
            }
            rows.append(row_data)
    
    return rows

def main():
    # Header
    st.markdown("<h1>📊 Spårbarhetsrapport</h1>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ladda upp Excel-filer för att generera spårbarhetsrapport</p>', unsafe_allow_html=True)
    
    # Single file uploader that accepts multiple files
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 📁 Välj eller dra in Excel-filer")
        uploaded_files = st.file_uploader(
            "Du kan välja eller dra in flera filer samtidigt",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="Dra och släpp flera filer här eller klicka för att välja. Du kan ladda upp 2 eller fler filer."
        )
    
    with col2:
        st.markdown("### ")  # Empty space for alignment
        if st.button("🗑️ Rensa allt", help="Rensa alla uppladdade filer och genererade rapporter"):
            # Clear all session state
            st.session_state.clear()
            st.rerun()
    
    # Process files if at least 2 are uploaded
    if uploaded_files and len(uploaded_files) >= 2:
        # Check if files have changed - if so, clear cached data
        current_files = [f.name for f in uploaded_files]
        if 'last_uploaded_files' not in st.session_state or st.session_state.get('last_uploaded_files') != current_files:
            # Files have changed, clear all cached data
            for key in ['html_content', 'report_generated', 'last_uploaded_files']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state['last_uploaded_files'] = current_files
        
        try:
            with st.spinner('Bearbetar filer...'):
                # Create fresh parser and database
                parser = TraceabilityParser()
                database = parser.get_database()
                
                # Save uploaded files temporarily with original names preserved
                temp_files = []
                original_names = []
                for uploaded_file in uploaded_files:
                    # Create temp file with proper extension
                    suffix = Path(uploaded_file.name).suffix
                    with tempfile.NamedTemporaryFile(
                        suffix=suffix, 
                        delete=False,
                        mode='wb',
                        prefix='tracer_'
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        temp_files.append(tmp_file.name)
                        original_names.append(uploaded_file.name)
                
                # Parse files
                loaded_files = []
                for i, temp_path in enumerate(temp_files):
                    try:
                        parsed_items = parser.parse_file(Path(temp_path), original_names[i])
                        loaded_files.append(temp_path)
                    except Exception as e:
                        st.error(f"Fel vid parsning av {original_names[i]}: {str(e)}")
                
                # Clean up temp files
                for temp_path in temp_files:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                
                # Show statistics
                total_articles = len(database.articles)
                total_items = sum(len(article.items) for article in database.articles.values())
                
                # Show loaded files
                st.markdown("#### Laddade filer:")
                for uploaded_file in uploaded_files:
                    st.markdown(f"✅ {uploaded_file.name}")
                
                st.markdown(f"""
                <div class="stats-box">
                    <strong>📈 Statistik:</strong><br>
                    • Artiklar: {total_articles}<br>
                    • Totalt antal poster: {total_items}<br>
                    • Laddade filer: {len(uploaded_files)}
                </div>
                """, unsafe_allow_html=True)
                
                # Generate HTML report
                if st.button("🔍 Generera spårbarhetsrapport", type="primary", use_container_width=True):
                    with st.spinner('Genererar rapport...'):
                        # Create hierarchical data
                        hierarchical_data = create_hierarchical_export_data(database)
                        
                        # Extract project info from loaded files if available
                        project_info = {}
                        for uploaded_file in uploaded_files:
                            if 'p5' in uploaded_file.name.lower() or 'p-5' in uploaded_file.name.lower():
                                # Try to extract project number from filename
                                import re
                                match = re.search(r'[Pp]-?(\d{5})', uploaded_file.name)
                                if match:
                                    project_info['project_number'] = f"P{match.group(1)}"
                                    break
                        
                        # Generate HTML using the same method as original app
                        html_gen = HierarchicalHTMLGenerator()
                        html_path = html_gen.generate_report(hierarchical_data, None, project_info)
                        
                        # Read the generated HTML with explicit UTF-8 encoding
                        try:
                            with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
                                html_content = f.read()
                        except Exception as e:
                            st.error(f"Fel vid läsning av HTML-fil: {str(e)}")
                            html_content = ""
                        
                        # Store HTML content in session state
                        st.session_state['html_content'] = html_content
                        st.session_state['report_generated'] = True
                        
                        st.success("✅ Rapport genererad!")
                
                # Show download button and preview if report is generated
                if 'report_generated' in st.session_state and st.session_state['report_generated']:
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="⬇️ Ladda ner HTML-rapport",
                            data=st.session_state['html_content'],
                            file_name=f"sparbarhetsrapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html",
                            use_container_width=True,
                            type="primary",
                            help="Ladda ner rapporten och öppna den i din webbläsare för bästa visning"
                        )
                    
                    with col2:
                        st.info("💡 **Tips:** Ladda ner filen och öppna den i din webbläsare för full funktionalitet och korrekt formatering.")
                    
                    # Show a simplified preview
                    with st.expander("📄 Förhandsvisning (förenklad)", expanded=False):
                        st.markdown("**OBS:** Detta är en förenklad visning. Ladda ner och öppna HTML-filen för fullständig rapport.")
                        # Recreate the data for preview
                        preview_data = create_hierarchical_export_data(database)
                        if preview_data:
                            import pandas as pd
                            df = pd.DataFrame(preview_data)
                            # Remove the Nivå column for display
                            if 'Nivå' in df.columns:
                                df = df.drop('Nivå', axis=1)
                            # Remove Grundtyp if it's empty
                            if 'Grundtyp' in df.columns and df['Grundtyp'].str.strip().eq('').all():
                                df = df.drop('Grundtyp', axis=1)
                            st.dataframe(df, use_container_width=True)
                
        except Exception as e:
            st.error(f"Ett fel uppstod: {str(e)}")
            st.exception(e)
    
    elif uploaded_files and len(uploaded_files) == 1:
        # Show message if only one file is uploaded
        st.warning("⚠️ Vänligen ladda upp minst 2 Excel-filer för att generera en spårbarhetsrapport.")
        st.markdown(f"**Laddad fil:** {uploaded_files[0].name}")
        st.markdown("Dra in eller välj ytterligare filer i samma ruta ovan.")
    
    else:
        # Show instructions when no files are uploaded
        st.info("""
        📌 **Instruktioner:**
        1. Dra och släpp eller klicka för att välja 2 eller fler Excel-filer
        2. Du kan markera flera filer samtidigt (håll Ctrl/Cmd intryckt)
        3. Eller dra och släpp alla filer direkt i uppladdningsrutan
        4. Filerna ska innehålla spårbarhetsdata (t.ex. nivålista, lagerlogg, eller sök i spårbarhet)
        5. När filerna är uppladdade kommer statistik att visas
        6. Klicka på "Visa spårbarhetsrapport" för att generera och visa rapporten
        7. Du kan skriva ut eller spara rapporten som PDF direkt från webbläsaren
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #9ca3af; font-size: 0.9rem;'>"
        "Spårbarhetsprogram | Version 2.0 | Streamlit Cloud"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()