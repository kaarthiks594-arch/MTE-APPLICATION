import streamlit as st
import pandas as pd
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="MTE Calculator", layout="centered")

# ---------------- LOAD LOGO ----------------
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image("kone_logo.png")

# ---------------- LOAD EXCEL ----------------
try:
    ken_db = pd.read_excel("ken_database.xlsx")
    ken_db.columns = ken_db.columns.str.strip()
except:
    ken_db = pd.DataFrame(columns=["Ken no", "Electrification","Drive System","Machinery","Car Door","Landing Door"])

try:
    actions_db = pd.read_excel("replacement_actions.xlsx")
    actions_db.columns = actions_db.columns.str.strip()
except:
    actions_db = pd.DataFrame(columns=["Module", "Variant", "Electrification", "Replacement Action"])

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "mode": None,
    "ken_number": "",
    "electrification": "",
    "selected_modules": [],
    "selected_actions": [],
    "results": {},
    "show_popup": {},
    "overall_mte": 0,
    "from_ken": False,
    "ken_variants": {}
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- RESET FUNCTIONS ----------------
def reset_session_state():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

def clear_selections():
    st.session_state.selected_modules = []
    st.session_state.selected_actions = []
    st.session_state.results.clear()
    st.session_state.show_popup.clear()
    st.session_state.overall_mte = 0
    st.rerun()

