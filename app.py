import streamlit as st
import pandas as pd
import pickle
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Dubai Real Estate Price Predictor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .price-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .price-value {
        font-size: 3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Load model and rules
@st.cache_resource
def load_all_components():
    """Load model, encoders, and rules"""
    import gzip

    # Load compressed model
    try:
        with gzip.open('model/random_forest_model.pkl.gz', 'rb') as f:
            model = pickle.load(f)
    except FileNotFoundError:
        # Fallback to uncompressed
        with open('model/random_forest_model.pkl', 'rb') as f:
            model = pickle.load(f)

    with open('model/label_encoder_area.pkl', 'rb') as f:
        le_area = pickle.load(f)

    with open('model/label_encoder_subtype.pkl', 'rb') as f:
        le_subtype = pickle.load(f)

    with open('model/label_encoder_regtype.pkl', 'rb') as f:
        le_regtype = pickle.load(f)

    with open('model/metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)

    try:
        with open('model/validation_rules.json', 'r') as f:
            validation_rules = json.load(f)
    except:
        validation_rules = None

    try:
        with open('model/dynamic_form_rules.json', 'r') as f:
            form_rules = json.load(f)
    except:
        form_rules = None

    try:
        with open('model/property_categorization.json', 'r') as f:
            categorization = json.load(f)
    except:
        categorization = None

    try:
        with open('model/location_multipliers.json', 'r') as f:
            location_multipliers = json.load(f)
    except:
        location_multipliers = None

    return model, le_area, le_subtype, le_regtype, metadata, validation_rules, form_rules, categorization, location_multipliers

# Helper functions
def safe_encode(encoder, value):
    """Safely encode categorical values"""
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    else:
        return encoder.transform([encoder.classes_[0]])[0]

def validate_inputs(area_size, bedrooms, property_subtype, validation_rules):
    """Validate inputs against rules and return warnings"""
    warnings = []

    if validation_rules is None:
        return warnings

    # Check size for given bedrooms
    bedroom_key = 'Studio' if bedrooms == 0 else f'{bedrooms}_bedroom'
    if bedroom_key in validation_rules.get('size_ranges', {}):
        size_info = validation_rules['size_ranges'][bedroom_key]
        min_size = size_info['min_typical']
        max_size = size_info['max_typical']

        if area_size < min_size * 0.7:
            warnings.append(f"⚠️ Size seems too small for {bedroom_key.replace('_', ' ')}. Typical range: {min_size:.0f}-{max_size:.0f} sqm")
        elif area_size > max_size * 1.5:
            warnings.append(f"⚠️ Size seems too large for {bedroom_key.replace('_', ' ')}. Typical range: {min_size:.0f}-{max_size:.0f} sqm")

    # Check property subtype specifics
    if property_subtype in validation_rules.get('property_subtype_specifics', {}):
        subtype_info = validation_rules['property_subtype_specifics'][property_subtype]

        if bedrooms not in subtype_info.get('typical_bedrooms', []):
            typical = subtype_info['typical_bedrooms']
            warnings.append(f"ℹ️ {property_subtype} typically has {min(typical)}-{max(typical)} bedrooms")

        size_range = subtype_info.get('size_range', [0, 1000])
        if area_size < size_range[0] or area_size > size_range[1]:
            warnings.append(f"ℹ️ {property_subtype} typically ranges {size_range[0]}-{size_range[1]} sqm")

    return warnings

def get_confidence_level(area_size, bedrooms, area_name, subtype, le_area, validation_rules):
    """Estimate confidence level"""
    confidence_score = 100

    if area_name not in le_area.classes_[:50]:
        confidence_score -= 15

    if subtype not in ['Flat', 'Villa', 'Hotel Apartment']:
        confidence_score -= 10

    # Check if size is within expected range
    if validation_rules:
        bedroom_key = 'Studio' if bedrooms == 0 else f'{bedrooms}_bedroom'
        if bedroom_key in validation_rules.get('size_ranges', {}):
            size_info = validation_rules['size_ranges'][bedroom_key]
            if area_size < size_info['min_typical'] * 0.7 or area_size > size_info['max_typical'] * 1.5:
                confidence_score -= 20

    if bedrooms > 5:
        confidence_score -= 10

    if confidence_score >= 85:
        return "High", "🟢"
    elif confidence_score >= 70:
        return "Medium", "🟡"
    else:
        return "Low", "🔴"

def get_expected_size_range(bedrooms, validation_rules):
    """Get expected size range for given bedrooms"""
    if validation_rules is None:
        return None

    bedroom_key = 'Studio' if bedrooms == 0 else f'{bedrooms}_bedroom'
    if bedroom_key in validation_rules.get('size_ranges', {}):
        size_info = validation_rules['size_ranges'][bedroom_key]
        return {
            'min': size_info['min_typical'],
            'max': size_info['max_typical'],
            'average': size_info['average']
        }
    return None

def format_price_millions(price):
    """Format price in millions (e.g., 1.2M, 1.3M)"""
    if price >= 1_000_000:
        millions = price / 1_000_000
        if millions >= 10:
            return f"{millions:.1f}M"
        else:
            return f"{millions:.2f}M"
    elif price >= 1_000:
        thousands = price / 1_000
        return f"{thousands:.0f}K"
    else:
        return f"{price:.0f}"

# Load components
try:
    model, le_area, le_subtype, le_regtype, metadata, validation_rules, form_rules, categorization, location_multipliers = load_all_components()
    model_loaded = True
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    model_loaded = False
    validation_rules = None
    form_rules = None
    categorization = None
    location_multipliers = None

# Header
st.markdown('<div class="main-header">🏢 Dubai Real Estate Price Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Property Valuation with Smart Form</div>', unsafe_allow_html=True)

if model_loaded:
    # Sidebar - Model Info
    with st.sidebar:
        st.header("📊 Model Information")
        st.metric("Model Type", metadata['model_type'].replace('Regressor', ''))
        st.metric("Training Samples", f"{metadata['training_samples']:,}")
        st.metric("R² Score", f"{metadata['r2_score']:.4f}")
        st.metric("MAE", f"{metadata['mae']:,.0f} AED")

        st.divider()
        st.header("ℹ️ About")
        st.info(
            "✨ **New:** Smart form with dynamic fields!\n\n"
            "Form adapts based on:\n"
            "- Property usage (Residential/Commercial)\n"
            "- Property type (Unit/Villa/Land)\n"
            "- Analysis of 1.5M transactions"
        )

        st.divider()
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")

    # Main content - Tabs
    tab1, tab2, tab3 = st.tabs(["🔮 Price Prediction", "📈 Batch Prediction", "📊 Data Insights"])

    # TAB 1: Single Prediction with Dynamic Form
    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Property Details - Smart Form")

            # Initialize session state for dynamic updates
            if 'property_usage' not in st.session_state:
                st.session_state.property_usage = 'Residential'
            if 'property_type' not in st.session_state:
                st.session_state.property_type = 'Unit'

            col_a, col_b = st.columns(2)

            with col_a:
                # 1. Property Usage
                if form_rules and 'property_usage_options' in form_rules:
                    usage_options = sorted(form_rules['property_usage_options'])
                    default_usage = 'Residential' if 'Residential' in usage_options else usage_options[0]
                else:
                    usage_options = ['Residential', 'Commercial']
                    default_usage = 'Residential'

                property_usage = st.selectbox(
                    "🏠 Property Usage",
                    options=usage_options,
                    index=usage_options.index(st.session_state.property_usage) if st.session_state.property_usage in usage_options else 0,
                    help="Select property usage category",
                    key='usage_select'
                )

                # Update session state
                if property_usage != st.session_state.property_usage:
                    st.session_state.property_usage = property_usage
                    st.rerun()

                # 2. Property Type (dynamic based on usage)
                if form_rules and property_usage in form_rules.get('property_type_by_usage', {}):
                    type_options = form_rules['property_type_by_usage'][property_usage]
                else:
                    type_options = ['Unit', 'Villa', 'Land', 'Building']

                if not type_options:
                    type_options = ['Unit', 'Villa', 'Land', 'Building']

                property_type = st.selectbox(
                    "🏗️ Property Type",
                    options=sorted(type_options),
                    index=sorted(type_options).index(st.session_state.property_type) if st.session_state.property_type in type_options else 0,
                    help="Select property type",
                    key='type_select'
                )

                # Update session state
                if property_type != st.session_state.property_type:
                    st.session_state.property_type = property_type
                    st.rerun()

                # 3. Property Sub-Type (dynamic based on usage AND type)
                if form_rules:
                    # Try to get subtypes for the specific usage
                    if property_usage in form_rules.get('property_subtype_by_usage', {}):
                        subtype_options = form_rules['property_subtype_by_usage'][property_usage]
                    # Fallback to type-based
                    elif property_type in form_rules.get('property_subtype_by_type', {}):
                        subtype_options = form_rules['property_subtype_by_type'][property_type]
                    else:
                        subtype_options = sorted(le_subtype.classes_)
                else:
                    subtype_options = sorted(le_subtype.classes_)

                # Filter based on categorization
                if categorization and property_usage == 'Residential':
                    residential_types = categorization.get('residential_subtypes', [])
                    subtype_options = [st for st in subtype_options if st in residential_types]
                elif categorization and property_usage == 'Commercial':
                    commercial_types = categorization.get('commercial_subtypes', [])
                    subtype_options = [st for st in subtype_options if st in commercial_types]

                if not subtype_options:
                    subtype_options = sorted(le_subtype.classes_)[:20]

                default_subtype = 'Flat' if 'Flat' in subtype_options else subtype_options[0]

                property_subtype = st.selectbox(
                    "🏘️ Property Sub-Type",
                    options=sorted(subtype_options),
                    index=sorted(subtype_options).index(default_subtype),
                    help="Select property sub-type"
                )

            with col_b:
                # 5. Bedrooms (conditional - only show if property type requires it)
                show_bedrooms = True
                if form_rules and property_type in form_rules.get('requires_bedrooms', {}):
                    show_bedrooms = form_rules['requires_bedrooms'][property_type]

                if show_bedrooms:
                    # Initialize bedroom state
                    if 'selected_bedrooms' not in st.session_state:
                        st.session_state.selected_bedrooms = 2
                    if 'last_bedrooms' not in st.session_state:
                        st.session_state.last_bedrooms = 2

                    bedrooms = st.selectbox(
                        "🛏️ Bedrooms",
                        options=[0, 1, 2, 3, 4, 5, 6],
                        index=st.session_state.selected_bedrooms if st.session_state.selected_bedrooms in [0,1,2,3,4,5,6] else 2,
                        format_func=lambda x: "Studio" if x == 0 else f"{x} Bedroom{'s' if x > 1 else ''}",
                        help="Select number of bedrooms (Studio = 0)",
                        key='bedrooms_select'
                    )

                    # Auto-update area size when bedroom changes
                    if bedrooms != st.session_state.last_bedrooms:
                        st.session_state.last_bedrooms = bedrooms
                        # Get suggested size based on new bedroom count
                        if validation_rules:
                            size_range = get_expected_size_range(bedrooms, validation_rules)
                            if size_range:
                                st.session_state.area_size = size_range['average']
                else:
                    bedrooms = 0
                    st.info("ℹ️ Bedrooms not applicable for this property type")

                # 4. Area Size with auto-fill
                # Initialize area size if not set
                if 'area_size' not in st.session_state:
                    suggested_size = 100.0
                    if validation_rules and show_bedrooms:
                        size_range = get_expected_size_range(bedrooms, validation_rules)
                        if size_range:
                            suggested_size = size_range['average']
                    st.session_state.area_size = suggested_size

                area_size = st.number_input(
                    "📐 Property Size (sqm)",
                    min_value=10.0,
                    max_value=999.0,
                    value=float(st.session_state.area_size),
                    step=5.0,
                    help="Auto-filled with average size for selected bedrooms",
                    key='area_input'
                )

                # Update area in state (only if user manually changed it)
                if area_size != st.session_state.area_size:
                    st.session_state.area_size = area_size

                # 6. Parking
                has_parking = st.radio(
                    "🚗 Parking",
                    options=[1, 0],
                    format_func=lambda x: "Yes" if x == 1 else "No",
                    horizontal=True
                )

                # 7. Location Area
                area_name = st.selectbox(
                    "📍 Location Area",
                    options=sorted(le_area.classes_),
                    index=sorted(le_area.classes_).index('DUBAI MARINA') if 'DUBAI MARINA' in le_area.classes_ else 0,
                    help="Select the property location"
                )

            # 8. Registration Type (dynamic based on property type)
            if form_rules and property_type in form_rules.get('typical_registration_types', {}):
                reg_type_options = form_rules['typical_registration_types'][property_type]
            else:
                reg_type_options = sorted(le_regtype.classes_)

            if not reg_type_options:
                reg_type_options = sorted(le_regtype.classes_)

            reg_type = st.selectbox(
                "📋 Registration Type",
                options=reg_type_options,
                help="Select registration type"
            )

            # 9. Named Project (removed as per requirement)
            has_project = 1  # Default to true for all properties

            # Show expected size range
            if validation_rules and show_bedrooms:
                expected_size = get_expected_size_range(bedrooms, validation_rules)
                if expected_size:
                    st.info(
                        f"💡 **Expected size for {'Studio' if bedrooms == 0 else f'{bedrooms} BR'}:** "
                        f"{expected_size['min']:.0f}-{expected_size['max']:.0f} sqm "
                        f"(avg: {expected_size['average']:.0f} sqm)"
                    )

            # Validate inputs and show warnings
            if validation_rules and show_bedrooms:
                input_warnings = validate_inputs(area_size, bedrooms, property_subtype, validation_rules)
                if input_warnings:
                    for warning in input_warnings:
                        st.warning(warning)

            # Predict button
            if st.button("🎯 Predict Price", type="primary", use_container_width=True):
                try:
                    # Encode features
                    area_encoded = safe_encode(le_area, area_name)
                    subtype_encoded = safe_encode(le_subtype, property_subtype)
                    regtype_encoded = safe_encode(le_regtype, reg_type)

                    # Create feature array
                    features = np.array([[
                        area_size,
                        bedrooms,
                        has_parking,
                        1 if has_project else 0,
                        area_encoded,
                        subtype_encoded,
                        regtype_encoded
                    ]])

                    # Make prediction
                    base_prediction = model.predict(features)[0]

                    # Apply location multiplier if available
                    location_multiplier = 1.0
                    if location_multipliers and area_name in location_multipliers:
                        location_multiplier = location_multipliers[area_name]

                    prediction = base_prediction * location_multiplier
                    price_per_sqm = prediction / area_size

                    # Get confidence
                    confidence, emoji = get_confidence_level(
                        area_size, bedrooms, area_name, property_subtype, le_area, validation_rules
                    )

                    # Store in session state
                    st.session_state['prediction'] = prediction
                    st.session_state['base_prediction'] = base_prediction
                    st.session_state['location_multiplier'] = location_multiplier
                    st.session_state['price_per_sqm'] = price_per_sqm
                    st.session_state['confidence'] = confidence
                    st.session_state['confidence_emoji'] = emoji
                    st.session_state['warnings'] = input_warnings if validation_rules and show_bedrooms else []
                    st.session_state['property_details'] = {
                        'usage': property_usage,
                        'type': property_type,
                        'subtype': property_subtype,
                        'size': area_size,
                        'bedrooms': bedrooms if show_bedrooms else 'N/A',
                        'area': area_name
                    }

                except Exception as e:
                    st.error(f"Prediction error: {str(e)}")

        with col2:
            st.subheader("Prediction Results")

            if 'prediction' in st.session_state:
                prediction = st.session_state['prediction']
                price_per_sqm = st.session_state['price_per_sqm']
                confidence = st.session_state['confidence']
                emoji = st.session_state['confidence_emoji']
                details = st.session_state.get('property_details', {})

                # Price range display (±10%)
                lower_bound = prediction * 0.90
                upper_bound = prediction * 1.10
                lower_formatted = format_price_millions(lower_bound)
                upper_formatted = format_price_millions(upper_bound)

                st.markdown(
                    f'<div class="price-box">'
                    f'<div style="font-size: 1.2rem;">Estimated Price Range</div>'
                    f'<div class="price-value">{lower_formatted} - {upper_formatted}</div>'
                    f'<div style="font-size: 1.2rem;">AED</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Show exact price and location multiplier
                multiplier = st.session_state.get('location_multiplier', 1.0)
                if multiplier != 1.0:
                    tier_name = {
                        2.0: "Ultra Luxury",
                        1.5: "Luxury",
                        1.2: "Premium",
                        0.9: "Budget"
                    }.get(multiplier, "Standard")
                    st.caption(f"Mid-point: {format_price_millions(prediction)} AED ({tier_name} Location {multiplier}x)")
                else:
                    st.caption(f"Mid-point: {format_price_millions(prediction)} AED")

                # Metrics
                st.metric(
                    "Price per sqm",
                    f"{format_price_millions(price_per_sqm)} AED",
                    help="Price per square meter (includes location premium)"
                )

                st.metric(
                    "Confidence Level",
                    f"{emoji} {confidence}",
                    help="Model confidence in this prediction"
                )

                # Additional info
                st.divider()
                st.caption(f"**Usage:** {details.get('usage', 'N/A')}")
                st.caption(f"**Type:** {details.get('type', 'N/A')}")
                st.caption(f"**Sub-Type:** {details.get('subtype', 'N/A')}")
                st.caption(f"**Size:** {details.get('size', 0):.1f} sqm")
                st.caption(f"**Bedrooms:** {details.get('bedrooms', 'N/A')}")
                st.caption(f"**Location:** {details.get('area', 'N/A')}")


                # Show validation warnings if any
                if 'warnings' in st.session_state and st.session_state['warnings']:
                    st.divider()
                    st.caption("**Input Validation Notes:**")
                    for warning in st.session_state['warnings']:
                        st.caption(warning)

            else:
                st.info("👈 Fill in the property details and click 'Predict Price' to see results")

    # TAB 2: Batch Prediction
    with tab2:
        st.subheader("Batch Price Prediction")
        st.write("Upload a CSV file with multiple properties to predict prices in bulk")

        # Sample template
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(
                "📋 **Required columns:** procedure_area, bedrooms, has_parking, has_project, "
                "area_name_en, property_sub_type_en, reg_type_en"
            )
        with col2:
            # Create sample data
            sample_data = pd.DataFrame({
                'procedure_area': [100, 150, 80],
                'bedrooms': [2, 3, 1],
                'has_parking': [1, 1, 0],
                'has_project': [1, 1, 1],
                'area_name_en': ['DUBAI MARINA', 'BUSINESS BAY', 'JUMEIRAH VILLAGE CIRCLE'],
                'property_sub_type_en': ['Flat', 'Flat', 'Flat'],
                'reg_type_en': ['Off-Plan Properties', 'Off-Plan Properties', 'Off-Plan Properties']
            })
            st.download_button(
                "📥 Download Template",
                data=sample_data.to_csv(index=False),
                file_name="batch_template.csv",
                mime="text/csv"
            )

        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write(f"Loaded {len(df)} properties")

                if st.button("🚀 Predict All Prices"):
                    predictions = []

                    progress_bar = st.progress(0)
                    for idx, row in df.iterrows():
                        area_encoded = safe_encode(le_area, row['area_name_en'])
                        subtype_encoded = safe_encode(le_subtype, row['property_sub_type_en'])
                        regtype_encoded = safe_encode(le_regtype, row['reg_type_en'])

                        features = np.array([[
                            row['procedure_area'],
                            row['bedrooms'],
                            row['has_parking'],
                            row['has_project'],
                            area_encoded,
                            subtype_encoded,
                            regtype_encoded
                        ]])

                        pred = model.predict(features)[0]
                        predictions.append(pred)

                        progress_bar.progress((idx + 1) / len(df))

                    df['predicted_price'] = predictions
                    df['price_per_sqm'] = df['predicted_price'] / df['procedure_area']

                    st.success(f"✅ Successfully predicted prices for {len(df)} properties!")

                    # Display results
                    st.dataframe(df, use_container_width=True)

                    # Summary statistics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Properties", len(df))
                    col2.metric("Avg. Price", f"{df['predicted_price'].mean():,.0f} AED")
                    col3.metric("Min Price", f"{df['predicted_price'].min():,.0f} AED")
                    col4.metric("Max Price", f"{df['predicted_price'].max():,.0f} AED")

                    # Download results
                    st.download_button(
                        "📥 Download Results",
                        data=df.to_csv(index=False),
                        file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    # TAB 3: Data Insights
    with tab3:
        st.subheader("Data Insights & Validation Rules")

        if form_rules:
            st.markdown("### 📊 Property Hierarchy")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Property Usage Categories")
                for usage in form_rules.get('property_usage_options', []):
                    st.caption(f"• {usage}")

                st.markdown("#### Bedrooms Required For:")
                for prop_type, required in form_rules.get('requires_bedrooms', {}).items():
                    if required:
                        st.caption(f"✅ {prop_type}")

            with col2:
                st.markdown("#### Bedrooms NOT Required For:")
                for prop_type, required in form_rules.get('requires_bedrooms', {}).items():
                    if not required:
                        st.caption(f"❌ {prop_type}")

            if categorization:
                st.divider()
                st.markdown("### 🏠 Property Categorization")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Residential Sub-Types")
                    for subtype in categorization.get('residential_subtypes', []):
                        st.caption(f"• {subtype}")

                with col2:
                    st.markdown("#### Commercial Sub-Types")
                    for subtype in categorization.get('commercial_subtypes', []):
                        st.caption(f"• {subtype}")

        st.divider()

        # Feature importance
        st.markdown("### 🎯 Key Price Factors")
        importance_data = pd.DataFrame({
            'Feature': ['Property Size', 'Location', 'Registration Type', 'Property Type', 'Bedrooms', 'Project', 'Parking'],
            'Importance': [66.2, 22.7, 5.1, 2.4, 1.5, 1.3, 0.7]
        })

        fig = px.bar(
            importance_data,
            x='Importance',
            y='Feature',
            orientation='h',
            title='Feature Importance in Price Prediction',
            color='Importance',
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "**Key Insight:** Property size accounts for 66% of price variation, "
            "followed by location at 23%. The smart form ensures you only see relevant options!"
        )

else:
    st.error("⚠️ Model files not found. Please run 'save_model.py' first to train and save the model.")
