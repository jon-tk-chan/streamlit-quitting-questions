import streamlit as st
import pandas as pd
import os
import random
import csv
import json
from io import StringIO

# Set page config
st.set_page_config(
    page_title="Should we quit - Question Cards",
    page_icon="❓",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#2e5e40"  # Forest green default
if 'text_color' not in st.session_state:
    st.session_state.text_color = "#f5f5dc"  # Light beige default
if 'accent_color' not in st.session_state:
    st.session_state.accent_color = "#c62828"  # Red default
if 'df' not in st.session_state:
    # Default path to the CSV file
    default_csv_path = os.path.join('data', 'quitting_questions.csv')
    
    # Check if file exists and load it
    if os.path.exists(default_csv_path):
        try:
            st.session_state.df = pd.read_csv(default_csv_path)
            # Fix category 'Self' to 'selfWorth' for consistency
            st.session_state.df['Category'] = st.session_state.df['Category'].replace('Self', 'selfWorth')
        except Exception as e:
            st.session_state.df = pd.DataFrame(columns=['title', 'main_question', 'Category'])
    else:
        st.session_state.df = pd.DataFrame(columns=['title', 'main_question', 'Category'])

# Function to adjust color brightness (for secondary background color)
def adjust_color_brightness(hex_color, factor):
    # Convert hex to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Adjust brightness
    new_rgb = tuple(max(0, min(255, int(c * (1 + factor)))) for c in rgb)
    
    # Convert back to hex
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

# Function to apply custom CSS based on session state colors
def apply_custom_css():
    # Create CSS with dynamic colors
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {st.session_state.bg_color};
            color: {st.session_state.text_color};
        }}
        .stButton>button {{
            color: {st.session_state.text_color};
            border-color: {st.session_state.text_color};
        }}
        /* Style for primary buttons (uses accent color) */
        .stButton>button[data-baseweb="button"][kind="primary"] {{
            background-color: {st.session_state.accent_color};
            color: {st.session_state.text_color};
        }}
        .stButton>button[data-baseweb="button"]:hover {{
            background-color: {st.session_state.text_color};
            color: {st.session_state.bg_color};
        }}
        .css-1adrfps {{  /* Card container */
            background-color: {st.session_state.bg_color};
            border-color: {st.session_state.text_color};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {st.session_state.text_color};
        }}
        
        /* Question card hover animations */
        .question-card {{
            transition: all 0.3s ease;
            border: 1px solid {st.session_state.text_color};
            border-radius: 10px;
            padding: 20px;
            background-color: {st.session_state.bg_color};
        }}
        
        .question-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            border-color: {st.session_state.accent_color};
        }}
        
        /* History card animations (smaller effect) */
        .history-card {{
            transition: all 0.2s ease;
            border: 1px solid {st.session_state.text_color};
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            background-color: {st.session_state.bg_color};
        }}
        
        .history-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 10px rgba(0,0,0,0.1);
            border-color: {st.session_state.accent_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to get a random question based on the selected category
def get_random_question(category=None):
    df = st.session_state.df
    
    if df.empty:
        return {"title": "No Questions Available", "main_question": "Please add questions through the Data Upload tab", "Category": "None"}
    
    # Filter by category if specified
    if category and category != "All Categories" and category in df['Category'].unique():
        filtered_df = df[df['Category'] == category]
        if filtered_df.empty:
            return {"title": "No Questions Available", "main_question": f"No questions found in the '{category}' category", "Category": category}
        question = filtered_df.sample(1).iloc[0].to_dict()
    else:
        question = df.sample(1).iloc[0].to_dict()
    
    return question

# Function to update the current question and add to history
def next_card():
    # Get a random question based on selected category
    question = get_random_question(st.session_state.selected_category)
    
    # Update session state
    if st.session_state.current_question:
        st.session_state.history.insert(0, st.session_state.current_question)
    st.session_state.current_question = question

# Function to handle category selection
def select_category(category):
    st.session_state.selected_category = category
    # Optionally get a new card with the selected category
    # next_card()

# Apply custom CSS before creating UI elements
apply_custom_css()

# Main app tabs
tab1, tab2, tab3 = st.tabs(["Questions", "Data Upload", "Settings"])

# Settings tab
with tab3:
    st.markdown(f"<h2 style='color: {st.session_state.text_color};'>App Settings</h2>", unsafe_allow_html=True)
    
    # Color settings
    st.markdown(f"<h3 style='color: {st.session_state.text_color};'>Color Settings</h3>", unsafe_allow_html=True)
    
    # Background color picker
    bg_color = st.color_picker("Background Color", value=st.session_state.bg_color, key="bg_color_picker")
    
    # Text color picker
    text_color = st.color_picker("Text Color", value=st.session_state.text_color, key="text_color_picker")
    
    # Accent color picker for buttons
    accent_color = st.color_picker("Button Accent Color", value=st.session_state.accent_color, key="accent_color_picker")
    
    # Apply button
    if st.button("Apply Colors", key="apply_colors"):
        st.session_state.bg_color = bg_color
        st.session_state.text_color = text_color
        st.session_state.accent_color = accent_color
        
        # Save colors to config
        try:
            # Ensure .streamlit directory exists
            os.makedirs('.streamlit', exist_ok=True)
            
            # Update config.toml file
            with open('.streamlit/config.toml', 'w') as f:
                f.write('[server]\n')
                f.write('headless = true\n')
                f.write('address = "0.0.0.0"\n')
                f.write('port = 5000\n\n')
                f.write('[theme]\n')
                f.write(f'primaryColor = "{accent_color}"\n')
                f.write(f'backgroundColor = "{bg_color}"\n')
                f.write(f'secondaryBackgroundColor = "{adjust_color_brightness(bg_color, -0.2)}"\n')
                f.write(f'textColor = "{text_color}"\n')
            
            st.success("Colors applied successfully! Some changes may require a page refresh.")
        except Exception as e:
            st.error(f"Error saving config: {e}")
        
        st.rerun()

with tab1:
    # Get all unique categories
    all_categories = []
    if not st.session_state.df.empty and 'Category' in st.session_state.df.columns:
        all_categories = sorted(st.session_state.df['Category'].unique().tolist())

    # Create three columns for layout
    col1, col2, col3 = st.columns([1, 2, 1])

    # Left Column - Categories
    with col1:
        st.markdown(f"<h2 style='text-align: center; color: {st.session_state.text_color};'>CATEGORIES</h2>", unsafe_allow_html=True)
        
        # Create category buttons
        if all_categories:
            for category in all_categories:
                # Check if this is the selected category
                is_selected = st.session_state.selected_category == category
                
                # Use different button styles based on selection state
                if is_selected:
                    button_type = "primary"
                else:
                    button_type = "secondary"
                
                # Create the button for this category
                if st.button(
                    category.upper(), 
                    key=f"btn_{category}", 
                    use_container_width=True,
                    type=button_type
                ):
                    select_category(category)
                    st.rerun()
        else:
            st.write("No categories available. Please upload data.")

    # Middle Column - Current Question
    with col2:
        st.markdown(f"<h2 style='text-align: center; color: {st.session_state.text_color};'>Should We Quit? Flashcards</h2>", unsafe_allow_html=True)
        
        # Initialize current question if not set
        if not st.session_state.current_question:
            next_card()
        
        # Display current question
        if st.session_state.current_question:
            with st.container(border=True):
                st.markdown(
                    f"<div class='question-card' style='padding: 20px; text-align: center;'>"
                    f"<h3 style='color: {st.session_state.text_color};'>{st.session_state.current_question['main_question']}</h3>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        
        # Next Card button
        if st.button("NEXT CARD", key="next_card", use_container_width=True, type="primary"):
            next_card()
            st.rerun()
            
        # Add footnote with attribution
        st.markdown("""
        <div style="margin-top: 40px; text-align: center; font-size: 0.8em; opacity: 0.8;">
            Inspired by <a href="https://munjoonteo.github.io/wnrs/" target="_blank">WNRS</a> by 
            <a href="https://github.com/munjoonteo" target="_blank">munjoonteo</a> and 
            <a href="https://github.com/ilyues" target="_blank">ilyues</a>
        </div>
        """, unsafe_allow_html=True)

    # Right Column - History
    with col3:
        st.markdown(f"<h2 style='text-align: center; color: {st.session_state.text_color};'>PREVIOUS CARDS</h2>", unsafe_allow_html=True)
        
        # Display history
        for question in st.session_state.history:
            with st.container(border=True):
                st.markdown(
                    f"<div class='history-card' style='padding: 10px; text-align: center;'>"
                    f"<p style='color: {st.session_state.text_color}; font-weight: bold;'>{question['main_question']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )

with tab2:
    st.markdown(f"<h2 style='color: {st.session_state.text_color};'>Upload or Edit Question Data</h2>", unsafe_allow_html=True)
    
    # Display example data from the default CSV file
    st.markdown(f"<h3 style='color: {st.session_state.text_color};'>Current Data</h3>", unsafe_allow_html=True)
    if not st.session_state.df.empty:
        st.dataframe(st.session_state.df)
    
    # CSV file uploader
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Read the uploaded CSV
            df = pd.read_csv(uploaded_file)
            
            # Check if the required columns exist
            required_columns = ['main_question', 'Category']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"CSV is missing required columns: {', '.join(missing_columns)}")
            else:
                st.session_state.df = df
                st.success("CSV file uploaded successfully!")
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
    
    # Save the current dataframe to a file
    if not st.session_state.df.empty and st.button("Save to CSV file"):
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Save to CSV
            csv_path = os.path.join('data', 'quitting_questions.csv')
            st.session_state.df.to_csv(csv_path, index=False)
            st.success(f"Data saved to {csv_path}")
        except Exception as e:
            st.error(f"Error saving CSV file: {e}")
