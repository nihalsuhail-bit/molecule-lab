import json
import time
from io import StringIO

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

APP_TITLE = "Molecule Lab"
PUBCHEM = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
HEADERS = {"User-Agent": "MoleculeLabStudentProject/1.0 (educational chemistry explorer)"}

st.set_page_config(
    page_title="Molecule Lab | Explore Chemistry",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#eaf2ff; --muted:#9db0c8; --line:rgba(160,190,220,.16); --panel:#101c2d; --cyan:#72f0e0; }
html, body, [class*="css"] { font-family:'Manrope',sans-serif; }
.stApp { background: radial-gradient(ellipse at 78% 0%, #18304a 0%, #0a1220 43%, #080e18 100%); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(8,14,24,.65); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0d1929,#0a111d); border-right:1px solid var(--line); }
.block-container { padding-top:1.7rem; max-width:1440px; }
.hero { padding:1.4rem 0 1.1rem 0; }
.eyebrow { color:#72f0e0; text-transform:uppercase; letter-spacing:.19em; font-size:.72rem; font-weight:800; }
.hero h1 { color:#f1f6ff; font-size:clamp(2.3rem,5vw,4.1rem); line-height:1.04; letter-spacing:-.055em; margin:.45rem 0 .7rem 0; font-weight:800; }
.hero p { color:#a9bbd0; font-size:1rem; max-width:760px; line-height:1.7; }
.panel { background:linear-gradient(145deg,rgba(20,35,54,.94),rgba(12,23,37,.94)); border:1px solid var(--line); border-radius:20px; padding:1.15rem 1.25rem; box-shadow:0 14px 42px rgba(0,0,0,.16); }
.metric { background:rgba(17,31,48,.85); border:1px solid var(--line); border-radius:14px; padding:1rem; min-height:105px; }
.metric-label { color:#9db0c8; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; }
.metric-value { color:#f1f6ff; font-size:1.35rem; font-weight:800; margin-top:.35rem; overflow-wrap:anywhere; }
.section-title { color:#edf5ff; font-size:1.2rem; font-weight:800; letter-spacing:-.02em; margin:.4rem 0 .8rem 0; }
.small-muted { color:#9db0c8; font-size:.84rem; line-height:1.6; }
.tag { display:inline-block; border:1px solid rgba(114,240,224,.28); background:rgba(114,240,224,.07); color:#8ff8e9; border-radius:999px; padding:.25rem .6rem; font-size:.72rem; margin:0 .3rem .3rem 0; }
code, .stCode { font-family:'DM Mono',monospace!important; }
.stButton button, .stDownloadButton button { border-radius:12px; border:1px solid rgba(114,240,224,.35); font-weight:700; }
.stButton button[kind="primary"] { background:linear-gradient(90deg,#55d8d0,#8bf2d7); color:#07131c; }
div[data-testid="stAlert"] { border-radius:12px; }
hr { border-color:var(--line); }
</style>
""", unsafe_allow_html=True)

# Common, recognizable compounds to make first use effortless.
STARTER_MOLECULES = [
    "Water", "Ethanol", "Caffeine", "Glucose", "Aspirin", "Acetaminophen",
    "Citric acid", "Benzene", "Methane", "Acetic acid", "Urea", "Lactic acid",
    "Ibuprofen", "Nicotine", "Vanillin", "Theobromine", "Glycine", "ATP",
]

PROPERTY_DESCRIPTIONS = {
    "MolecularFormula": ("Molecular formula", "The types and numbers of atoms in one molecule, written using element symbols."),
    "MolecularWeight": ("Molecular weight", "Average mass per mole of compound, reported in g/mol."),
    "IUPACName": ("IUPAC name", "A systematic name designed to identify the compound unambiguously."),
    "CanonicalSMILES": ("Canonical SMILES", "A text notation that encodes molecular connectivity. Different valid SMILES can represent the same structure."),
    "IsomericSMILES": ("Isomeric SMILES", "SMILES notation that can encode stereochemistry and isotopic information."),
    "XLogP": ("XLogP", "A computed estimate of the octanol/water partition coefficient; higher values generally indicate greater lipophilicity."),
    "TPSA": ("Topological polar surface area", "A calculated estimate of the polar surface area; often useful when discussing permeability and molecular polarity."),
    "HBondDonorCount": ("Hydrogen-bond donors", "Count of donor groups, such as suitable O–H or N–H groups, under the database's rules."),
    "HBondAcceptorCount": ("Hydrogen-bond acceptors", "Count of atoms that can accept a hydrogen bond under the database's rules."),
    "RotatableBondCount": ("Rotatable bonds", "An approximate count of single bonds whose rotation contributes to molecular flexibility."),
    "ExactMass": ("Exact mass", "Mass calculated from the most abundant isotopes, in unified atomic mass units (u)."),
    "Complexity": ("Structural complexity", "A database-computed descriptor; it is not a direct measure of toxicity or difficulty of synthesis."),
}
PROP_FIELDS = ",".join(PROPERTY_DESCRIPTIONS.keys())

@st.cache_data(ttl=3600, show_spinner=False)
def pubchem_lookup(name: str) -> dict:
    """Resolve a name through PubChem and retrieve its standard property record."""
    safe_name = requests.utils.quote(name.strip(), safe="")
    url = f"{PUBCHEM}/compound/name/{safe_name}/property/{PROP_FIELDS}/JSON"
    response = requests.get(url, headers=HEADERS, timeout=20)
    if response.status_code == 404:
        raise ValueError(f'PubChem could not find a compound named “{name}”. Try a common name or a PubChem CID.')
    response.raise_for_status()
    payload = response.json()
    props = payload.get("PropertyTable", {}).get("Properties", [])
    if not props:
        raise ValueError("PubChem returned no property record for this search.")
    record = props[0]
    cid = record.get("CID")
    record["CID"] = cid
    record["RequestedName"] = name.strip()
    record["PubChemURL"] = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
    return record

@st.cache_data(ttl=3600, show_spinner=False)
def pubchem_sdf(cid: int) -> str:
    """Request a 3D SDF conformer. PubChem may not have a 3D conformer for every CID."""
    url = f"{PUBCHEM}/compound/cid/{int(cid)}/SDF"
    response = requests.get(url, params={"record_type": "3d"}, headers=HEADERS, timeout=25)
    if response.status_code != 200 or not response.text.strip() or "V2000" not in response.text and "V3000" not in response.text:
        raise ValueError("A 3D conformer was not available from PubChem for this compound.")
    return response.text

def pretty(value):
    if value is None or value == "":
        return "Not available"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)

def render_viewer(sdf: str, cid: int, style: str = "stick"):
    # JSON encoding safely escapes the SDF before placing it inside JavaScript.
    sdf_js = json.dumps(sdf)
    html = f"""
    <html><head>
      <script src="https://3dmol.org/build/3Dmol-min.js"></script>
      <style>
        html,body{{margin:0;background:#0b1523;color:#c9d8e9;font-family:Arial,sans-serif;overflow:hidden}}
        #viewer{{width:100%;height:430px;position:relative;border-radius:16px;overflow:hidden}}
        .hint{{position:absolute;bottom:10px;left:14px;z-index:5;font-size:11px;letter-spacing:.04em;color:#a8bed3;background:rgba(8,15,25,.65);padding:6px 9px;border-radius:8px;pointer-events:none}}
      </style>
    </head><body>
      <div id="viewer"><div class="hint">DRAG TO ROTATE · SCROLL TO ZOOM</div></div>
      <script>
      const sdf = {sdf_js};
      const element = document.getElementById('viewer');
      const viewer = $3Dmol.createViewer(element, {{backgroundColor:'#0b1523', antialias:true}});
      viewer.addModel(sdf, 'sdf');
      viewer.setStyle({{}}, {{"stick":{{radius:0.16,colorscheme:"Jmol"}}, "sphere":{{scale:0.24,colorscheme:"Jmol"}}}});
      viewer.zoomTo();
      viewer.render();
      window.addEventListener('resize', () => viewer.resize());
      </script>
    </body></html>
    """
    components.html(html, height=445, scrolling=False)

def property_table(record):
    rows = []
    for key, (label, description) in PROPERTY_DESCRIPTIONS.items():
        rows.append({"Property": label, "Value": pretty(record.get(key)), "What it means": description})
    return pd.DataFrame(rows)

with st.sidebar:
    st.markdown("## ⚛️ Molecule Lab")
    st.markdown('<span class="tag">CHEMISTRY EXPLORER</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigate")
    page = st.radio("Workspace", ["Explore molecules", "Compare molecules", "About this project"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Data source**")
    st.markdown("[PubChem · NIH](https://pubchem.ncbi.nlm.nih.gov/)")
    st.markdown("[3Dmol.js viewer](https://3dmol.org/doc/)")
    st.caption("Educational tool. Property availability depends on each PubChem record.")

if page == "Explore molecules":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">THE MOLECULAR ATLAS · 01</div>
      <h1>Explore the building<br>blocks of everything.</h1>
      <p>Discover molecular identity, interpret chemical descriptors, and inspect three-dimensional structures in an interactive workspace powered by PubChem.</p>
    </div>
    """, unsafe_allow_html=True)

    col_search, col_btn = st.columns([4, 1])
    with col_search:
        search_name = st.text_input("Search by molecule name", value="Caffeine", placeholder="Try caffeine, ethanol, glucose…", label_visibility="collapsed")
    with col_btn:
        lookup_clicked = st.button("Explore molecule ↗", type="primary", use_container_width=True)

    st.markdown('<div class="small-muted">QUICK DISCOVERY · Choose a compound to begin</div>', unsafe_allow_html=True)
    chosen = st.pills("Popular compounds", STARTER_MOLECULES, selection_mode="single", label_visibility="collapsed") if hasattr(st, "pills") else st.selectbox("Popular compounds", ["Choose one…"] + STARTER_MOLECULES, label_visibility="collapsed")
    if chosen and chosen != "Choose one…" and not lookup_clicked:
        search_name = chosen

    if "active_molecule" not in st.session_state:
        st.session_state.active_molecule = "Caffeine"
    if lookup_clicked and search_name.strip():
        st.session_state.active_molecule = search_name.strip()
    elif chosen and chosen != "Choose one…":
        st.session_state.active_molecule = chosen

    active_name = st.session_state.active_molecule
    try:
        with st.spinner(f"Retrieving verified compound data for {active_name}…"):
            record = pubchem_lookup(active_name)
        title_name = record.get("IUPACName") or active_name
        st.markdown("---")
        left, right = st.columns([1.05, 1.15], gap="large")
        with left:
            st.markdown('<div class="section-title">Molecular identity</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="panel"><div class="eyebrow">PUBCHEM CID {record.get("CID")}</div><h2 style="margin:.5rem 0;color:#f1f6ff;font-size:1.7rem">{active_name.title()}</h2><div class="small-muted">{title_name}</div><br><span class="tag">{pretty(record.get("MolecularFormula"))}</span><span class="tag">PubChem verified record</span><br><br><div class="small-muted">Canonical SMILES</div><div style="font-family:monospace;color:#8ff8e9;overflow-wrap:anywhere;margin:.35rem 0 1rem">{pretty(record.get("CanonicalSMILES"))}</div><div class="small-muted">Isomeric SMILES</div><div style="font-family:monospace;color:#d8c5ff;overflow-wrap:anywhere;margin:.35rem 0">{pretty(record.get("IsomericSMILES"))}</div></div>', unsafe_allow_html=True)
            st.markdown("")
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f'<div class="metric"><div class="metric-label">Molecular weight</div><div class="metric-value">{pretty(record.get("MolecularWeight"))}<span style="font-size:.7rem;color:#9db0c8"> g/mol</span></div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric"><div class="metric-label">XLogP</div><div class="metric-value">{pretty(record.get("XLogP"))}</div></div>', unsafe_allow_html=True)
            st.markdown("")
            st.link_button("Open full PubChem record ↗", record["PubChemURL"], use_container_width=True)
        with right:
            st.markdown('<div class="section-title">3D molecular observatory</div>', unsafe_allow_html=True)
            try:
                sdf = pubchem_sdf(int(record["CID"]))
                render_viewer(sdf, int(record["CID"]))
                st.markdown('<div class="small-muted">Ball-and-stick model · Drag to rotate · Scroll or pinch to zoom. Coordinates are retrieved from PubChem when a 3D conformer is available.</div>', unsafe_allow_html=True)
                st.download_button("↓ Download 3D structure (.sdf)", sdf, file_name=f"pubchem_{record['CID']}.sdf", mime="chemical/x-mdl-sdfile", use_container_width=True)
            except Exception as e:
                st.warning(f"3D structure unavailable: {e}")
                st.markdown("You can still explore the compound's text properties and open its PubChem record.")
        st.markdown("---")
        st.markdown('<div class="section-title">Chemical property dossier</div>', unsafe_allow_html=True)
        df = property_table(record)
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={
            "Property": st.column_config.TextColumn(width="medium"),
            "Value": st.column_config.TextColumn(width="medium"),
            "What it means": st.column_config.TextColumn(width="large"),
        })
        export = {k: record.get(k) for k in ["CID", "RequestedName", *PROPERTY_DESCRIPTIONS.keys(), "PubChemURL"]}
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("↓ Export property dossier · CSV", pd.DataFrame([export]).to_csv(index=False), file_name=f"{active_name.lower().replace(' ','_')}_properties.csv", mime="text/csv", use_container_width=True)
        with d2:
            st.download_button("↓ Export raw record · JSON", json.dumps(export, indent=2), file_name=f"{active_name.lower().replace(' ','_')}_properties.json", mime="application/json", use_container_width=True)
        st.caption("Data retrieved from PubChem PUG REST. Computed descriptors and conformer availability can vary by compound.")
    except requests.RequestException as e:
        st.error("Could not connect to PubChem right now. Check your internet connection and try again.")
        st.caption(f"Technical detail: {e}")
    except (ValueError, KeyError, IndexError) as e:
        st.error(str(e))
    except Exception as e:
        st.error("Something went wrong while loading this compound.")
        st.caption(str(e))

elif page == "Compare molecules":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">COMPARATIVE CHEMISTRY · 02</div>
      <h1>Two molecules.<br>One clear comparison.</h1>
      <p>Compare common descriptors side by side and see how molecular composition and polarity differ.</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name1 = st.text_input("Molecule A", "Caffeine")
    with c2:
        name2 = st.text_input("Molecule B", "Theobromine")
    if st.button("Compare compounds ↗", type="primary", use_container_width=True):
        try:
            with st.spinner("Fetching both compound records from PubChem…"):
                a = pubchem_lookup(name1)
                b = pubchem_lookup(name2)
            st.markdown("---")
            a_col, b_col = st.columns(2)
            with a_col:
                st.markdown(f'<div class="panel"><div class="eyebrow">COMPOUND A · CID {a.get("CID")}</div><h2 style="color:#f1f6ff">{name1.title()}</h2><div style="font-size:1.3rem;color:#72f0e0;font-weight:800">{pretty(a.get("MolecularFormula"))}</div><div class="small-muted">{pretty(a.get("IUPACName"))}</div></div>', unsafe_allow_html=True)
            with b_col:
                st.markdown(f'<div class="panel"><div class="eyebrow">COMPOUND B · CID {b.get("CID")}</div><h2 style="color:#f1f6ff">{name2.title()}</h2><div style="font-size:1.3rem;color:#c5a4ff;font-weight:800">{pretty(b.get("MolecularFormula"))}</div><div class="small-muted">{pretty(b.get("IUPACName"))}</div></div>', unsafe_allow_html=True)
            compare_keys = ["MolecularWeight", "XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount", "RotatableBondCount", "ExactMass", "Complexity"]
            labels = [PROPERTY_DESCRIPTIONS[k][0] for k in compare_keys]
            comparison = pd.DataFrame({
                "Property": labels,
                name1.title(): [a.get(k) for k in compare_keys],
                name2.title(): [b.get(k) for k in compare_keys],
            })
            st.markdown('<div class="section-title">Descriptor comparison</div>', unsafe_allow_html=True)
            st.dataframe(comparison, use_container_width=True, hide_index=True)
            st.markdown('<div class="section-title">How to interpret this</div>', unsafe_allow_html=True)
            st.markdown("""
            - **Molecular weight** compares average mass per mole; it does not by itself predict biological activity.
            - **XLogP** is a computed estimate related to lipophilicity; it should be interpreted alongside other descriptors.
            - **TPSA** estimates polar surface area and can help frame discussions about polarity and permeability.
            - **Hydrogen-bond donors/acceptors** describe interaction potential, not a direct measurement of binding strength.
            """)
            st.download_button("↓ Download comparison · CSV", comparison.to_csv(index=False), file_name="molecule_comparison.csv", mime="text/csv", use_container_width=True)
        except Exception as e:
            st.error(f"Could not complete comparison: {e}")
    else:
        st.info("Enter two compound names, then select **Compare compounds**. Examples: caffeine and theobromine, ethanol and methanol, or glucose and fructose.")

else:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">PROJECT NOTES · 03</div>
      <h1>Science you can<br>inspect and understand.</h1>
      <p>Molecule Lab is an educational molecular exploration interface built around public chemical data.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="panel">
      <div class="section-title">Technology stack</div>
      <p><b>Streamlit</b> provides the interactive Python web application.</p>
      <p><b>PubChem PUG REST</b> supplies compound identifiers and property records from the National Library of Medicine / NIH.</p>
      <p><b>3Dmol.js</b> renders the returned SDF coordinates in an interactive WebGL molecular viewer.</p>
      <p><b>Pandas</b> prepares tabular data and CSV exports.</p>
      <hr>
      <div class="section-title">Scientific notes</div>
      <p>SMILES is a line notation, not a 3D structure. The 3D viewer uses coordinates from an available PubChem conformer. A computed conformer is one plausible geometry and should not be assumed to represent every physical environment or experimental state.</p>
      <p>Descriptors such as XLogP and TPSA are model-derived properties. They are useful for learning and comparison, but they do not independently establish safety, toxicity, efficacy, or biological behaviour.</p>
      <p>Property availability varies by compound. Missing values are shown as unavailable rather than invented.</p>
      <hr>
      <div class="small-muted">Sources: PubChem PUG REST documentation · 3Dmol.js documentation. Created as an educational project.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;color:#7f94ac;font-size:.76rem"><span>MOLECULE LAB · EDUCATIONAL CHEMISTRY EXPLORER</span><span>Data: PubChem · Visualization: 3Dmol.js</span></div>', unsafe_allow_html=True)
