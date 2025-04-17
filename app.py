import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import json
import os

# Config
CANVAS_SIZE = 400
MAX_POINTS = 100
MIN_POINTS = 70
DATA_FILE = "saved_strokes.json"

# Load existing data (persistent across sessions)
if "all_data" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                st.session_state.all_data = json.load(f)
            except json.JSONDecodeError:
                st.session_state.all_data = []
    else:
        st.session_state.all_data = []

st.title("✍️ Hindi Numeral Stroke Recorder")

# Drawing canvas
canvas_result = st_canvas(
    fill_color="rgba(0,0,0,1)",
    stroke_width=4,
    stroke_color="#000000",
    background_color="#FFFFFF",
    width=CANVAS_SIZE,
    height=CANVAS_SIZE,
    drawing_mode="freedraw",
    key="canvas",
)


# Extract stroke points
def extract_points(json_data):
    points = []
    if json_data and "objects" in json_data:
        for obj in json_data["objects"]:
            if obj["type"] == "path":
                for cmd in obj["path"]:
                    if len(cmd) >= 3:
                        x, y = int(cmd[1]), int(cmd[2])
                        p = 0 if len(points) == 0 else 1
                        points.append([x, y, p])
    return points


# Downsample or pad to exactly 100
def process_points(points):
    total = len(points)
    if total > MAX_POINTS:
        indices = np.linspace(0, total - 1, MAX_POINTS, dtype=int)
        points = [points[i] for i in indices]
    elif total < MAX_POINTS:
        points += [[0, 0, 0]] * (MAX_POINTS - total)
    return points


# Display count
st.markdown(f"📦 **Total Saved Drawings**: `{len(st.session_state.all_data)}`")

# Save button
if st.button("💾 Save Drawing"):
    points = extract_points(canvas_result.json_data)

    if len(points) < MIN_POINTS:
        st.warning(f"⚠️ Too few points! Minimum {MIN_POINTS} required.")
    else:
        processed = process_points(points)
        st.session_state.all_data.append(processed)

        # Save to file
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(st.session_state.all_data, f)
            st.success("✅ Drawing saved successfully!")
        except Exception as e:
            st.error(f"❌ Failed to save drawing: {str(e)}")

# Option to view all saved stroke data
if st.checkbox("📋 Show All Saved Strokes"):
    if st.session_state.all_data:
        st.json(st.session_state.all_data)
    else:
        st.info("No saved strokes yet.")

# Option to browse stroke data by index
if st.checkbox("🔍 Browse Saved Drawing by Index"):
    if st.session_state.all_data:
        idx = st.slider(
            "Select Drawing Index", 0, len(st.session_state.all_data) - 1, 0
        )
        st.json(st.session_state.all_data[idx])
    else:
        st.info("No saved strokes to browse.")

# Clear all saved strokes
if st.button("🧹 Clear All Saved Strokes"):
    st.session_state.all_data = []
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.success("✅ All saved strokes cleared.")



