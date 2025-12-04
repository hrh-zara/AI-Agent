#!/usr/bin/env python3
"""
Easy Data Entry Tool for Translation Pairs
Save as: data_entry_tool.py

Run with: streamlit run data_entry_tool.py
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
import os

# Page config
st.set_page_config(
    page_title="Translation Data Entry",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'translations' not in st.session_state:
    st.session_state.translations = []
if 'current_category' not in st.session_state:
    st.session_state.current_category = "general"

# Title
st.title("📝 Translation Data Entry Tool")
st.markdown("Create high-quality English-Hausa translation pairs")

# Sidebar
with st.sidebar:
    st.header("📊 Current Session")
    st.metric("Total Entries", len(st.session_state.translations))
    
    st.divider()
    
    st.header("💾 Save Options")
    filename = st.text_input("Filename", value="new_translations.json")
    
    if st.button("💾 Save to File", type="primary", use_container_width=True):
        if st.session_state.translations:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            filepath = os.path.join('data', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.translations, f, 
                         ensure_ascii=False, indent=2)
            
            st.success(f"✅ Saved {len(st.session_state.translations)} translations!")
            st.info(f"File: {filepath}")
        else:
            st.warning("No translations to save!")
    
    st.divider()
    
    st.header("📋 Load Existing")
    if st.button("Load from File", use_container_width=True):
        try:
            filepath = os.path.join('data', filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                st.session_state.translations.extend(loaded)
                st.success(f"Loaded {len(loaded)} translations!")
        except FileNotFoundError:
            st.error("File not found!")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.translations = []
        st.rerun()

# Main content
tab1, tab2, tab3 = st.tabs(["➕ Add New", "📋 View All", "📚 Quick Templates"])

# TAB 1: Add New Translation
with tab1:
    st.subheader("Add New Translation Pair")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🇬🇧 English")
        english_input = st.text_area(
            "English text",
            height=100,
            placeholder="Enter English phrase...",
            label_visibility="collapsed",
            key="english_input"
        )
    
    with col2:
        st.markdown("### 🇳🇬 Hausa")
        hausa_input = st.text_area(
            "Hausa text",
            height=100,
            placeholder="Enter Hausa translation...",
            label_visibility="collapsed",
            key="hausa_input"
        )
    
    # Category selection
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        categories = [
            "general", "greeting", "healthcare", "education", 
            "emergency", "agriculture", "finance", "legal"
        ]
        category = st.selectbox("Category", categories)
    
    with col2:
        notes = st.text_input("Notes (optional)", placeholder="Context or usage notes...")
    
    with col3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        add_button = st.button("➕ Add", type="primary", use_container_width=True)
    
    if add_button:
        if english_input.strip() and hausa_input.strip():
            new_translation = {
                "english": english_input.strip(),
                "hausa": hausa_input.strip(),
                "category": category,
            }
            
            if notes.strip():
                new_translation["notes"] = notes.strip()
            
            st.session_state.translations.append(new_translation)
            st.success("✅ Translation added!")
            
            # Clear inputs
            st.rerun()
        else:
            st.error("⚠️ Please fill both English and Hausa fields")

# TAB 2: View All Translations
with tab2:
    st.subheader("All Translation Pairs")
    
    if not st.session_state.translations:
        st.info("No translations yet. Add some in the 'Add New' tab!")
    else:
        # Convert to DataFrame for display
        df = pd.DataFrame(st.session_state.translations)
        
        # Add filters
        col1, col2 = st.columns([1, 3])
        with col1:
            filter_category = st.selectbox(
                "Filter by category",
                ["All"] + list(df['category'].unique())
            )
        
        # Apply filter
        if filter_category != "All":
            df_filtered = df[df['category'] == filter_category]
        else:
            df_filtered = df
        
        st.write(f"Showing {len(df_filtered)} of {len(df)} translations")
        
        # Display translations
        for idx, row in df_filtered.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 3, 1])
                
                with col1:
                    st.markdown(f"**🇬🇧** {row['english']}")
                
                with col2:
                    st.markdown(f"**🇳🇬** {row['hausa']}")
                
                with col3:
                    st.caption(row['category'])
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.translations.pop(idx)
                        st.rerun()
                
                if 'notes' in row and row['notes']:
                    st.caption(f"📝 {row['notes']}")
                
                st.divider()

# TAB 3: Quick Templates
with tab3:
    st.subheader("Quick Translation Templates")
    st.write("Click 'Add All' to bulk-add common phrases")
    
    templates = {
        "Basic Greetings": [
            ("Hello", "Sannu"),
            ("Good morning", "Barka da safe"),
            ("Good afternoon", "Barka da yamma"),
            ("Good evening", "Barka da yamma"),
            ("Good night", "Barka da dare"),
            ("How are you?", "Yaya kuke?"),
            ("I am fine", "Lafiya lau"),
            ("Thank you", "Na gode"),
            ("You're welcome", "Ba komai"),
            ("Goodbye", "Sai anjima"),
        ],
        "Healthcare Basics": [
            ("I need help", "Ina bukatan taimako"),
            ("Where is the clinic?", "Ina asibitin?"),
            ("I am sick", "Ina rashin lafiya"),
            ("Take this medicine", "Sha wannan magani"),
            ("Drink water", "Sha ruwa"),
            ("Rest well", "Huta sosai"),
            ("Come back tomorrow", "Komo gobe"),
            ("Do you have pain?", "Kuna da ciwo?"),
        ],
        "Education": [
            ("Go to school", "Tafi makaranta"),
            ("Read your book", "Karanta littafinka"),
            ("Write your name", "Rubuta sunanka"),
            ("Listen carefully", "Ku saurara sosai"),
            ("Do your homework", "Yi aikin gida"),
            ("The teacher is here", "Malami yana nan"),
            ("Class starts now", "Aji ya fara yanzu"),
        ],
        "Emergency": [
            ("Help!", "Taimako!"),
            ("Call a doctor", "Kira likita"),
            ("This is urgent", "Wannan na gaggawa ne"),
            ("Stay calm", "Ku natsu"),
            ("Are you okay?", "Kuna lafiya?"),
            ("Wait here", "Ku jira a nan"),
        ]
    }
    
    for category, phrases in templates.items():
        with st.expander(f"📂 {category} ({len(phrases)} phrases)"):
            # Show preview
            for eng, hau in phrases[:3]:
                st.write(f"• {eng} → {hau}")
            
            if len(phrases) > 3:
                st.caption(f"... and {len(phrases)-3} more")
            
            if st.button(f"➕ Add All {category}", key=f"add_{category}"):
                for eng, hau in phrases:
                    # Check if not already exists
                    exists = any(
                        t['english'] == eng 
                        for t in st.session_state.translations
                    )
                    
                    if not exists:
                        st.session_state.translations.append({
                            "english": eng,
                            "hausa": hau,
                            "category": category.lower().replace(" ", "_")
                        })
                
                st.success(f"✅ Added {len(phrases)} translations!")
                st.rerun()

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #666;">
        💡 <strong>Tips:</strong> 
        • Add translations one at a time or use templates
        • Save regularly to avoid losing work
        • Use clear, natural language
        • Verify translations with native speakers
    </div>
""", unsafe_allow_html=True)