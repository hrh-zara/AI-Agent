#!/usr/bin/env python3
"""
Enhanced Web Interface for English-Hausa Translator
Save this as: web_app/app.py
"""

import streamlit as st
import requests
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="English-Hausa Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .translation-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .stats-box {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .example-box {
        background-color: #fff9e6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffa500;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'translation_history' not in st.session_state:
    st.session_state.translation_history = []
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

# Header
st.markdown('<div class="main-header">🌍 English ↔ Hausa Translator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Translation for NGOs in Northern Nigeria</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API connection
    api_url = st.text_input("API URL", value=st.session_state.api_url)
    st.session_state.api_url = api_url
    
    # Check API status
    try:
        response = requests.get(f"{api_url}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Not Running")
        st.info("Start API with: `python api/main.py`")
    
    st.divider()
    
    # Translation direction
    st.header("🔄 Translation Direction")
    direction = st.radio(
        "Select direction:",
        ["English → Hausa", "Hausa → English"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Statistics
    st.header("📊 Session Stats")
    st.metric("Translations", len(st.session_state.translation_history))
    
    if st.session_state.translation_history:
        avg_time = sum(h['time'] for h in st.session_state.translation_history) / len(st.session_state.translation_history)
        st.metric("Avg. Time", f"{avg_time:.2f}s")
    
    st.divider()
    
    # Clear history
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.translation_history = []
        st.rerun()

# Main content area
tab1, tab2, tab3 = st.tabs(["🔤 Translate", "📚 Examples", "📊 History"])

# TAB 1: Translation
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Text")
        
        # Determine source and target languages
        if direction == "English → Hausa":
            source_lang = "en"
            target_lang = "ha"
            input_label = "Enter English text:"
            placeholder = "Type or paste English text here..."
        else:
            source_lang = "ha"
            target_lang = "en"
            input_label = "Enter Hausa text:"
            placeholder = "Type or paste Hausa text here..."
        
        # Input text area
        input_text = st.text_area(
            input_label,
            height=200,
            placeholder=placeholder,
            key="input_text"
        )
        
        # Character count
        char_count = len(input_text)
        st.caption(f"Characters: {char_count}/1000")
        
        # Translate button
        translate_btn = st.button("🚀 Translate", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("✨ Translation")
        
        # Translation output area
        output_placeholder = st.empty()
        
        # Display previous translation if exists
        if 'last_translation' in st.session_state:
            output_placeholder.markdown(
                f'<div class="translation-box">{st.session_state.last_translation}</div>',
                unsafe_allow_html=True
            )
        else:
            output_placeholder.info("Translation will appear here...")
    
    # Handle translation
    if translate_btn:
        if not input_text.strip():
            st.error("⚠️ Please enter some text to translate")
        else:
            with st.spinner("🔄 Translating..."):
                try:
                    start_time = time.time()
                    
                    # Make API request
                    response = requests.post(
                        f"{st.session_state.api_url}/translate",
                        json={
                            "text": input_text,
                            "source_lang": source_lang,
                            "target_lang": target_lang
                        },
                        timeout=30
                    )
                    
                    end_time = time.time()
                    translation_time = end_time - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        # API returns the translated text under the key 'translation'.
                        # For backward compatibility also accept 'translated_text'.
                        translated_text = result.get('translation') or result.get('translated_text') or 'No translation received'
                        
                        # Store translation
                        st.session_state.last_translation = translated_text
                        
                        # Add to history
                        st.session_state.translation_history.append({
                            'input': input_text,
                            'output': translated_text,
                            'direction': direction,
                            'time': translation_time,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        # Display result
                        output_placeholder.markdown(
                            f'<div class="translation-box">{translated_text}</div>',
                            unsafe_allow_html=True
                        )
                        
                        st.success(f"✅ Translated in {translation_time:.2f}s")
                        
                        # Copy button
                        st.code(translated_text, language=None)
                        
                    else:
                        st.error(f"❌ Translation failed: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure it's running!")
                    st.info("Start the API with: `python api/main.py`")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# TAB 2: Examples
with tab2:
    st.subheader("📚 Common NGO Phrases")
    st.write("Click any example to try it:")
    
    examples = {
        "Greetings & Basic": [
            ("Hello, how are you?", "Sannu, yaya kuke?"),
            ("Good morning", "Barka da safe"),
            ("Good afternoon", "Barka da yamma"),
            ("Thank you very much", "Na gode sosai"),
            ("You're welcome", "Ba komai"),
        ],
        "Healthcare": [
            ("We need clean water", "Muna bukatan ruwa mai tsabta"),
            ("The clinic is open today", "Asibitin yana bude yau"),
            ("Please take your medicine", "Don Allah sha maganinka"),
            ("Do you have any allergies?", "Kuna da wani rashin lafiya?"),
            ("Wash your hands regularly", "Ku wanke hannuwanku akai-akai"),
        ],
        "Education": [
            ("School starts tomorrow", "Makaranta tana farawa gobe"),
            ("Please do your homework", "Don Allah yi aikin gida"),
            ("The teacher will help you", "Malami zai taimake ka"),
            ("Bring your books to class", "Kawo littattafanka zuwa aji"),
        ],
        "Emergency": [
            ("We need help immediately", "Muna bukatan taimako nan take"),
            ("Is anyone injured?", "Akwai wanda ya ji rauni?"),
            ("Call for medical assistance", "Kira don taimakon lafiya"),
            ("Stay calm and wait here", "Ku natsu ku jira a nan"),
        ]
    }
    
    # Helper to set the input text from examples.
    def _set_input_text(text: str) -> None:
        st.session_state['input_text'] = text

    for category, phrases in examples.items():
        with st.expander(f"📂 {category}", expanded=True):
            for eng, hau in phrases:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"🇬🇧 {eng}")
                with col2:
                    st.write(f"🇳🇬 {hau}")
                with col3:
                    # Use on_click callback to set session state before widgets are rendered
                    st.button("Try", key=f"example_{eng[:20]}", on_click=_set_input_text, args=(eng,))

# TAB 3: History
with tab3:
    st.subheader("📊 Translation History")
    
    if not st.session_state.translation_history:
        st.info("No translations yet. Start translating to see your history!")
    else:
        # Display history in reverse order (newest first)
        for idx, item in enumerate(reversed(st.session_state.translation_history)):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{item['direction']}** • {item['timestamp']}")
                with col2:
                    st.caption(f"⏱️ {item['time']:.2f}s")
                
                st.markdown(f"**Input:** {item['input']}")
                st.markdown(f"**Output:** {item['output']}")
                st.divider()

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            Built with ❤️ for NGOs in Northern Nigeria<br>
            Powered by AI • mT5 Translation Model
        </div>
    """, unsafe_allow_html=True)