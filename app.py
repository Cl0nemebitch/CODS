import streamlit as st
from PIL import Image
import os
import random
import base64
from io import BytesIO

from predict import CAMOUFLAGE_THRESHOLD, UNCERTAIN_MARGIN, load_model, predict_image

# 1. Page Configuration and Layout
st.set_page_config(
    page_title="CODS - The Discerning Naturalist",
    page_icon="🔬",
    layout="wide",
)

# Helper function to get base64 encoded string of PIL Image
def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Helper function to get base64 of file on disk
def get_file_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return ""

# Helper to select a random sample from local dataset
def select_random_sample():
    camo_dir = "dataset/Train/camouflage"
    normal_dir = "dataset/Train/normal"
    
    camo_exists = os.path.exists(camo_dir)
    normal_exists = os.path.exists(normal_dir)
    
    images = []
    
    if camo_exists:
        camo_files = [os.path.join(camo_dir, f) for f in os.listdir(camo_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if camo_files:
            images.extend([(f, True) for f in camo_files])
            
    if normal_exists:
        normal_files = [os.path.join(normal_dir, f) for f in os.listdir(normal_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if normal_files:
            images.extend([(f, False) for f in normal_files])
            
    if not images:
        return
        
    img_path, is_camo = random.choice(images)
    img = Image.open(img_path)
    st.session_state.selected_image = img
    
    if is_camo:
        st.session_state.meta_source = random.choice([
            "Field Dataset A-12", "Canopy Dataset C-08", "Forest Floor F-22", "Swamp Sample S-15"
        ])
    else:
        st.session_state.meta_source = random.choice([
            "Control Dataset B-04", "Standard Meadow M-02", "Urban Foliage U-10", "Plain Grassland G-05"
        ])
        
    st.session_state.meta_res = f"{img.size[0]}px"
    st.session_state.meta_date = f"Captured: {random.choice(['Oct 2023', 'Nov 2023', 'Dec 2023', 'Jan 2024', 'Mar 2024', 'Apr 2024'])}"
    st.session_state.image_analyzed = False

# Initialize Session State Variables
if "selected_image" not in st.session_state:
    st.session_state.selected_image = None
if "meta_source" not in st.session_state:
    st.session_state.meta_source = ""
if "meta_res" not in st.session_state:
    st.session_state.meta_res = ""
if "meta_date" not in st.session_state:
    st.session_state.meta_date = ""
if "image_analyzed" not in st.session_state:
    st.session_state.image_analyzed = False
if "verdict_label" not in st.session_state:
    st.session_state.verdict_label = "Awaiting Analysis"
if "verdict_confidence" not in st.session_state:
    st.session_state.verdict_confidence = 0.0
if "verdict_probability" not in st.session_state:
    st.session_state.verdict_probability = 0.0
if "custom_threshold" not in st.session_state:
    st.session_state.custom_threshold = CAMOUFLAGE_THRESHOLD
if "custom_margin" not in st.session_state:
    st.session_state.custom_margin = UNCERTAIN_MARGIN
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

# 2. Inject CSS Styles to Match Template Exactly
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <style>
    /* Global styles and backgrounds */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #FAF8F5 !important;
        color: #1A1D1A !important;
    }
    
    /* Layout Container spacing */
    .main .block-container {
        max-width: 1200px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Hide default Streamlit headers, menus, footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* Center align the horizontal header columns vertically */
    [data-testid="stHorizontalBlock"]:has(.logo-container) {
        align-items: center !important;
    }
    
    /* Custom Header Styles */
    .main-header {
        border-bottom: 1px solid #EAE6DF;
        padding-bottom: 15px;
        margin-bottom: 35px;
    }
    .logo-container {
        display: flex;
        align-items: center;
        padding-top: 10px;
    }
    .logo-title {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 2.2rem;
        font-weight: 800;
        color: #3B4E38;
        letter-spacing: -0.5px;
    }
    .logo-pipe {
        font-size: 1.8rem;
        color: #E2DDD5;
        margin: 0 20px;
        font-weight: 300;
    }
    .logo-sub {
        font-size: 1.15rem;
        color: #8B8579;
        font-weight: 500;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .header-right-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 15px;
    }
    
    /* Section Title Styles */
    .section-title-container {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .section-main-title {
        font-size: 1.95rem;
        font-weight: 700;
        color: #1A1D1A;
        margin: 0;
    }
    .section-subtitle {
        font-size: 0.95rem;
        color: #8B8579;
        margin: 4px 0 0 0;
    }
    
    /* Image card viewport corners */
    .image-card {
        background-color: #FFFFFF;
        border: 1px solid #EAE6DF;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(92, 86, 76, 0.03);
        margin-top: 20px;
    }
    .viewport-container {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        background-color: #FAF8F5;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        aspect-ratio: 16/10.5;
    }
    .viewport-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 16px;
    }
    .viewfinder-corner {
        position: absolute;
        width: 24px;
        height: 24px;
        border: 1.5px solid rgba(255, 255, 255, 0.5);
        pointer-events: none;
    }
    .top-left { top: 25px; left: 25px; border-right: none; border-bottom: none; }
    .top-right { top: 25px; right: 25px; border-left: none; border-bottom: none; }
    .bottom-left { bottom: 25px; left: 25px; border-right: none; border-top: none; }
    .bottom-right { bottom: 25px; right: 25px; border-left: none; border-top: none; }
    
    /* Metadata Pills */
    .metadata-row {
        display: flex;
        gap: 12px;
        margin-top: 16px;
        flex-wrap: wrap;
    }
    .meta-pill {
        background-color: #FAF8F5;
        border: 1px solid #EAE6DF;
        border-radius: 12px;
        padding: 6px 14px;
        font-size: 0.85rem;
        color: #5C564C;
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
    }
    .meta-icon {
        font-size: 0.95rem;
        color: #7A756B;
    }
    
    /* Detection Verdict card */
    .verdict-card {
        background-color: #FAF6EE;
        border: 1px solid #EAE6DF;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 8px 30px rgba(92, 86, 76, 0.03);
        height: 100%;
        margin-top: 20px;
    }
    .dashed-verdict-container {
        border: 2.2px dashed #D9D2C4;
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 45px 20px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 270px;
        transition: all 0.3s ease;
    }
    .dashed-verdict-container.result-camo {
        border-color: #F4E3DD;
        background-color: #FFFDFD;
    }
    .dashed-verdict-container.result-normal {
        border-color: #E4ECDF;
        background-color: #FDFFFD;
    }
    .dashed-verdict-container.result-uncertain {
        border-color: #F6EEDA;
        background-color: #FFFAFD;
    }
    
    .status-icon-circle {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    .bg-neutral { background-color: #FAF8F5; border: 1.5px solid #EAE6DF; }
    .bg-camo { background-color: #F4E3DD; }
    .bg-normal { background-color: #E4ECDF; }
    .bg-uncertain { background-color: #F6EEDA; }
    
    .status-icon {
        font-size: 1.5rem;
        color: #5C564C;
    }
    .icon-camo { color: #B2503A; }
    .icon-normal { color: #3B4E38; }
    .icon-uncertain { color: #B2893A; }
    
    .verdict-status-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 10px 0;
        color: #1A1D1A;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .text-camo { color: #B2503A !important; }
    .text-normal { color: #3B4E38 !important; }
    .text-uncertain { color: #B2893A !important; }
    
    .verdict-status-desc {
        font-size: 0.95rem;
        color: #8B8579;
        margin: 0;
        max-width: 290px;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* Processing Confidence Indicator */
    .confidence-container {
        margin-top: 25px;
        margin-bottom: 25px;
    }
    .confidence-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        font-weight: 700;
        color: #5C564C;
        margin-bottom: 8px;
    }
    .confidence-value {
        font-weight: 800;
        color: #1A1D1A;
    }
    .progress-track {
        background-color: #EAE5D9;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        width: 100%;
    }
    .progress-fill {
        height: 100%;
        width: 0%;
        border-radius: 4px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        background-color: #3B4E38;
    }
    .progress-fill.fill-camo { background-color: #B2503A; }
    .progress-fill.fill-normal { background-color: #3B4E38; }
    .progress-fill.fill-uncertain { background-color: #B2893A; }
    
    /* Custom Streamlit Button Styling (with sibling overrides to prevent theme collisions) */
    
    /* 1. Upload Custom Image button */
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] {
        width: auto !important;
        padding: 0 !important;
        margin: 0 !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] label {
        display: none !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        justify-content: flex-end !important;
        height: auto !important;
        width: auto !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section > div {
        display: none !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section button {
        background-color: #3B4E38 !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 9px 22px !important;
        font-size: 0 !important; /* Hide original text */
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(59, 78, 56, 0.1) !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section button::before {
        content: "\\f607"; /* bi-upload */
        font-family: "bootstrap-icons" !important;
        margin-right: 9px;
        font-size: 0.95rem !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section button::after {
        content: "Upload Image";
        font-size: 0.9rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section button,
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section button * {
        color: #FAF8F5 !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section button:hover {
        background-color: #2D3A26 !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] section button:hover * {
        color: #FFFFFF !important;
    }
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
    .element-container:has(.upload-btn-container) + .element-container div[data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"] {
        display: none !important;
    }
    
    /* 2. Run Algorithm button */
    .element-container:has(.run-btn-container) + .element-container button {
        background-color: #3B4E38 !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 14px 28px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.2s ease !important;
    }
    .element-container:has(.run-btn-container) + .element-container button,
    .element-container:has(.run-btn-container) + .element-container button * {
        color: white !important;
    }
    .element-container:has(.run-btn-container) + .element-container button::before {
        content: "\\f4f3"; /* bi-play-circle-fill */
        font-family: "bootstrap-icons" !important;
        margin-right: 9px;
        font-size: 1.15rem;
    }
    .element-container:has(.run-btn-container) + .element-container button:hover:not(:disabled) {
        background-color: #2D3A26 !important;
        box-shadow: 0 6px 18px rgba(45, 58, 38, 0.15) !important;
        transform: translateY(-1px);
    }
    .element-container:has(.run-btn-container) + .element-container button:disabled {
        background-color: #EAE5D9 !important;
        opacity: 0.7;
        cursor: not-allowed !important;
    }
    .element-container:has(.run-btn-container) + .element-container button:disabled,
    .element-container:has(.run-btn-container) + .element-container button:disabled * {
        color: #A19B8F !important;
    }
    
    /* 3. Clear button */
    .element-container:has(.clear-btn-container) + .element-container button {
        background-color: transparent !important;
        color: #7A756B !important;
        border: 1px solid #D3CDBC !important;
        border-radius: 20px !important;
        padding: 9px 18px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        width: auto !important;
        height: auto !important;
        transition: all 0.2s ease !important;
    }
    .element-container:has(.clear-btn-container) + .element-container button:hover {
        background-color: #EDE9DC !important;
        color: #1A1D1A !important;
    }
    
    /* Empty Card File Uploader Styles */
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #D3CDBC !important;
        border-radius: 24px !important;
        padding: 50px 20px !important;
        text-align: center !important;
        box-shadow: 0 8px 30px rgba(92, 86, 76, 0.03) !important;
        min-height: 270px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.2s ease !important;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"]:hover {
        border-color: #3B4E38 !important;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] label {
        display: none !important;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section > div {
        display: none !important;
    }
    /* Inject custom icon, subtitle, and layout */
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section::before {
        content: "\\f607"; /* bi-upload */
        font-family: "bootstrap-icons" !important;
        font-size: 2rem;
        color: #7A756B;
        background-color: #FAF8F5;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
        border: 1.5px solid #EAE6DF;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section::after {
        content: "Upload an environment sample to begin analysis";
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem;
        color: #8B8579;
        font-weight: 500;
        margin-top: 5px;
        margin-bottom: 15px;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section button {
        background-color: #3B4E38 !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 9px 22px !important;
        font-size: 0 !important; /* Hide original browse text */
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section button::after {
        content: "Browse files";
        font-size: 0.9rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section button,
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section button * {
        color: white !important;
    }
    .element-container:has(.image-card-empty) + .element-container div[data-testid="stFileUploader"] section button:hover {
        background-color: #2D3A26 !important;
    }
    
    /* Popovers (Gear and Help Icons) styled via robust selectors to avoid styling collision across Streamlit versions */
    div[data-testid="stPopover"] button {
        background: transparent !important;
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        color: transparent !important;
        font-size: 0 !important;
    }
    div[data-testid="stPopover"] button svg {
        display: none !important; /* Hide the default chevron icon */
    }
    div[data-testid="stPopover"] button:hover {
        background-color: #EAE5D9 !important;
        transform: scale(1.05) !important;
    }

    /* Style the header column containing the settings buttons as a flexbox row */
    div[data-testid="column"]:has(.settings-btn-container) {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        align-items: center !important;
        gap: 12px !important;
        height: auto !important;
        padding-top: 10px !important; /* Align vertically with the logo */
    }

    /* Hide the empty anchor containers so they don't take up space in the flex layout */
    div[data-testid="column"]:has(.settings-btn-container) .element-container:has(.settings-btn-container),
    div[data-testid="column"]:has(.settings-btn-container) .element-container:has(.help-btn-container) {
        display: none !important;
    }

    /* Set the popover element containers to auto width inside the flex layout */
    div[data-testid="column"]:has(.settings-btn-container) .element-container:has(div[data-testid="stPopover"]) {
        width: auto !important;
        margin: 0 !important;
    }

    /* 1. Settings Popover Button Icon (Gear) */
    .element-container:has(.settings-btn-container) + .element-container div[data-testid="stPopover"] button::before,
    .settings-btn-container + div div[data-testid="stPopover"] button::before {
        content: "\\f3e5" !important; /* bi-gear */
        font-family: "bootstrap-icons" !important;
        font-size: 1.35rem !important;
        color: #5C564C !important;
        display: block !important;
    }
    .element-container:has(.settings-btn-container) + .element-container div[data-testid="stPopover"] button:hover::before,
    .settings-btn-container + div div[data-testid="stPopover"] button:hover::before {
        color: #1A1D1A !important;
    }

    /* 2. Help Popover Button Icon (Question) */
    .element-container:has(.help-btn-container) + .element-container div[data-testid="stPopover"] button::before,
    .help-btn-container + div div[data-testid="stPopover"] button::before {
        content: "\\f506" !important; /* bi-question-circle */
        font-family: "bootstrap-icons" !important;
        font-size: 1.35rem !important;
        color: #5C564C !important;
        display: block !important;
    }
    .element-container:has(.help-btn-container) + .element-container div[data-testid="stPopover"] button:hover::before,
    .help-btn-container + div div[data-testid="stPopover"] button:hover::before {
        color: #1A1D1A !important;
    }
    
    /* Custom Popover Content Slider Styles */
    div[data-testid="stPopover"] div[data-testid="stButton"] button {
        background-color: #3B4E38 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        border: none !important;
    }
    div[data-testid="stPopover"] div[data-testid="stButton"] button,
    div[data-testid="stPopover"] div[data-testid="stButton"] button * {
        color: white !important;
    }
    
    /* Custom Avatar Styling */
    .avatar-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 40px;
        width: 40px;
    }
    .avatar-img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid #EAE6DF;
    }
    .avatar-img-fallback {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #EAE6DF;
        color: #7A756B;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    
    /* Footer Styling */
    .app-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FAF6EE !important;
        padding: 24px 40px;
        margin-top: 60px;
        border-top: 1px solid #EAE6DF;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .footer-left {
        display: flex;
        align-items: center;
    }
    .footer-logo {
        font-weight: 800;
        color: #354730;
        margin-right: 15px;
        font-size: 1.15rem;
    }
    .footer-copyright {
        color: #8B8579;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .footer-right {
        display: flex;
        gap: 30px;
    }
    .footer-link {
        color: #5C564C !important;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 600;
        transition: color 0.2s;
    }
    .footer-link:hover {
        color: #354730 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Model Loading with Cache
@st.cache_resource
def get_model():
    return load_model()

# --- HEADER SECTION ---
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown(
        """
        <div class="logo-container">
            <span class="logo-title">CODS</span>
            <span class="logo-pipe">|</span>
            <span class="logo-sub">The Discerning Naturalist</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with header_col2:
    st.markdown('<div class="settings-btn-container"></div>', unsafe_allow_html=True)
    with st.popover(""):
        st.markdown("### ⚙️ Settings")
        
        # Select Random Sample Option inside settings
        st.markdown("#### 🔀 Load Validation Sample")
        random_sample_clicked = st.button("Load Random Sample", key="popover_random_sample", use_container_width=True)
        if random_sample_clicked:
            select_random_sample()
            st.session_state.last_uploaded_name = None
            st.rerun()
            
        st.markdown("#### 🛠️ Classifier Tuning")
        custom_threshold = st.slider(
            "Camouflage Threshold",
            min_value=0.1,
            max_value=0.9,
            value=float(st.session_state.custom_threshold),
            step=0.05
        )
        st.session_state.custom_threshold = custom_threshold

        custom_margin = st.slider(
            "Uncertainty Margin",
            min_value=0.0,
            max_value=0.3,
            value=float(st.session_state.custom_margin),
            step=0.02
        )
        st.session_state.custom_margin = custom_margin
        
    st.markdown('<div class="help-btn-container"></div>', unsafe_allow_html=True)
    with st.popover(""):
        st.markdown("### 🔬 About CODS")
        st.markdown(
            """
            **CODS: Camouflaged Object Detection System**
            
            This neural classifier evaluates visual patterns to detect camouflaged objects in natural environments.
            
            - **Upload Image**: Submits your own custom environment photo for neural evaluation.
            - **Run Algorithm**: Submits the active image to a Custom Deep Convolutional Neural Network (CNN) trained to identify high-frequency texture anomalies.
            - **Inference**: Resolves class status and displays confidence metrics.
            - **Settings Menu**: Lets you adjust confidence thresholds or quickly load a random sample from our database.
            """
        )

# --- MAIN CONTENT LAYOUT ---
col1, col2 = st.columns(2, gap="large")

# Left Column: Dataset Explorer
with col1:
    title_col, btn_col = st.columns([1.6, 1])
    with title_col:
        st.markdown(
            """
            <div class="section-title-container">
                <h3 class="section-main-title">Dataset Explorer</h3>
                <p class="section-subtitle">Select an environment sample for analysis.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with btn_col:
        if st.session_state.selected_image is not None:
            btn_sub_col1, btn_sub_col2 = st.columns([2, 1])
            with btn_sub_col1:
                st.markdown('<div class="upload-btn-container">', unsafe_allow_html=True)
                uploaded_file = st.file_uploader(
                    "Upload Image",
                    type=["png", "jpg", "jpeg"],
                    key="main_uploader"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            with btn_sub_col2:
                st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
                clear_clicked = st.button("🗑️", key="btn_clear", help="Clear Selection")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="upload-btn-container">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload Image",
                type=["png", "jpg", "jpeg"],
                key="main_uploader"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            clear_clicked = False
            
    # Handle Button Actions
    if uploaded_file is not None:
        if st.session_state.last_uploaded_name != uploaded_file.name:
            img = Image.open(uploaded_file)
            st.session_state.selected_image = img
            st.session_state.meta_source = "User Upload"
            st.session_state.meta_res = f"{img.size[0]}x{img.size[1]}px"
            st.session_state.meta_date = "Captured: Just Now"
            st.session_state.image_analyzed = False
            st.session_state.last_uploaded_name = uploaded_file.name
            st.rerun()
            
    if clear_clicked:
        st.session_state.selected_image = None
        st.session_state.image_analyzed = False
        st.session_state.last_uploaded_name = None
        st.rerun()

    # Image Card View
    if st.session_state.selected_image is None:
        st.markdown('<div class="image-card-empty">', unsafe_allow_html=True)
        card_uploaded_file = st.file_uploader(
            "Upload environment sample",
            type=["png", "jpg", "jpeg"],
            key="card_uploader"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle Card Uploader Actions
        if card_uploaded_file is not None:
            if st.session_state.last_uploaded_name != card_uploaded_file.name:
                img = Image.open(card_uploaded_file)
                st.session_state.selected_image = img
                st.session_state.meta_source = "User Upload"
                st.session_state.meta_res = f"{img.size[0]}x{img.size[1]}px"
                st.session_state.meta_date = "Captured: Just Now"
                st.session_state.image_analyzed = False
                st.session_state.last_uploaded_name = card_uploaded_file.name
                st.rerun()
    else:
        img_b64 = get_image_base64(st.session_state.selected_image)
        st.markdown(
            f"""
            <div class="image-card">
                <div class="viewport-container">
                    <img class="viewport-img" src="data:image/png;base64,{img_b64}"/>
                    <div class="viewfinder-corner top-left"></div>
                    <div class="viewfinder-corner top-right"></div>
                    <div class="viewfinder-corner bottom-left"></div>
                    <div class="viewfinder-corner bottom-right"></div>
                </div>
                <div class="metadata-row">
                    <div class="meta-pill"><i class="bi bi-database meta-icon"></i> Source: {st.session_state.meta_source}</div>
                    <div class="meta-pill"><i class="bi bi-aspect-ratio meta-icon"></i> Resolution: {st.session_state.meta_res}</div>
                    <div class="meta-pill"><i class="bi bi-calendar-event meta-icon"></i> {st.session_state.meta_date}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Right Column: Detection Verdict
with col2:
    st.markdown(
        """
        <div class="section-title-container">
            <h3 class="section-main-title">Detection Verdict</h3>
            <p class="section-subtitle">Neural evaluation of visual camouflage.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Verdict Card Frame
    st.markdown('<div class="verdict-card">', unsafe_allow_html=True)
    
    if not st.session_state.image_analyzed:
        # Initial awaiting state
        st.markdown(
            """
            <div class="dashed-verdict-container">
                <div class="status-icon-circle bg-neutral">
                    <i class="bi bi-microscope status-icon"></i>
                </div>
                <h4 class="verdict-status-title">Awaiting Analysis</h4>
                <p class="verdict-status-desc">Run the algorithm to scan for<br>camouflaged entities within the<br>selected image.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        confidence_val = 0.0
        color_class = "neutral"
    else:
        label = st.session_state.verdict_label
        confidence_val = st.session_state.verdict_confidence
        
        if label == "Camouflage Detected":
            color_class = "camo"
            icon_cls = "bi bi-eye-slash-fill icon-camo"
            title = "Camouflage Detected"
            desc = "High probability of camouflage pattern match. Texture blending indicates a masked target."
        elif label == "No Camouflage":
            color_class = "normal"
            icon_cls = "bi bi-check-circle-fill icon-normal"
            title = "No Camouflage"
            desc = "Standard background features detected. No significant camouflage signature pattern found."
        else: # Uncertain Match
            color_class = "uncertain"
            icon_cls = "bi bi-exclamation-circle-fill icon-uncertain"
            title = "Uncertain Match"
            desc = "Model confidence is low. Try a clearer image or adjust thresholds in settings."
            
        st.markdown(
            f"""
            <div class="dashed-verdict-container result-{color_class}">
                <div class="status-icon-circle bg-{color_class}">
                    <i class="{icon_cls} status-icon"></i>
                </div>
                <h4 class="verdict-status-title text-{color_class}">{title}</h4>
                <p class="verdict-status-desc">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # Processing Confidence Level Indicator
    st.markdown(
        f"""
        <div class="confidence-container">
            <div class="confidence-header">
                <span class="confidence-label">Processing Confidence</span>
                <span class="confidence-value">{confidence_val:.1f}%</span>
            </div>
            <div class="progress-track">
                <div class="progress-fill fill-{color_class}" style="width: {confidence_val}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Run Algorithm Button
    st.markdown('<div class="run-btn-container">', unsafe_allow_html=True)
    is_disabled = st.session_state.selected_image is None
    run_clicked = st.button("Run Algorithm", key="btn_run", disabled=is_disabled, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # End of verdict-card

# Handle Run Action
if run_clicked and st.session_state.selected_image is not None:
    with st.spinner("Analyzing image patterns..."):
        try:
            model = get_model()
        except Exception as e:
            st.error("Model file not found. Make sure to run model training first.")
            st.stop()
            
        label, confidence, probability = predict_image(
            st.session_state.selected_image, 
            model=model, 
            threshold=st.session_state.custom_threshold,
            margin=st.session_state.custom_margin
        )
        
        st.session_state.verdict_label = label
        st.session_state.verdict_confidence = confidence
        st.session_state.verdict_probability = probability
        st.session_state.image_analyzed = True
        st.rerun()

# --- FOOTER SECTION ---
st.markdown(
    """
    <footer class="app-footer">
        <div class="footer-left">
            <span class="footer-logo">CODS</span>
            <span class="footer-copyright">© 2024 CODS v1.0.2 - The Discerning Naturalist</span>
        </div>
        <div class="footer-right">
            <a href="#" class="footer-link">Documentation</a>
            <a href="#" class="footer-link">Privacy Policy</a>
            <a href="#" class="footer-link">System Status</a>
        </div>
    </footer>
    """,
    unsafe_allow_html=True
)