# ---------------- STYLE ----------------
st.markdown("""
<style>

.stButton > button{
background:#1450F5;
color:white;
height:48px;
border:none;
font-weight:bold;
border-radius:0px !important;
}

.module-box{
border:1px solid #ddd;
padding:12px;
background:#f8f8f8;
margin-bottom:20px;
}

.result-card{
background:#1450F5;
color:white;
padding:16px;
margin:10px 0;
}

.popup-card{
background:#1E5CFF;
color:white;
padding:12px;
margin-bottom:20px;
}

.overall-card{
background:#1450F5;
color:white;
padding:20px;
margin-top:20px;
margin-bottom:18px;
text-align:center;
font-weight:bold;
}

[data-baseweb="tag"]{
background:#1450F5 !important;
color:white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
st.markdown(f"""
<div style='text-align:center; margin-top:2mm; margin-bottom:2mm;'>
    <img src="data:image/png;base64,{logo_base64}" width="140">
</div>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div style='background:#1450F5;padding:15px;text-align:center'>
<h2 style='color:white'>MTE Calculator</h2>
</div>
""", unsafe_allow_html=True)

st.write("")

# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.mode is None:

    option = st.radio("", ["Search KEN No", "Browse Modules"])

    if st.button("Continue"):

        if option == "Search KEN No":
            st.session_state.mode = "ken"
        else:
            st.session_state.mode = "modules"

        st.rerun()

# =====================================================
# KEN SEARCH PAGE
# =====================================================
elif st.session_state.mode == "ken":

    st.subheader("Search KEN Number")

    ken = st.text_input("Enter KEN Number")

    col1,col2 = st.columns([4,1])

    if col1.button("Search"):

        row = ken_db[ken_db["Ken no"].astype(str) == ken]

        if not row.empty:

            st.session_state.selected_modules=[]
            st.session_state.selected_actions=[]
            st.session_state.results.clear()
            st.session_state.show_popup.clear()

            st.session_state.ken_number = ken
            st.session_state.electrification = row.iloc[0]["Electrification"]

            ken_row = row.iloc[0]

            st.session_state.ken_variants = {
                "Drive System": ken_row["Drive System"],
                "Machinery": ken_row["Machinery"],
                "Car Door": ken_row["Car Door"],
                "Landing Door": ken_row["Landing Door"]
            }

            st.session_state.from_ken = True
            st.session_state.mode="modules"

            st.rerun()

        else:
            st.error("KEN number not found")

    if col2.button("Home"):
        reset_session_state()

# =====================================================
# MODULE PAGE
# =====================================================
elif st.session_state.mode == "modules":

    # --------- DUMMY MODULES (NEW FINE TUNE) ---------
    dummy_modules = [
        "Counterweights",
        "Ropes and compensation",
        "Guide shoe",
        "Electrification",
        "Shaft equipments",
        "Peripheral devices",
        "Car Slings",
        "Signalization"
    ]

    if st.session_state.from_ken:

        st.markdown(f"**KEN No : {st.session_state.ken_number}**")
        st.markdown(f"**Electrification : {st.session_state.electrification}**")

        html=""

        for module,variant in st.session_state.ken_variants.items():
            if variant:
                html += f"{module} - {variant}<br>"

        st.markdown(
            f"<div class='module-box'>{html}</div>",
            unsafe_allow_html=True
        )

        MODULES = list(st.session_state.ken_variants.keys()) + dummy_modules

    else:
        MODULES = sorted(actions_db["Module"].dropna().unique()) + dummy_modules

    st.markdown("### Modules")

    cols_per_row = 3

    for i in range(0,len(MODULES),cols_per_row):

        row_modules = MODULES[i:i+cols_per_row]
        cols = st.columns(cols_per_row)

        for j,module in enumerate(row_modules):

            if cols[j].button(module,key=f"module_{module}"):

                if module in st.session_state.selected_modules:

                    st.session_state.selected_modules.remove(module)

                    st.session_state.selected_actions = [
                        a for a in st.session_state.selected_actions
                        if not a.endswith(f" - {module}")
                    ]

                    st.rerun()

                else:
                    st.session_state.selected_modules.append(module)
                    st.rerun()

    if st.session_state.selected_modules:

        st.markdown("**Selected Modules**")

        cols = st.columns(len(st.session_state.selected_modules))

        for i,module in enumerate(st.session_state.selected_modules):

            if cols[i].button(f"{module} ✕",key=f"remove_{module}"):

                st.session_state.selected_modules.remove(module)

                st.session_state.selected_actions = [
                    a for a in st.session_state.selected_actions
                    if not a.endswith(f" - {module}")
                ]

                st.rerun()


    st.markdown("### Replacement Actions")

    if st.session_state.selected_modules:

        options=[]

        for module in st.session_state.selected_modules:

            variant = st.session_state.ken_variants.get(module,"")

            df = actions_db[
                (actions_db["Module"]==module) & 
                ((actions_db["Electrification"]==st.session_state.electrification) | (not st.session_state.from_ken)) &
                ((actions_db["Variant"]==variant) | (not st.session_state.from_ken))
            ]

            for _,r in df.iterrows():

                options.append(
                    f"{r['Replacement Action']} - {r['Variant']} - {module}"
                )

        options = sorted(list(set(options)))

        selected = st.multiselect(
            "Search replacement actions",
            options,
            default=[a for a in st.session_state.selected_actions if a in options],
            key="replacement_dropdown"
        )

        st.session_state.selected_actions = selected

    if st.session_state.from_ken:
        col1,col2,col3,col4 = st.columns(4)
    else:
        col1,col2,col3 = st.columns(3)

    if col1.button("Calculate MTE"):

        st.session_state.results.clear()
        st.session_state.show_popup.clear()  # <-- reset popups when new calculation

        total=0

        for action in st.session_state.selected_actions:

            result={
                "time":4.5,
                "manpower":3,
                "prep":1,
                "replace":2.5,
                "final":1
            }

            st.session_state.results[action]=result
            total += result["time"]

        st.session_state.overall_mte = total
        st.session_state.mode="result"

        st.rerun()

    if col2.button("Clear"):
        clear_selections()

    if st.session_state.from_ken:

        if col3.button("KEN Search"):
            st.session_state.mode="ken"
            st.rerun()

        if col4.button("Home"):
            reset_session_state()

    else:

        if col3.button("Home"):
            reset_session_state()

# =====================================================
# RESULT PAGE
# =====================================================
elif st.session_state.mode == "result":

    st.markdown("## Result")

    if st.session_state.from_ken:

        st.markdown(
            f"<div class='result-card'><b>Electrification : {st.session_state.electrification}</b></div>",
            unsafe_allow_html=True
        )

    for action,data in st.session_state.results.items():

        st.markdown(
            f"<div class='result-card'><b>{action}</b></div>",
            unsafe_allow_html=True
        )

        c1,c2,c3 = st.columns(3)

        c1.write("Time")
        c1.write(data["time"])

        if action not in st.session_state.show_popup:
            st.session_state.show_popup[action]=False

        if c2.button("View",key=action):

            st.session_state.show_popup[action] = not st.session_state.show_popup[action]

        c3.write("Manpower")
        c3.write(data["manpower"])

        if st.session_state.show_popup[action]:

            st.markdown(
                f"""
                <div class='popup-card'>
                Preparation : {data['prep']} <br><br>
                Replacement : {data['replace']} <br><br>
                Finalisation : {data['final']}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        f"<div class='overall-card'>Overall MTE : {st.session_state.overall_mte}</div>",
        unsafe_allow_html=True
    )

    if st.session_state.from_ken:

        col1,col2,col3 = st.columns(3)

        if col1.button("Back"):
            st.session_state.mode="modules"
            st.rerun()

        if col2.button("KEN Search"):
            st.session_state.mode="ken"
            st.rerun()

        if col3.button("Home"):
            reset_session_state()

    else:

        col1,col2 = st.columns(2)

        if col1.button("Back"):
            st.session_state.mode="modules"
            st.rerun()

        if col2.button("Home"):
            reset_session_state()
