# imf_data.py - Datos extraídos del FMI
import datetime
import pandas as pd

def get_fandd_march2026():
    """Retorna los artículos de F&D de Marzo 2026"""
    
    rows = [
        # Debt Section
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Debt: High Debt, Hard Choices", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/high-debt-hard-choices-era-dabla-norris",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Debt: The New Face of African Debt", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/the-new-face-of-african-debt-amadou-sy",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Debt: The Debt-Inequality Cycle", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/the-debt-inequality-cycle-atif-mian",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Debt: Safeguarding the Treasury Market", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/safeguarding-the-treasury-market-jeremy-stein",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Debt: Policy Coordination for Fractured Times", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/policy-coordination-for-fractured-times-giancarlo-corsetti",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Debt: Can Advanced Economies Avoid Debt Distress?", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/stabilizing-debt-in-advanced-economies-zsolt-darvas",
         "Organismo": "FMI"},
        
        # Editor's Letter
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Editor's Letter: Testing Debt Limits", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/editor-letter-testing-debt-limits",
         "Organismo": "FMI"},
        
        # Point of View
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Point of View: Worlds Apart", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/point-of-view-worlds-apart-alan-blinder",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Point of View: AI Can Lift Global Growth", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/point-of-view-ai-can-lift-global-growth-marcello-estevao",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Point of View: America's Perilous Fiscal Path", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/point-of-view-americas-perilous-fiscal-path-alan-auerbach",
         "Organismo": "FMI"},
        
        # Also in this Issue
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Also in this Issue: Debt Reduction Lessons from Jamaica", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/debt-reduction-lessons-from-jamaica",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Also in this Issue: Taxing Harmful Habits", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/taxing-harmful-habits-christoph-rosenberg",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Also in this Issue: Digital Infrastructure", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/digital-infrastructure-diane-coyle",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Also in this Issue: Old Laws for New Machines", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/old-laws-for-new-machines-biagio-bossone",
         "Organismo": "FMI"},
        
        # In the Trenches
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "In the Trenches: The Transformative Central Banker", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/in-the-trenches-the-transformative-central-banker",
         "Organismo": "FMI"},
        
        # Back to Basics
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Back to Basics: The Art of Taxation", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/back-to-basics-the-art-taxation-katherine-baer",
         "Organismo": "FMI"},
        
        # Picture This
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Picture This: The Race for AI-Ready Workers", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/picture-this-the-race-for-ai-ready-workers",
         "Organismo": "FMI"},
        
        # People in Economics
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "People in Economics: Myrto Kalouptsidi - A Maritime Mind", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/people-in-economics-a-maritime-mind-jeff-kearns",
         "Organismo": "FMI"},
        
        # Currency Notes
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Currency Notes: Bhutan's Next Ngultrum", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/currency-notes-bhutans-next-ngultrum-jeff-kearns",
         "Organismo": "FMI"},
        
        # Book Reviews
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Book Review: How China Builds", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/book-review-how-china-builds-melanie-sisson",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Book Review: A Chronicle of Currencies", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/book-review-a-chronicle-of-currencies-catherine-schenk",
         "Organismo": "FMI"},
        
        {"Date": datetime.datetime(2026, 3, 1), 
         "Title": "Book Review: Human Stories behind an Era-Defining Crisis", 
         "Link": "https://www.imf.org/en/publications/fandd/issues/2026/03/book-review-human-stories-behind-a-era-defining-crisis-prakash-loungani",
         "Organismo": "FMI"},
    ]
    
    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"])
    return df