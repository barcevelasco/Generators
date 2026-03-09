import streamlit as st
import requests
import pandas as pd
import html
from io import BytesIO
import datetime
import docx
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from bs4 import BeautifulSoup
import calendar
import time
import re
from dateutil import parser

# ==========================================
# CONFIGURACIÓN INICIAL Y ESTILOS
# ==========================================
st.set_page_config(page_title="Boletín Mensual", layout="wide")

st.markdown("""
    <style>
    div.stButton > button, div.stDownloadButton > button {
        background-color: #00205B !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #00153D !important;
        color: white !important;
    }
    span[data-baseweb="tag"] {
        background-color: #00205B !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# UTILIDADES DE FORMATO
# ==========================================
def clean_author_name(name):
    """Convierte nombres en mayúsculas a formato de nombre propio (Ej: UEDA Kazuo -> Ueda Kazuo)"""
    if not name:
        return ""
    cleaned = name.strip().title()
    cleaned = re.sub(r'\b([A-Z])\.\s*([A-Z])', lambda m: f"{m.group(1)}. {m.group(2)}", cleaned)
    return cleaned

# ==========================================
# FUNCIONES DE EXTRACCIÓN (BACKEND)
# ==========================================

# --- SECCIÓN: REPORTES ---
@st.cache_data(show_spinner=False)
def load_reportes_cef(start_date_str, end_date_str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    
    rows, page = [], 1
    while True:
        url = f"https://www.fsb.org/publications/?dps_paged={page}"
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            items = soup.find_all('div', class_=lambda c: c and 'post-excerpt' in c)
            if not items: break
            
            items_found = 0
            for item in items:
                title_div = item.find('div', class_='post-title')
                if not title_div or not title_div.find('a'): continue
                
                a_tag = title_div.find('a')
                titulo_raw = a_tag.get_text(strip=True)
                link = a_tag.get('href', '')
                
                date_div = item.find('div', class_='post-date')
                parsed_date = None
                if date_div:
                    date_str = date_div.get_text(strip=True)
                    try: parsed_date = parser.parse(date_str)
                    except: pass
                
                if not parsed_date: continue
                
                if not any(r['Link'] == link for r in rows):
                    rows.append({"Date": parsed_date, "Title": titulo_raw, "Link": link, "Organismo": "CEF"})
                    items_found += 1
            
            if items_found == 0 or (rows and rows[-1]['Date'] < start_date): break
            page += 1
            time.sleep(0.5) 
            
        except Exception as e:
            print("Error extrayendo CEF (Reportes):", e)
            break
            
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_reportes_ocde(start_date_str, end_date_str):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    rows = []
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    year = start_date.year
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        url = f"https://www.oecd.org/en/search/publications.html?orderBy=mostRecent&page=0&facetTags=oecd-content-types%3Apublications%2Freports%2Coecd-languages%3Aen&minPublicationYear={year}&maxPublicationYear={year}"
        
        driver.get(url)
        time.sleep(12) 
        
        js_script = """
        let linksData = [];
        function findLinks(root) {
            let els = root.querySelectorAll('*');
            els.forEach(el => {
                if (el.shadowRoot) {
                    findLinks(el.shadowRoot);
                }
                if (el.tagName === 'A' && el.href) {
                    let text = el.innerText || el.textContent;
                    let aria = el.getAttribute('aria-label') || el.getAttribute('title') || '';
                    let final_text = text.trim() ? text.trim() : aria.trim();
                    
                    if(final_text.length > 15) { 
                        linksData.push({
                            title: final_text,
                            link: el.href
                        });
                    }
                }
            });
        }
        findLinks(document);
        return linksData;
        """
        
        extracted_links = driver.execute_script(js_script)
        driver.quit()
        
        for item in extracted_links:
            href = item['link'].lower()
            title = item['title'].replace('\n', ' ')
            
            firmas_validas = ['/publications/', '/reports/', 'oecd-ilibrary.org', '/books/']
            
            if any(firma in href for firma in firmas_validas):
                if any(basura in title.lower() for x in ['download', 'read more', 'pdf', 'buy', 'search', 'subscribe']):
                    continue
                
                if not any(r['Link'] == item['link'] for r in rows):
                    rows.append({"Date": start_date, "Title": title, "Link": item['link'], "Organismo": "OCDE"})
                    
    except Exception as e:
        print("Error extrayendo OCDE:", e)
        
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_reportes_bid(start_date_str, end_date_str):
    base_domain = "https://publications.iadb.org"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    
    rows, page = [], 0
    meses_en = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    
    while page < 3: 
        url = f"{base_domain}/en/publications?f%5B0%5D=type%3AAnnual%20Reports&page={page}"
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_='views-row')
            if not items: break
            
            for item in items:
                title_div = item.select_one('.views-field-field-title')
                if not title_div or not title_div.find('a'): continue
                
                a_tag = title_div.find('a')
                titulo_raw = a_tag.get_text(strip=True)
                link = base_domain + a_tag.get('href', '')
                
                date_div = item.select_one('.views-field-field-date-issued-text')
                parsed_date = None
                if date_div:
                    date_span = date_div.find('span', class_='field-content')
                    if date_span: 
                        date_str = date_span.get_text(strip=True).lower()
                        match = re.search(r'([a-z]{3})\w*\s+(\d{4})', date_str)
                        if match:
                            m_str = match.group(1)
                            y_str = int(match.group(2))
                            if m_str in meses_en:
                                parsed_date = datetime.datetime(y_str, meses_en[m_str], 1)
                        else:
                            try: parsed_date = parser.parse(date_str, default=datetime.datetime(2000, 1, 1))
                            except: pass
                
                if not parsed_date: continue
                
                autor = ""
                author_div = item.select_one('.views-field-field-author')
                if author_div:
                    author_span = author_div.find('span', class_='field-content')
                    if author_span: 
                        autor = clean_author_name(author_span.get_text(strip=True).replace(';', ', '))
                
                final_t = f"{autor}: {titulo_raw}" if autor else titulo_raw
                
                if not any(r['Link'] == link for r in rows):
                    rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "BID"})
                    
            page += 1
            time.sleep(0.5)
        except Exception as e:
            break
        
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
        df = df[df["Date"] >= start_date]
    return df

@st.cache_data(show_spinner=False)
def load_reportes_bpi(start_date_str, end_date_str):
    urls_api = [
        "https://www.bis.org/api/document_lists/bcbspubls.json",
        "https://www.bis.org/api/document_lists/cpmi_publs.json"
    ]
    urls_html = ["https://www.bis.org/ifc/publications.htm"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    
    rows = []
    
    for url in urls_api:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            data = res.json()
            lista_documentos = data.get("list", {})
            for path, doc_info in lista_documentos.items():
                titulo = html.unescape(doc_info.get("short_title", ""))
                if not titulo: continue
                link = "https://www.bis.org" + doc_info.get("path", "")
                if not link.endswith(".htm") and not link.endswith(".pdf"):
                    link += ".htm"
                date_str = doc_info.get("publication_start_date", "")
                parsed_date = None
                if date_str:
                    try: parsed_date = parser.parse(date_str)
                    except: pass
                if not parsed_date: continue
                if parsed_date >= start_date:
                    rows.append({"Date": parsed_date, "Title": titulo, "Link": link, "Organismo": "BPI"})
        except Exception as e:
            continue

    for url in urls_html:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            content_div = soup.find('div', id='cmsContent')
            if not content_div: continue
            for p in content_div.find_all('p'):
                a_tag = p.find('a')
                if not a_tag: continue
                titulo = a_tag.get_text(strip=True)
                href = a_tag.get('href', '')
                if not href or 'index.htm' in href: continue 
                link = "https://www.bis.org" + href if href.startswith('/') else href
                full_text = p.get_text(strip=True)
                date_str = full_text.replace(titulo, '').strip(', ')
                parsed_date = None
                if date_str:
                    try: parsed_date = parser.parse(date_str)
                    except: pass
                if not parsed_date:
                    match = re.search(r'\b(20\d{2})\b', titulo)
                    if match: parsed_date = datetime.datetime(int(match.group(1)), 1, 1)
                if not parsed_date: continue
                if parsed_date >= start_date:
                    rows.append({"Date": parsed_date, "Title": titulo, "Link": link, "Organismo": "BPI"})
        except Exception as e:
            continue
            
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=['Link'])
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

# --- SECCIÓN: PUBLICACIONES INSTITUCIONALES ---
@st.cache_data(show_spinner=False)
def load_pub_inst_cef(start_date_str, end_date_str):
    """Extractor para Publicaciones Institucionales del CEF (FSB)"""
    url = "https://www.fsb.org/publications/key-regular-publications/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)

    rows = []
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # El CEF organiza estas publicaciones en bloques de filas (wp-bootstrap-blocks-row)
        sections = soup.find_all('div', class_='wp-bootstrap-blocks-row')
        
        for section in sections:
            # Buscamos el título del bloque (h2)
            h2 = section.find('h2')
            if not h2: continue
            base_title = h2.get_text(strip=True)
            
            # 1. Extraer el "Latest Report" (Botón principal)
            latest_btn = section.find('button', class_='btn-primary')
            if latest_btn and latest_btn.find('a'):
                a_tag = latest_btn.find('a')
                link = "https://www.fsb.org" + a_tag['href'] if a_tag['href'].startswith('/') else a_tag['href']
                
                # Extraer fecha del texto del botón (ej: "January 2026")
                date_match = re.search(r'\((.*?)\)', a_tag.get_text())
                parsed_date = None
                if date_match:
                    try: parsed_date = parser.parse(date_match.group(1))
                    except: pass
                
                if parsed_date and parsed_date >= start_date:
                    rows.append({"Date": parsed_date, "Title": f"{base_title}: Latest Report", "Link": link, "Organismo": "CEF"})

            # 2. Extraer "Previous Reports" (Menú desplegable)
            dropdown = section.find('div', class_='dropdown-menu')
            if dropdown:
                links = dropdown.find_all('a')
                for l in links:
                    link = l['href']
                    year_text = l.get_text(strip=True)
                    # Intentamos crear una fecha basada en el año del link
                    try: parsed_date = datetime.datetime(int(year_text), 1, 1)
                    except: parsed_date = None
                    
                    if parsed_date and parsed_date >= start_date:
                        rows.append({"Date": parsed_date, "Title": f"{base_title} ({year_text})", "Link": link, "Organismo": "CEF"})

    except Exception as e:
        print(f"Error extrayendo Pub Institucionales CEF:", e)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=['Link'])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date", ascending=False)
    return df
@st.cache_data(show_spinner=False)
def load_pub_inst_bpi(start_date_str, end_date_str):
    urls_api = [
        "https://www.bis.org/api/document_lists/annualeconomicreports.json",
        "https://www.bis.org/api/document_lists/quarterlyreviews.json"
    ]
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)

    rows = []
    for url in urls_api:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            data = res.json()
            lista_documentos = data.get("list", {})
            for path, doc_info in lista_documentos.items():
                titulo = html.unescape(doc_info.get("short_title", ""))
                if not titulo: continue
                
                link = "https://www.bis.org" + doc_info.get("path", "")
                if not link.endswith(".htm") and not link.endswith(".pdf"):
                    link += ".htm"
                    
                date_str = doc_info.get("publication_start_date", "")
                parsed_date = None
                if date_str:
                    try: parsed_date = parser.parse(date_str)
                    except: pass
                if not parsed_date: continue
                
                if parsed_date >= start_date:
                    rows.append({"Date": parsed_date, "Title": titulo, "Link": link, "Organismo": "BPI"})
        except Exception as e:
            continue

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=['Link'])
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

# --- SECCIÓN: INVESTIGACIÓN ---
@st.cache_data(show_spinner=False)
def load_investigacion_bpi(start_date_str, end_date_str):
    urls_api = [
        "https://www.bis.org/api/document_lists/bispapers.json",
        "https://www.bis.org/api/document_lists/wppubls.json"
    ]
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)

    rows = []
    for url in urls_api:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            data = res.json()
            lista_documentos = data.get("list", {})
            for path, doc_info in lista_documentos.items():
                titulo = html.unescape(doc_info.get("short_title", ""))
                if not titulo: continue
                link = "https://www.bis.org" + doc_info.get("path", "")
                if not link.endswith(".htm") and not link.endswith(".pdf"):
                    link += ".htm"
                date_str = doc_info.get("publication_start_date", "")
                parsed_date = None
                if date_str:
                    try: parsed_date = parser.parse(date_str)
                    except: pass
                if not parsed_date: continue
                if parsed_date >= start_date:
                    rows.append({"Date": parsed_date, "Title": titulo, "Link": link, "Organismo": "BPI"})
        except Exception as e:
            continue

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=['Link'])
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

# --- SECCIÓN: DISCURSOS ---
@st.cache_data(show_spinner=False)
def load_data_ecb(start_date_str, end_date_str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    rows = []
    try: 
        start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
        end_date = datetime.datetime.strptime(end_date_str, '%d.%m.%Y')
        anios_num = list(range(start_date.year, end_date.year + 1))
    except: 
        anios_num = [2026, 2025, 2024]
        
    for year in anios_num:
        url = f"https://www.ecb.europa.eu/press/key/date/{year}/html/index.en.html"
        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if f'/press/key/date/{year}/html/' in href and href.endswith('.html') and 'index' not in href:
                    link = "https://www.ecb.europa.eu" + href if href.startswith('/') else href
                    titulo_raw = a.get_text(strip=True)
                    if len(titulo_raw) < 5: continue
                    
                    parent = a.find_parent(['dd', 'div', 'li'])
                    if not parent: continue
                    
                    fecha_str = ""
                    dt = parent.find_previous_sibling('dt')
                    if dt:
                        fecha_str = dt.get_text(strip=True)
                    else:
                        prev_div = parent.find_previous_sibling('div')
                        if prev_div and re.search(r'\d{1,2}\s+[A-Za-z]+\s+\d{4}', prev_div.get_text()):
                            fecha_str = prev_div.get_text(strip=True)
                    
                    parsed_date = None
                    if fecha_str:
                        try: parsed_date = parser.parse(fecha_str)
                        except: pass
                    if not parsed_date: continue
                    
                    autor = ""
                    sub = parent.find('div', class_='subtitle')
                    if sub:
                        sub_text = sub.get_text(separator=' ', strip=True)
                        match = re.search(r'\b(?:by|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', sub_text)
                        if match: autor = clean_author_name(match.group(1))
                        else: autor = clean_author_name(sub_text.split(',')[0])
                            
                    final_t = f"{autor}: {titulo_raw}" if autor and autor not in titulo_raw else titulo_raw
                    if not any(r['Link'] == link for r in rows):
                        rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "ECB (Europa)"})
        except: pass
        
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_bis():
    urls = [
        "https://www.bis.org/api/document_lists/cbspeeches.json",
        "https://www.bis.org/api/document_lists/bcbs_speeches.json",
        "https://www.bis.org/api/document_lists/mgmtspeeches.json"
    ]
    headers = {'User-Agent': 'Mozilla/5.0'}
    rows = []
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            for path, speech in data.get("list", {}).items():
                title = html.unescape(speech.get("short_title", ""))
                date_str = speech.get("publication_start_date", "")
                link = "https://www.bis.org" + path + (".htm" if not path.endswith(".htm") else "")
                rows.append({"Date": date_str, "Title": title, "Link": link, "Organismo": "BPI"})
        except: continue
    df = pd.DataFrame(rows).drop_duplicates(subset=['Link']) if rows else pd.DataFrame()
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_bbk(start_date_str, end_date_str):
    base_url = "https://www.bundesbank.de/action/en/730564/bbksearch"
    headers = {'User-Agent': 'Mozilla/5.0'}
    rows, page = [], 0
    while True:
        params = {'sort': 'bbksortdate desc', 'dateFrom': start_date_str, 'dateTo': end_date_str, 'pageNumString': str(page)}
        try: response = requests.get(base_url, headers=headers, params=params, timeout=10)
        except: break 
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='resultlist__item')
        if not items: break 
        for item in items:
            fecha_tag = item.find('span', class_='metadata__date')
            fecha_str = fecha_tag.text.strip() if fecha_tag else ""
            author_tag = item.find('span', class_='metadata__authors')
            author_str = clean_author_name(author_tag.text) if author_tag else ""
            if author_str: author_str = re.sub(r'([a-z])([A-Z])', r'\1 \2', author_str)
            data_div = item.find('div', class_='teasable__data')
            link, titulo = "", ""
            if data_div and data_div.find('a'):
                a_tag = data_div.find('a')
                link = "https://www.bundesbank.de" + a_tag.get('href', '') if a_tag.get('href', '').startswith('/') else a_tag.get('href', '')
                if a_tag.find('span', class_='link__label'): titulo = a_tag.find('span', class_='link__label').text.strip()
            if author_str and author_str not in titulo: titulo = f"{author_str}: {titulo}"
            if fecha_str and titulo: rows.append({"Date": fecha_str, "Title": titulo, "Link": link, "Organismo": "BBk (Alemania)"})
        if len(items) < 10: break
        page += 1
        time.sleep(0.3) 
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], format='%d.%m.%Y', errors='coerce')
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_pboc(start_date_str, end_date_str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    
    rows, page = [], 1
    while True:
        url = "https://www.pbc.gov.cn/en/3688110/3688175/index.html" if page == 1 else f"https://www.pbc.gov.cn/en/3688110/3688175/0180081b-{page}.html"
        try:
            res = requests.get(url, headers=headers, timeout=12)
            res.encoding = 'utf-8' 
            soup = BeautifulSoup(res.text, 'html.parser')
            
            items = soup.find_all('div', class_='ListR')
            if not items: break
            
            items_found = 0
            for item in items:
                date_span = item.find('span', class_='prhhdata')
                a_tag = item.find('a')
                if not date_span or not a_tag: continue
                
                parsed_date = parser.parse(date_span.get_text(strip=True))
                if not parsed_date: continue
                
                titulo_raw = a_tag.get('title', a_tag.get_text(strip=True))
                
                try:
                    titulo_raw = titulo_raw.encode('latin1').decode('utf-8')
                except:
                    pass
                
                diccionario_basura = {
                    'â€™': "'", 'â€œ': '"', 'â€': '"', 
                    'â€“': '-', 'â€”': '--', 'Â': '', 
                    'â€': "'", 'â': "'"
                }
                for malo, bueno in diccionario_basura.items():
                    titulo_raw = titulo_raw.replace(malo, bueno)
                    
                titulo_raw = html.unescape(titulo_raw)
                
                link = "https://www.pbc.gov.cn" + a_tag.get('href', '') if a_tag.get('href', '').startswith('/') else a_tag.get('href', '')
                
                autor = ""
                match = re.search(r'\bby\s+(?:PBOC\s+)?(?:Deputy\s+)?(?:Governor\s+)?(?:and\s+SAFE\s+Administrator\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', titulo_raw)
                if match:
                    autor = clean_author_name(match.group(1))
                    
                final_t = f"{autor}: {titulo_raw}" if autor and autor not in titulo_raw else titulo_raw
                
                if not any(r['Link'] == link for r in rows):
                    rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "PBoC (China)"})
                    items_found += 1
            
            if items_found == 0 or (rows and rows[-1]['Date'] < start_date): break
            page += 1
            time.sleep(0.5) 
        except: break
        
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_fed(anios_num):
    headers = {'User-Agent': 'Mozilla/5.0'}
    rows = []
    for year in anios_num:
        url = f"https://www.federalreserve.gov/newsevents/{year}-speeches.htm"
        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code == 404:
                url = "https://www.federalreserve.gov/newsevents/speeches.htm"
                res = requests.get(url, headers=headers, timeout=12)
            soup = BeautifulSoup(res.text, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                if '/newsevents/speech/' in a_tag['href']:
                    link = "https://www.federalreserve.gov" + a_tag['href'] if a_tag['href'].startswith('/') else a_tag['href']
                    titulo = a_tag.get_text(strip=True)
                    parent = a_tag.find_parent('div', class_='row') or a_tag.parent
                    text = parent.get_text(separator=' | ', strip=True)
                    date_m = re.search(r'(\d{1,2}/\d{1,2}/\d{4}|\w+\s\d{1,2},\s\d{4})', text)
                    if date_m:
                        try:
                            parsed_date = parser.parse(date_m.group(1))
                            if parsed_date.year not in anios_num: continue
                            autor = ""
                            partes = text.split(' | ')
                            for p in partes:
                                p_clean = p.strip()
                                if p_clean and p_clean != titulo and date_m.group(1) not in p_clean and 'Watch Live' not in p_clean:
                                    if any(cargo in p_clean for cargo in ['Chair', 'Governor', 'Vice Chair', 'President']):
                                        autor_raw = re.sub(r'^(?:Statement\s+(?:by|from)\s+)?(?:Federal Reserve\s+)?(?:Former\s+)?(Vice Chair for Supervision|Vice Chair|Chair|Governor|President)\s+', '', p_clean, flags=re.IGNORECASE)
                                        autor = clean_author_name(autor_raw)
                                        break
                            final_t = f"{autor}: {titulo}" if autor and autor not in titulo else titulo
                            rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "Fed (Estados Unidos)"})
                        except: pass
        except: pass
    df = pd.DataFrame(rows).drop_duplicates(subset=['Link']) if rows else pd.DataFrame()
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_bdf(start_date_str, end_date_str):
    base_url = "https://www.banque-france.fr/en/governor-interventions"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    rows, page = [], 0
    while True:
        try:
            response = requests.get(base_url, headers=headers, params={'category[7052]': '7052', 'page': page}, timeout=12)
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_=lambda c: c and 'card' in c)
            if not cards: break
            items_found = 0
            for card in cards:
                a = card.find('a', href=True, class_=lambda c: c and 'text-underline-hover' in c)
                if not a or not a.find('span', class_='title-truncation'): continue
                titulo_raw, link = a.find('span', class_='title-truncation').get_text(strip=True), "https://www.banque-france.fr" + a['href']
                date_s = card.find('small', class_=lambda c: c and 'fw-semibold' in c)
                if not date_s: continue
                fecha_clean = re.sub(r'(\d+)(st|nd|rd|th)\s+of\s+', r'\1 ', date_s.get_text(strip=True))
                parsed_date = parser.parse(fecha_clean)
                autor = ""
                for btn in card.find_all('a', class_='thematic-pill'):
                    if 'Governor' in btn.text:
                        autor = "Deputy Governor" if 'Deputy' in btn.text else "François Villeroy De Galhau"
                        break
                autor = clean_author_name(autor)
                final_t = f"{autor}: {titulo_raw}" if autor and autor not in titulo_raw else titulo_raw
                if not any(r['Link'] == link for r in rows):
                    rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "BdF (Francia)"})
                    items_found += 1
            if items_found == 0 or (rows and rows[-1]['Date'] < start_date): break
            page += 1
            time.sleep(0.3)
        except: break
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_bm(start_date_str, end_date_str):
    base_url = "https://openknowledge.worldbank.org/server/api/discover/search/objects"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    rows, page = [], 0
    while True:
        try:
            res = requests.get(base_url, headers=headers, params={'scope': 'b6a50016-276d-56d3-bbe5-891c8d18db24', 'sort': 'dc.date.issued,DESC', 'page': page, 'size': 20}, timeout=12)
            data = res.json()
            objects = data.get('_embedded', {}).get('searchResult', {}).get('_embedded', {}).get('objects', [])
            if not objects: break
            items_found = 0
            for obj in objects:
                item = obj.get('_embedded', {}).get('indexableObject', {})
                meta = item.get('metadata', {})
                title = meta.get('dc.title', [{'value': ''}])[0].get('value', '')
                date_s = meta.get('dc.date.issued', [{'value': ''}])[0].get('value', '')
                parsed_date = parser.parse(date_s) if date_s else None
                if not parsed_date: continue
                link = meta.get('dc.identifier.uri', [{'value': ''}])[0].get('value', '') or f"https://openknowledge.worldbank.org/entities/publication/{item.get('id', '')}"
                autor = ""
                auth_l = meta.get('dc.contributor.author', [])
                if auth_l:
                    raw = auth_l[0].get('value', '')
                    autor = clean_author_name(f"{raw.split(',')[1].strip()} {raw.split(',')[0].strip()}" if ',' in raw else raw)
                final_t = f"{autor}: {title}" if autor and autor not in title else title
                if not any(r['Link'] == link for r in rows):
                    rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "BM"})
                    items_found += 1
            last_d = rows[-1]['Date'].replace(tzinfo=None) if rows and rows[-1]['Date'].tzinfo else (rows[-1]['Date'] if rows else None)
            if items_found == 0 or (last_d and last_d < start_date): break
            page += 1
            time.sleep(0.3)
        except: break
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_boc(start_date_str, end_date_str):
    base_url = "https://www.bankofcanada.ca/press/speeches/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    rows, page = [], 1
    while True:
        try:
            res = requests.get(base_url, headers=headers, params={'mt_page': page}, timeout=12)
            soup = BeautifulSoup(res.text, 'html.parser')
            articles = soup.find_all('div', class_=lambda c: c and ('mtt-result' in c or 'media' in c))
            if not articles: break
            items_found = 0
            for art in articles:
                h3 = art.find('h3', class_='media-heading')
                if not h3 or not h3.find('a'): continue
                titulo_raw, link = h3.find('a').text.strip(), h3.find('a')['href']
                date_s = art.find('span', class_='media-date')
                parsed_date = parser.parse(date_s.text.strip()) if date_s else None
                if not parsed_date: continue
                autor = clean_author_name(", ".join([x.text.strip() for x in art.find('span', class_='media-authors').find_all('a')])) if art.find('span', class_='media-authors') else ""
                final_t = f"{autor}: {titulo_raw}" if autor and autor not in titulo_raw else titulo_raw
                if not any(r['Link'] == link for r in rows):
                    rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "BoC (Canadá)"})
                    items_found += 1
            if items_found == 0 or (rows and rows[-1]['Date'] < start_date): break
            page += 1
            time.sleep(0.3)
        except: break
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_boj(start_date_str, end_date_str):
    base_url = "https://www.boj.or.jp/en/about/press/index.htm"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    rows = []
    try:
        response = requests.get(base_url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='js-tbl')
        if table:
            for tr in table.find('tbody').find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) < 3: continue
                fecha_str = tds[0].get_text(strip=True).replace('\xa0', ' ')
                parsed_date = parser.parse(fecha_str)
                if parsed_date < start_date: continue
                autor_raw = tds[1].get_text(strip=True)
                autor = clean_author_name(autor_raw.split(',')[0])
                a_tag = tds[2].find('a', href=True)
                if not a_tag: continue
                titulo_raw = a_tag.get_text(strip=True).strip('"')
                link = "https://www.boj.or.jp" + a_tag['href'] if a_tag['href'].startswith('/') else a_tag['href']
                final_t = f"{autor}: {titulo_raw}" if autor and autor not in titulo_raw else titulo_raw
                rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "BoJ (Japón)"})
    except: pass
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_cef(start_date_str, end_date_str):
    base_url = "https://www.fsb.org/press/speeches-and-statements/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try: start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    except: start_date = datetime.datetime(2000, 1, 1)
    rows, page = [], 1
    while True:
        url = f"{base_url}?dps_paged={page}"
        try:
            res = requests.get(url, headers=headers, timeout=12)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_='post-excerpt')
            if not items: break
            items_found = 0
            for item in items:
                title_tag = item.find('div', class_='post-title')
                if not title_tag or not title_tag.find('a'): continue
                a = title_tag.find('a')
                titulo_raw, link = a.get_text(strip=True), a['href']
                
                date_tag = item.find('div', class_='post-date')
                parsed_date = parser.parse(date_tag.get_text(strip=True)) if date_tag else None
                if not parsed_date: continue
                
                autor = ""
                excerpt_tag = item.find('span', class_='media-excerpt')
                if excerpt_tag:
                    excerpt_text = excerpt_tag.get_text(strip=True)
                    match = re.search(r'(?:[Ss]peech|[Rr]emarks|[Aa]rticle|[Vv]ideo)\s+(?:by|provided\s+by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', excerpt_text)
                    if match: 
                        autor = match.group(1)
                
                if not autor and excerpt_tag:
                    match_simple = re.search(r'^([A-Z][a-z]+\s[A-Z][a-z]+)', excerpt_text)
                    if match_simple: autor = match_simple.group(1)

                autor = clean_author_name(autor)
                final_t = f"{autor}: {titulo_raw}" if autor and autor not in titulo_raw else titulo_raw
                
                if not any(r['Link'] == link for r in rows):
                    rows.append({"Date": parsed_date, "Title": final_t, "Link": link, "Organismo": "CEF"})
                    items_found += 1
            
            if items_found == 0 or (rows and rows[-1]['Date'] < start_date): break
            page += 1
            time.sleep(0.3)
        except: break
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

@st.cache_data(show_spinner=False)
def load_data_generic(urls, base_domain, org_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    rows = []
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=12)
            soup = BeautifulSoup(res.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                link = a['href'] if 'http' in a['href'] else base_domain + a['href']
                if base_domain not in link: continue
                title = re.sub(r'\s+', ' ', a.get_text(strip=True))
                if len(title) < 15: continue
                ctx = (a.parent.get_text() + " " + a.parent.parent.get_text()) if a.parent and a.parent.parent else ""
                date_m = re.search(r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})', ctx, re.I)
                if date_m:
                    try:
                        parsed_date = parser.parse(date_m.group(1), fuzzy=True)
                        rows.append({"Date": parsed_date, "Title": title, "Link": link, "Organismo": org_name})
                    except: pass
        except: continue
    df = pd.DataFrame(rows).drop_duplicates(subset=['Link'])
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None: df["Date"] = df["Date"].dt.tz_convert(None)
        df = df.sort_values("Date", ascending=False)
    return df

# ==========================================
# EXPORTACIÓN A WORD
# ==========================================
def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id)
    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')
    
    # Color azul y subrayado
    c = docx.oxml.shared.OxmlElement('w:color'); c.set(docx.oxml.shared.qn('w:val'), '0000EE'); rPr.append(c)
    u = docx.oxml.shared.OxmlElement('w:u'); u.set(docx.oxml.shared.qn('w:val'), 'single'); rPr.append(u)
    
    # Negrita (Bold)
    b = docx.oxml.shared.OxmlElement('w:b'); rPr.append(b)
    
    # Tamaño de letra (28 medios-puntos = tamaño 14)
    for s in ['w:sz', 'w:szCs']:
        sz = docx.oxml.shared.OxmlElement(s); sz.set(docx.oxml.shared.qn('w:val'), '28'); rPr.append(sz)
        
    # Fuente Calibri
    rFonts = docx.oxml.shared.OxmlElement('w:rFonts'); rFonts.set(docx.oxml.shared.qn('w:ascii'), 'Calibri'); rFonts.set(docx.oxml.shared.qn('w:hAnsi'), 'Calibri'); rPr.append(rFonts)
    
    t = docx.oxml.shared.OxmlElement('w:t'); t.text = text; new_run.append(rPr); new_run.append(t); hyperlink.append(new_run); paragraph._p.append(hyperlink)

def generate_word(df, title="Boletín Mensual", subtitle=""):
    doc = Document()
    h = doc.add_heading(title, 0); h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if subtitle:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(subtitle); run.font.name, run.font.size = 'Calibri', Pt(14)
    doc.add_paragraph()
    
    table = doc.add_table(rows=1, cols=len(df.columns)-1)
    table.style = 'Table Grid'
    
    cols = [c for c in df.columns if c != 'Link']
    
    # --- ENCABEZADOS EN CALIBRI 14 NEGRITA ---
    for idx, name in enumerate(cols):
        p = table.rows[0].cells[idx].paragraphs[0]
        run = p.add_run(name)
        run.font.name = 'Calibri'
        run.font.size = Pt(14) 
        run.bold = True
        
    # --- LLENADO DE DATOS ---
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(cols):
            p = cells[i].paragraphs[0]
            if col == 'Nombre de Documento': 
                add_hyperlink(p, str(row[col]), str(row['Link']))
            else:
                run = p.add_run(str(row[col]))
                run.font.name = 'Calibri'
                run.font.size = Pt(14)
                run.bold = True

    # --- FUSIÓN INTELIGENTE (MERGE) ---
    if 'Tipo de Documento' in df.columns and 'Organismo' in df.columns:
        col_tipo = cols.index('Tipo de Documento')
        col_org = cols.index('Organismo')
        
        # 1. Fusión de la columna Organismo
        start_row = 1
        while start_row <= len(df):
            cat_val = df.iloc[start_row - 1]['Tipo de Documento']
            org_val = df.iloc[start_row - 1]['Organismo']
            end_row = start_row
            
            if cat_val == "Discursos":
                table.cell(start_row, col_org).text = "" 
                while end_row < len(df) and df.iloc[end_row]['Tipo de Documento'] == "Discursos":
                    table.cell(end_row + 1, col_org).text = "" 
                    end_row += 1
                
                if end_row > start_row:
                    target_cell = table.cell(start_row, col_org)
                    target_cell.merge(table.cell(end_row, col_org))
                
                start_row = end_row + 1
                continue
                
            while end_row < len(df) and df.iloc[end_row]['Tipo de Documento'] == cat_val and df.iloc[end_row]['Organismo'] == org_val:
                table.cell(end_row + 1, col_org).text = "" 
                end_row += 1
                
            if end_row > start_row:
                target_cell = table.cell(start_row, col_org)
                target_cell.merge(table.cell(end_row, col_org))
                target_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER 
                
            start_row = end_row + 1

        # 2. Fusión de la columna Tipo de Documento
        start_row = 1
        while start_row <= len(df):
            cat_val = df.iloc[start_row - 1]['Tipo de Documento']
            end_row = start_row
            
            while end_row < len(df) and df.iloc[end_row]['Tipo de Documento'] == cat_val:
                table.cell(end_row + 1, col_tipo).text = ""
                end_row += 1
            
            if end_row > start_row:
                target_cell = table.cell(start_row, col_tipo)
                target_cell.merge(table.cell(end_row, col_tipo))
                target_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER 
                
            start_row = end_row + 1
                
    out = BytesIO(); doc.save(out); out.seek(0); return out

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
try: 
    st.sidebar.image("logo_banxico.png", use_container_width=True)
except: 
    st.sidebar.markdown("### 🏦 BANCO DE MÉXICO")

st.sidebar.markdown("---")
st.sidebar.header("Menú de Navegación")
modo_app = st.sidebar.radio("", ["Boletín", "Categorías"], key="menu_principal") 
st.sidebar.markdown("---")

anios_str = ["2026", "2025", "2024", "2023", "2022"]
meses_dict = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

mapeo_discursos = {
    "PBoC (China)": (["https://www.pbc.gov.cn/en/3688110/3688175/index.html"], "https://www.pbc.gov.cn")
}

# --- LISTAS DINÁMICAS DE ORGANISMOS ---
orgs_discursos = ["BBk (Alemania)", "BdF (Francia)", "BM", "BoC (Canadá)", "BoJ (Japón)", "BPI", "CEF", "ECB (Europa)", "Fed (Estados Unidos)", "PBoC (China)"]
orgs_reportes = ["BID", "OCDE", "CEF", "BPI"]
orgs_pub_inst = ["BPI", "CEF"] # <-- ACTUALIZADO 
orgs_investigacion = ["BPI"]

if modo_app == "Boletín":
    st.title("Generador de Boletín Mensual")
    st.markdown("Extrae y unifica documentos de todas las categorías y organismos por mes."); st.markdown("---")
    
    c1, c2 = st.columns(2)
    m_sel = c1.multiselect("Mes(es)", options=list(meses_dict.keys()))
    a_sel = c2.multiselect("Año(s)", options=anios_str, default=["2026"])
    
    if st.button("📄 Generar Boletín Mensual", type="primary"):
        if not m_sel or not a_sel: 
            st.warning("⚠️ Selecciona mes y año.")
        else:
            m_num = [meses_dict[m] for m in m_sel]
            a_num = [int(a) for a in a_sel]
            sd = f"01.{min(m_num):02d}.{min(a_num)}"
            ed = f"{calendar.monthrange(max(a_num), max(m_num))[1]:02d}.{max(m_num):02d}.{max(a_num)}"
            
            all_dfs = []
            prog = st.progress(0)
            txt = st.empty()
            
            # Calculamos el total con todas las categorías
            total_pasos = len(orgs_discursos) + len(orgs_reportes) + len(orgs_pub_inst) + len(orgs_investigacion)
            paso_actual = 0
            
            # 1. BARRIDO DE DISCURSOS
            for org in orgs_discursos:
                txt.text(f"Procesando Discursos: {org}...")
                df = pd.DataFrame()
                try:
                    if org == "BPI": df = load_data_bis()
                    elif org == "ECB (Europa)": df = load_data_ecb(sd, ed)
                    elif org == "BBk (Alemania)": df = load_data_bbk(sd, ed)
                    elif org == "BdE (España)": df = load_data_bde(sd, ed)
                    elif org == "Fed (Estados Unidos)": df = load_data_fed(a_num)
                    elif org == "BdF (Francia)": df = load_data_bdf(sd, ed)
                    elif org == "BM": df = load_data_bm(sd, ed)
                    elif org == "BoC (Canadá)": df = load_data_boc(sd, ed)
                    elif org == "BoJ (Japón)": df = load_data_boj(sd, ed)
                    elif org == "CEF": df = load_data_cef(sd, ed)
                    elif org == "PBoC (China)": df = load_data_pboc(sd, ed)
                except Exception as e: pass 
                
                if not df.empty:
                    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                    df_f = df[(df["Date"].dt.year.isin(a_num)) & (df["Date"].dt.month.isin(m_num))].copy()
                    if not df_f.empty: 
                        df_f['Organismo'] = org
                        df_f['Categoría'] = "Discursos"
                        all_dfs.append(df_f)
                paso_actual += 1; prog.progress(paso_actual / total_pasos)

            # 2. BARRIDO DE REPORTES
            for org in orgs_reportes:
                txt.text(f"Procesando Reportes: {org}...")
                df = pd.DataFrame()
                try:
                    if org == "BID": df = load_reportes_bid(sd, ed)
                    elif org == "OCDE": df = load_reportes_ocde(sd, ed)
                    elif org == "CEF": df = load_reportes_cef(sd, ed)
                    elif org == "BPI": df = load_reportes_bpi(sd, ed)
                except Exception as e: pass 
                
                if not df.empty:
                    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                    df_f = df[(df["Date"].dt.year.isin(a_num)) & (df["Date"].dt.month.isin(m_num))].copy()
                    if not df_f.empty: 
                        df_f['Organismo'] = org
                        df_f['Categoría'] = "Reportes"
                        all_dfs.append(df_f)
                paso_actual += 1; prog.progress(paso_actual / total_pasos)
                
            # 3. BARRIDO DE PUBLICACIONES INSTITUCIONALES 
            for org in orgs_pub_inst:
                txt.text(f"Procesando Pub. Institucionales: {org}...")
                df = pd.DataFrame()
                try:
                    if org == "BPI": df = load_pub_inst_bpi(sd, ed)
                except Exception as e: pass 
                
                if not df.empty:
                    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                    df_f = df[(df["Date"].dt.year.isin(a_num)) & (df["Date"].dt.month.isin(m_num))].copy()
                    if not df_f.empty: 
                        df_f['Organismo'] = org
                        df_f['Categoría'] = "Publicaciones Institucionales"
                        all_dfs.append(df_f)
                paso_actual += 1; prog.progress(paso_actual / total_pasos)

            # 4. BARRIDO DE INVESTIGACIÓN
            for org in orgs_investigacion:
                txt.text(f"Procesando Investigación: {org}...")
                df = pd.DataFrame()
                try:
                    if org == "BPI": df = load_investigacion_bpi(sd, ed)
                except Exception as e: pass 
                
                if not df.empty:
                    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                    df_f = df[(df["Date"].dt.year.isin(a_num)) & (df["Date"].dt.month.isin(m_num))].copy()
                    if not df_f.empty: 
                        df_f['Organismo'] = org
                        df_f['Categoría'] = "Investigación"
                        all_dfs.append(df_f)
                paso_actual += 1; prog.progress(paso_actual / total_pasos)
            
            txt.empty()
            prog.empty()
            
            # --- CONSOLIDACIÓN FINAL ---
            if all_dfs:
                f_df = pd.concat(all_dfs, ignore_index=True)
                
                # 1. SEPARAR Y ORDENAR CON REGLAS Y JERARQUÍA ESTRICTA
                df_rep = f_df[f_df['Categoría'] == "Reportes"].copy()
                df_pub = f_df[f_df['Categoría'] == "Publicaciones Institucionales"].copy()
                df_inv = f_df[f_df['Categoría'] == "Investigación"].copy()
                df_disc = f_df[f_df['Categoría'] == "Discursos"].copy()
                
                # Ordenamiento específico
                if not df_rep.empty: df_rep = df_rep.sort_values(by=["Organismo", "Title"], ascending=[True, True])
                if not df_pub.empty: df_pub = df_pub.sort_values(by=["Organismo", "Title"], ascending=[True, True])
                if not df_inv.empty: df_inv = df_inv.sort_values(by=["Organismo", "Title"], ascending=[True, True])
                if not df_disc.empty: df_disc = df_disc.sort_values(by=["Title"], ascending=[True]) # Sin agrupar por organismo
                
                # Unimos respetando tu jerarquía exacta
                f_df = pd.concat([df_rep, df_pub, df_inv, df_disc], ignore_index=True)
                
                # 2. COLUMNAS: Dejamos las 3 solicitadas + Link
                f_df = f_df[['Categoría', 'Organismo', 'Title', 'Link']]
                f_df = f_df.rename(columns={"Categoría": "Tipo de Documento", "Title": "Nombre de Documento"})
                
                st.success(f"Se consolidaron **{len(f_df)}** documentos en total.")
                word = generate_word(f_df, subtitle=", ".join(m_sel) + " " + ", ".join(a_sel))
                st.download_button("📄 Descargar Boletín", word, f"Boletin_{'_'.join(m_sel)}.docx")
                
                disp = f_df.copy()
                disp["Nombre de Documento"] = disp.apply(lambda x: f"[{x['Nombre de Documento']}]({x['Link']})", axis=1)
                st.markdown(disp[["Tipo de Documento", "Organismo", "Nombre de Documento"]].to_markdown(index=False), unsafe_allow_html=True)
            else: 
                st.warning("No se encontraron documentos para los criterios seleccionados.")

elif modo_app == "Categorías":
    st.title("Documentos de Organismos Internacionales")
    tipo_doc = st.sidebar.selectbox("Tipo de Documento", ["Discursos", "Reportes", "Investigación", "Publicaciones Institucionales"])
    
    # Construcción segura de las listas de interfaz
    if tipo_doc == "Discursos":
        orgs_list = ["Todos"] + sorted(orgs_discursos)
    elif tipo_doc == "Reportes":
        orgs_list = ["Todos"] + sorted(orgs_reportes)
    elif tipo_doc == "Investigación":
        orgs_list = ["Todos"] + sorted(orgs_investigacion)
    elif tipo_doc == "Publicaciones Institucionales":
        orgs_list = ["Todos"] + sorted(orgs_pub_inst)
    else:
        orgs_list = ["Todos"] + sorted(list(set(orgs_discursos + orgs_reportes + orgs_investigacion + orgs_pub_inst)))
        
    organismo_seleccionado = st.sidebar.selectbox("Organismo", orgs_list)
    
    c1, c2 = st.columns(2)
    m_sel = c1.multiselect("Mes(es)", options=list(meses_dict.keys()))
    a_sel = c2.multiselect("Año(s)", options=anios_str, default=["2026"])
    
    if st.button("🔍 Buscar", type="primary"):
        if not m_sel or not a_sel:
            st.warning("⚠️ Selecciona mes y año.")
        else:
            m_num = [meses_dict[m] for m in m_sel]
            a_num = [int(a) for a in a_sel]
            sd = f"01.{min(m_num):02d}.{min(a_num)}"
            ed = f"{calendar.monthrange(max(a_num), max(m_num))[1]:02d}.{max(m_num):02d}.{max(a_num)}"
            
            target_orgs = orgs_list[1:] if organismo_seleccionado == "Todos" else [organismo_seleccionado]
            dfs_comb = []
            progreso = st.progress(0)
            txt = st.empty()
            
            for i, o in enumerate(target_orgs):
                txt.text(f"Extrayendo: {o}...")
                df = pd.DataFrame()
                try:
                    if tipo_doc == "Discursos":
                        if o == "BPI": df = load_data_bis()
                        elif o == "ECB (Europa)": df = load_data_ecb(sd, ed)
                        elif o == "BBk (Alemania)": df = load_data_bbk(sd, ed)
                        elif o == "BdE (España)": df = load_data_bde(sd, ed)
                        elif o == "Fed (Estados Unidos)": df = load_data_fed(a_num)
                        elif o == "BdF (Francia)": df = load_data_bdf(sd, ed)
                        elif o == "BM": df = load_data_bm(sd, ed)
                        elif o == "BoC (Canadá)": df = load_data_boc(sd, ed)
                        elif o == "BoJ (Japón)": df = load_data_boj(sd, ed)
                        elif o == "CEF": df = load_data_cef(sd, ed)
                        elif o == "PBoC (China)": df = load_data_pboc(sd, ed)
                    
                    elif tipo_doc == "Reportes":
                        if o == "BID": df = load_reportes_bid(sd, ed)
                        elif o == "OCDE": df = load_reportes_ocde(sd, ed)
                        elif o == "CEF": df = load_reportes_cef(sd, ed)
                        elif o == "BPI": df = load_reportes_bpi(sd, ed) 
                        
                    elif tipo_doc == "Investigación":
                        if o == "BPI": df = load_investigacion_bpi(sd, ed)
                        
                    elif tipo_doc == "Publicaciones Institucionales":
                        if o == "BPI": df = load_pub_inst_bpi(sd, ed)
                        elif o == "CEF": df = load_pub_inst_cef(sd, ed) # <-- LÍNEA CORREGIDA
                        
                except Exception as e:
                    pass
                
                if not df.empty:
                    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                    df_f = df[(df["Date"].dt.year.isin(a_num)) & (df["Date"].dt.month.isin(m_num))].copy()
                    if not df_f.empty: 
                        df_f['Organismo'] = o
                        dfs_comb.append(df_f)
                progreso.progress((i+1)/len(target_orgs))
            
            txt.empty()
            progreso.empty()
            
            if dfs_comb:
                f_df = pd.concat(dfs_comb, ignore_index=True)
                
                # ADAPTAMOS LA ESTRUCTURA PARA QUE EL FORMATO SEA IDÉNTICO AL BOLETÍN
                f_df['Categoría'] = tipo_doc
                if tipo_doc == "Discursos":
                    f_df = f_df.sort_values(by=["Title"], ascending=[True])
                else:
                    f_df = f_df.sort_values(by=["Organismo", "Title"], ascending=[True, True])
                    
                f_df = f_df[['Categoría', 'Organismo', 'Title', 'Link']]
                f_df = f_df.rename(columns={"Categoría": "Tipo de Documento", "Title": "Nombre de Documento"})
                
                st.success(f"Se encontraron **{len(f_df)}** documentos.")
                word = generate_word(f_df, title=f"Explorador - {tipo_doc}")
                st.download_button("📄 Descargar en Word", word, "Explorador.docx")
                
                disp = f_df.copy()
                disp["Nombre de Documento"] = disp.apply(lambda x: f"[{x['Nombre de Documento']}]({x['Link']})", axis=1)
                
                # Pantalla: mostramos u ocultamos la columna Organismo dependiendo del filtro
                cols_pantalla = ["Tipo de Documento", "Organismo", "Nombre de Documento"] if organismo_seleccionado == "Todos" else ["Tipo de Documento", "Nombre de Documento"]
                st.markdown(disp[cols_pantalla].to_markdown(index=False), unsafe_allow_html=True)
            else: 
                st.warning("No se encontraron documentos para las fechas seleccionadas.")