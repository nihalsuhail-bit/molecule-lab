import streamlit as st
import pandas as pd
import re
import math
import requests
import json
import html as html_lib
import streamlit.components.v1 as components
from urllib.parse import quote
from collections import Counter

st.set_page_config(page_title="Chemistry Explorer | Molecule Lab", page_icon="🧪", layout="wide")

st.markdown(""" <style> .stApp{background:radial-gradient(circle at 12% 0%,#12342b 0,#0b1415 38%,#080d0f 100%);color:#e8f5ef} [data-testid="stSidebar"]{background:#0b1717;border-right:1px solid #244b40} h1,h2,h3{color:#edfff5!important;letter-spacing:-.025em} p, label, .stMarkdown{color:#cfe1d9} div[data-testid="stMetric"]{background:#101f1d;border:1px solid #285346;border-radius:14px;padding:14px} div[data-testid="stMetricLabel"]{color:#a9c8bc!important} div[data-testid="stMetricValue"]{color:#6ee7b7!important} .stButton>button,.stDownloadButton>button{background:#10b981;color:#06120e;border:0;border-radius:10px;font-weight:700} .stButton>button:hover,.stDownloadButton>button:hover{background:#34d399;color:#06120e} div[data-baseweb="select"]>div,div[data-baseweb="input"]>div,textarea{background:#101b1d!important;border-color:#2a5146!important} hr{border-color:#24463e} div[data-testid="stExpander"]{border:1px solid #25483e;border-radius:12px} .lab-card{padding:18px;border:1px solid #285346;border-radius:16px;background:linear-gradient(135deg,rgba(16,40,35,.95),rgba(13,23,25,.95));min-height:115px} .eyebrow{color:#6ee7b7;font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase} </style> """, unsafe_allow_html=True)

# Reference data: atomic masses in u; family labels are simplified educational categories.
RAW = ''' H|Hydrogen|1.008|Nonmetal;He|Helium|4.0026|Noble gas;Li|Lithium|6.94|Alkali metal;Be|Beryllium|9.0122|Alkaline earth metal;B|Boron|10.81|Metalloid;C|Carbon|12.011|Nonmetal;N|Nitrogen|14.007|Nonmetal;O|Oxygen|15.999|Nonmetal;F|Fluorine|18.998|Halogen;Ne|Neon|20.180|Noble gas;Na|Sodium|22.990|Alkali metal;Mg|Magnesium|24.305|Alkaline earth metal;Al|Aluminium|26.982|Post-transition metal;Si|Silicon|28.085|Metalloid;P|Phosphorus|30.974|Nonmetal;S|Sulfur|32.06|Nonmetal;Cl|Chlorine|35.45|Halogen;Ar|Argon|39.948|Noble gas;K|Potassium|39.098|Alkali metal;Ca|Calcium|40.078|Alkaline earth metal;Sc|Scandium|44.956|Transition metal;Ti|Titanium|47.867|Transition metal;V|Vanadium|50.942|Transition metal;Cr|Chromium|51.996|Transition metal;Mn|Manganese|54.938|Transition metal;Fe|Iron|55.845|Transition metal;Co|Cobalt|58.933|Transition metal;Ni|Nickel|58.693|Transition metal;Cu|Copper|63.546|Transition metal;Zn|Zinc|65.38|Transition metal;Ga|Gallium|69.723|Post-transition metal;Ge|Germanium|72.630|Metalloid;As|Arsenic|74.922|Metalloid;Se|Selenium|78.971|Nonmetal;Br|Bromine|79.904|Halogen;Kr|Krypton|83.798|Noble gas;Rb|Rubidium|85.468|Alkali metal;Sr|Strontium|87.62|Alkaline earth metal;Y|Yttrium|88.906|Transition metal;Zr|Zirconium|91.224|Transition metal;Nb|Niobium|92.906|Transition metal;Mo|Molybdenum|95.95|Transition metal;Tc|Technetium|98|Transition metal;Ru|Ruthenium|101.07|Transition metal;Rh|Rhodium|102.91|Transition metal;Pd|Palladium|106.42|Transition metal;Ag|Silver|107.87|Transition metal;Cd|Cadmium|112.41|Transition metal;In|Indium|114.82|Post-transition metal;Sn|Tin|118.71|Post-transition metal;Sb|Antimony|121.76|Metalloid;Te|Tellurium|127.60|Metalloid;I|Iodine|126.90|Halogen;Xe|Xenon|131.29|Noble gas;Cs|Caesium|132.91|Alkali metal;Ba|Barium|137.33|Alkaline earth metal;La|Lanthanum|138.91|Lanthanide;Ce|Cerium|140.12|Lanthanide;Pr|Praseodymium|140.91|Lanthanide;Nd|Neodymium|144.24|Lanthanide;Pm|Promethium|145|Lanthanide;Sm|Samarium|150.36|Lanthanide;Eu|Europium|151.96|Lanthanide;Gd|Gadolinium|157.25|Lanthanide;Tb|Terbium|158.93|Lanthanide;Dy|Dysprosium|162.50|Lanthanide;Ho|Holmium|164.93|Lanthanide;Er|Erbium|167.26|Lanthanide;Tm|Thulium|168.93|Lanthanide;Yb|Ytterbium|173.05|Lanthanide;Lu|Lutetium|174.97|Lanthanide;Hf|Hafnium|178.49|Transition metal;Ta|Tantalum|180.95|Transition metal;W|Tungsten|183.84|Transition metal;Re|Rhenium|186.21|Transition metal;Os|Osmium|190.23|Transition metal;Ir|Iridium|192.22|Transition metal;Pt|Platinum|195.08|Transition metal;Au|Gold|196.97|Transition metal;Hg|Mercury|200.59|Transition metal;Tl|Thallium|204.38|Post-transition metal;Pb|Lead|207.2|Post-transition metal;Bi|Bismuth|208.98|Post-transition metal;Po|Polonium|209|Post-transition metal;At|Astatine|210|Halogen;Rn|Radon|222|Noble gas;Fr|Francium|223|Alkali metal;Ra|Radium|226|Alkaline earth metal;Ac|Actinium|227|Actinide;Th|Thorium|232.04|Actinide;Pa|Protactinium|231.04|Actinide;U|Uranium|238.03|Actinide;Np|Neptunium|237|Actinide;Pu|Plutonium|244|Actinide;Am|Americium|243|Actinide;Cm|Curium|247|Actinide;Bk|Berkelium|247|Actinide;Cf|Californium|251|Actinide;Es|Einsteinium|252|Actinide;Fm|Fermium|257|Actinide;Md|Mendelevium|258|Actinide;No|Nobelium|259|Actinide;Lr|Lawrencium|266|Actinide;Rf|Rutherfordium|267|Transition metal;Db|Dubnium|268|Transition metal;Sg|Seaborgium|269|Transition metal;Bh|Bohrium|270|Transition metal;Hs|Hassium|277|Transition metal;Mt|Meitnerium|278|Transition metal;Ds|Darmstadtium|281|Transition metal;Rg|Roentgenium|282|Transition metal;Cn|Copernicium|285|Transition metal;Nh|Nihonium|286|Post-transition metal;Fl|Flerovium|289|Post-transition metal;Mc|Moscovium|290|Post-transition metal;Lv|Livermorium|293|Post-transition metal;Ts|Tennessine|294|Halogen;Og|Oganesson|294|Noble gas '''
elements=[]
for z,entry in enumerate(RAW.strip().split(';'), start=1):
    sym,name,mass,fam=entry.split('|')
    elements.append({'Atomic number':z,'Symbol':sym,'Element':name,'Atomic mass (u)':float(mass),'Family':fam})
EDF=pd.DataFrame(elements)
MASS={x['Symbol']:x['Atomic mass (u)'] for x in elements}
E_BY_SYMBOL={x['Symbol']:x for x in elements}

MOLECULES={
 'Water':('H2O','Polar molecule essential to known life.','Solvent, heat transfer, and biological chemistry.'),
 'Carbon dioxide':('CO2','Linear molecule involved in respiration and photosynthesis.','Carbon cycle, carbonation, and industrial processes.'),
 'Methane':('CH4','The simplest alkane; carbon has a tetrahedral arrangement.','Fuel and chemical feedstock.'),
 'Ammonia':('NH3','Nitrogen-containing molecule with a trigonal-pyramidal shape.','Fertilizer production and industrial chemistry.'),
 'Glucose':('C6H12O6','A simple sugar used by cells as an energy source.','Cellular respiration and metabolism.'),
 'Caffeine':('C8H10N4O2','A naturally occurring stimulant found in coffee and tea.','Common in beverages; affects alertness.'),
 'Ethanol':('C2H6O','An alcohol containing a hydroxyl group.','Solvent and fuel additive.'),
 'Benzene':('C6H6','An aromatic six-carbon ring. Benzene is carcinogenic.','Industrial feedstock; hazardous chemical.'),
 'Oxygen':('O2','A diatomic form of the element oxygen.','Cellular respiration and combustion support.'),
 'Hydrogen peroxide':('H2O2','A peroxide with an oxygen–oxygen bond.','Bleaching and disinfecting uses at suitable concentrations.'),
 'Sodium chloride':('NaCl','An ionic compound made of sodium and chloride ions.','Food seasoning and chemical manufacture.'),
 'Sulfuric acid':('H2SO4','A strong diprotic acid and important industrial chemical.','Fertilizer manufacture; highly corrosive.'),
 'Acetic acid':('C2H4O2','The acid responsible for vinegar’s characteristic acidity.','Food chemistry and chemical manufacture.'),
 'Calcium carbonate':('CaCO3','An ionic compound found in limestone, chalk, and shells.','Construction materials and antacids.'),
}

# Representative SMILES strings. For ionic compounds, disconnected ions and
# formal charges are shown explicitly. Equivalent SMILES strings may also exist.
SMILES = {
    'Water': 'O',
    'Carbon dioxide': 'O=C=O',
    'Methane': 'C',
    'Ammonia': 'N',
    'Glucose': 'C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O',
    'Caffeine': 'Cn1c(=O)c2c(ncn2C)n(C)c1=O',
    'Ethanol': 'CCO',
    'Benzene': 'c1ccccc1',
    'Oxygen': 'O=O',
    'Hydrogen peroxide': 'OO',
    'Sodium chloride': '[Na+].[Cl-]',
    'Sulfuric acid': 'OS(=O)(=O)O',
    'Acetic acid': 'CC(=O)O',
    'Calcium carbonate': '[Ca+2].[O-]C(=O)[O-]',
}

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_pubchem_compound(molecule_name):
    """Fetch current compound properties from the official PubChem PUG REST API."""
    encoded_name = quote(molecule_name, safe="")
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
        f"{encoded_name}/property/SMILES,ConnectivitySMILES,IUPACName,MolecularFormula,MolecularWeight/JSON"
    )
    try:
        response = requests.get(
            url, timeout=12, headers={"User-Agent": "ChemistryExplorer/1.0 (educational Streamlit app)"}
        )
        response.raise_for_status()
        properties = response.json().get("PropertyTable", {}).get("Properties", [])
        if not properties:
            return {"ok": False, "error": "PubChem returned no matching compound."}
        record = properties[0]
        return {"ok": True, "cid": record.get("CID"), "smiles": record.get("SMILES"),
                "connectivity_smiles": record.get("ConnectivitySMILES"),
                "iupac_name": record.get("IUPACName"), "formula": record.get("MolecularFormula"),
                "molecular_weight": record.get("MolecularWeight"),
                "source_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{record.get('CID')}"}
    except requests.RequestException as exc:
        return {"ok": False, "error": f"PubChem could not be reached right now ({type(exc).__name__})."}
    except (ValueError, KeyError, TypeError):
        return {"ok": False, "error": "PubChem returned data in an unexpected format."}

@st.cache_data(ttl=86400, show_spinner=False)
def generate_local_3d_sdf(smiles):
    """Generate 3D coordinates locally from SMILES using RDKit (no PubChem 3D API)."""
    if not smiles:
        return {"ok": False, "error": "No SMILES string is available to build this molecule."}
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError:
        return {"ok": False, "error": "The 3D chemistry engine is not installed yet. Add 'rdkit' to requirements.txt and wait for Streamlit to redeploy."}

    try:
        mol = Chem.MolFromSmiles(str(smiles))
        if mol is None:
            return {"ok": False, "error": "RDKit could not interpret the selected SMILES string."}
        mol = Chem.AddHs(mol)
        params = AllChem.ETKDGv3()
        params.randomSeed = 2026
        params.maxIterations = 1000
        embedded = AllChem.EmbedMolecule(mol, params)
        if embedded != 0:
            # Try a second deterministic embedding attempt for difficult structures.
            params.randomSeed = 42
            embedded = AllChem.EmbedMolecule(mol, params)
        if embedded != 0:
            return {"ok": False, "error": "RDKit could not generate 3D coordinates for this molecule. Try another molecule."}

        # Optimise coordinates using a molecular mechanics force field when available.
        if AllChem.MMFFHasAllMoleculeParams(mol):
            AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
        elif AllChem.UFFHasAllMoleculeParams(mol):
            AllChem.UFFOptimizeMolecule(mol, maxIters=500)

        mol_block = Chem.MolToMolBlock(mol, confId=0)
        if not mol_block or "M END" not in mol_block:
            return {"ok": False, "error": "RDKit generated coordinates, but the structure file was incomplete."}
        return {"ok": True, "sdf": mol_block + "\n$$$$\n", "dimension": "3D", "source": "RDKit local conformer generation"}
    except Exception as exc:
        return {"ok": False, "error": f"Local 3D generation failed ({type(exc).__name__}). Try another molecule."}

def render_3d_viewer(sdf, molecule_name):
    """Render an interactive 3Dmol.js structure in a Streamlit component."""
    safe_name = html_lib.escape(str(molecule_name))
    # Escape closing-script sequences before placing API data inside JavaScript.
    sdf_json = json.dumps(sdf).replace("</", "<\\/")
    viewer_html = f'''<!doctype html> <html> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <script src="https://3dmol.org/build/3Dmol-min.js"></script> <style> *{{box-sizing:border-box}} body{{margin:0;background:#0b1415;color:#d8eee5;font-family:Arial,sans-serif}} #viewer{{width:100%;height:370px;border:1px solid #285346;border-radius:14px;overflow:hidden;background:#0b1415;touch-action:pan-y}} .toolbar{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 0}} button{{background:#102a23;color:#b9f6d7;border:1px solid #2c6b55;border-radius:9px;padding:8px 12px;font-weight:700;font-size:13px;cursor:pointer}} button.active{{background:#10b981;color:#06120e;border-color:#10b981}} .note{{font-size:12px;color:#91aaa1;margin:8px 2px 0;line-height:1.45}} #error{{color:#fca5a5;padding:16px}} </style> </head> <body> <div id="viewer" aria-label="Interactive 3D molecular structure"></div> <div class="toolbar"> <button id="stick" class="active" type="button">Ball &amp; stick</button> <button id="sphere" type="button">Space-filling</button> <button id="reset" type="button">Reset view</button> </div> <div class="note">{safe_name} · Drag to rotate, pinch or scroll to zoom. Use the buttons to change the molecular display.</div> <script> (function(){{ const sdf = {sdf_json}; const el = document.getElementById('viewer'); if (!window.$3Dmol) {{ el.innerHTML='<div id="error">The 3D viewer library could not load. Check your internet connection and reload this page.</div>'; return; }} const viewer = $3Dmol.createViewer(el, {{backgroundColor:'#0b1415', antialias:true}}); viewer.addModel(sdf, 'sdf'); function setBallStick() {{ viewer.setStyle({{}}, {{stick:{{radius:0.18}}, sphere:{{scale:0.25}}}}); viewer.zoomTo(); viewer.render(); document.getElementById('stick').classList.add('active'); document.getElementById('sphere').classList.remove('active'); }} function setSpaceFill() {{ viewer.setStyle({{}}, {{sphere:{{scale:0.8}}}}); viewer.zoomTo(); viewer.render(); document.getElementById('sphere').classList.add('active'); document.getElementById('stick').classList.remove('active'); }} document.getElementById('stick').addEventListener('click', setBallStick); document.getElementById('sphere').addEventListener('click', setSpaceFill); document.getElementById('reset').addEventListener('click', function() {{ viewer.zoomTo(); viewer.render(); }}); setBallStick(); window.addEventListener('resize', function() {{ viewer.resize(); viewer.render(); }}); }})(); </script> </body> </html>'''
    components.html(viewer_html, height=435, scrolling=False)


def parse_formula(formula):
    formula=formula.strip().replace(' ','')
    if not formula: raise ValueError('Enter a chemical formula.')
    tokens=re.findall(r'[A-Z][a-z]?|\d+|[()]',formula)
    if ''.join(tokens)!=formula: raise ValueError('Use valid element symbols, subscripts as numbers, and parentheses only.')
    i=0
    def group():
        nonlocal i
        counts=Counter()
        while i<len(tokens) and tokens[i]!=')':
            if tokens[i]=='(':
                i+=1; inside=group()
                if i>=len(tokens) or tokens[i]!=')': raise ValueError('Check the parentheses in your formula.')
                i+=1; mult=1
                if i<len(tokens) and tokens[i].isdigit(): mult=int(tokens[i]); i+=1
                for s,n in inside.items(): counts[s]+=n*mult
            elif re.fullmatch(r'[A-Z][a-z]?',tokens[i]):
                s=tokens[i]; i+=1
                if s not in MASS: raise ValueError(f'Unknown element symbol: {s}')
                n=1
                if i<len(tokens) and tokens[i].isdigit(): n=int(tokens[i]); i+=1
                if n<1: raise ValueError('Subscripts must be positive integers.')
                counts[s]+=n
            else: raise ValueError('Formula format is not valid.')
        return counts
    result=group()
    if i<len(tokens) and tokens[i]==')': i+=1
    if i!=len(tokens): raise ValueError('Formula format is not valid.')
    return result

def calc_mass(formula):
    counts=parse_formula(formula)
    return sum(MASS[s]*n for s,n in counts.items()),counts

def balance_equation(equation):
    try: import sympy as sp
    except ImportError: raise ValueError('The equation balancer dependency is missing. Check requirements.txt.')
    eq=equation.replace('→','->').replace('=','->')
    if '->' not in eq: raise ValueError('Use an arrow, e.g. H2 + O2 -> H2O')
    left,right=eq.split('->',1)
    react=[x.strip() for x in left.split('+') if x.strip()]
    prod=[x.strip() for x in right.split('+') if x.strip()]
    if not react or not prod: raise ValueError('Enter reactants and products.')
    fs=react+prod; parsed=[parse_formula(x) for x in fs]
    atoms=sorted(set().union(*(p.keys() for p in parsed)))
    mat=[[p.get(a,0)*(1 if j<len(react) else -1) for j,p in enumerate(parsed)] for a in atoms]
    ns=sp.Matrix(mat).nullspace()
    if not ns: raise ValueError('No balancing solution found. Check the formulas.')
    vec=ns[0]; lcm=sp.ilcm(*[v.q for v in vec]); coeff=[int(v*lcm) for v in vec]
    if all(c<0 for c in coeff): coeff=[-c for c in coeff]
    if any(c<=0 for c in coeff): raise ValueError('Could not find positive coefficients for this equation.')
    g=math.gcd(*coeff); coeff=[c//g for c in coeff]
    fmt=lambda f,c: ('' if c==1 else str(c))+f
    return ' + '.join(fmt(f,c) for f,c in zip(react,coeff[:len(react)]))+' → '+' + '.join(fmt(f,c) for f,c in zip(prod,coeff[len(react):]))

st.sidebar.markdown('<div class="eyebrow">EMERALD LAB</div>',unsafe_allow_html=True)
st.sidebar.title('Chemistry Explorer')
page=st.sidebar.radio('Navigate',['Home','Molecule Explorer','Periodic Table','Chemistry Solver','Quiz Arena','AI Tutor'])
st.sidebar.markdown('---')
st.sidebar.caption('Explore • Calculate • Learn')

if page=='Home':
    st.markdown('<div class="eyebrow">YOUR DIGITAL CHEMISTRY WORKBENCH</div>',unsafe_allow_html=True)
    st.title('🧪 Chemistry Explorer')
    st.subheader('Explore Molecules. Understand Chemistry.')
    st.write('Discover the fascinating world of molecules, chemical structures, and the elements that make up our universe. Explore molecular formulas, learn essential chemical concepts, and build confidence through interactive tools.')
    a,b,c=st.columns(3); a.metric('Elements','118'); b.metric('Molecule profiles',len(MOLECULES)); c.metric('Learning tools','4')
    st.markdown('### Start exploring')
    c1,c2=st.columns(2)
    with c1: st.markdown('<div class="lab-card"><h3>🧬 Molecule Explorer</h3><p>Discover formulas, atom counts, molar masses, and useful facts.</p></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="lab-card"><h3>⚛️ Periodic Table</h3><p>Search all 118 elements and explore their basic properties.</p></div>',unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3: st.markdown('<div class="lab-card"><h3>🧮 Chemistry Solver</h3><p>Calculate molar mass, convert moles and grams, and balance equations.</p></div>',unsafe_allow_html=True)
    with c4: st.markdown('<div class="lab-card"><h3>🎯 Quiz Arena</h3><p>Practise key concepts with instant feedback and explanations.</p></div>',unsafe_allow_html=True)
    st.info('Choose a tool from the sidebar to begin.')

elif page=='Molecule Explorer':
    st.markdown('<div class="eyebrow">MOLECULAR REFERENCE</div>',unsafe_allow_html=True); st.title('Molecule Explorer')
    st.write('Search the molecule library and explore each compound’s formula, SMILES notation, composition, molar mass, and key facts. SMILES is a text-based way to represent molecular structures.')
    query=st.text_input('Search by molecule name or formula',placeholder='Try caffeine, H2O, or C6H12O6')
    found=[n for n,(f,_,__) in MOLECULES.items() if not query or query.lower() in n.lower() or query.lower() in f.lower()]
    if found:
        name=st.selectbox('Select a molecule',found); formula,desc,uses=MOLECULES[name]; mass,counts=calc_mass(formula)
        x,y,z=st.columns(3); x.metric('Chemical formula',formula); y.metric('Molar mass',f'{mass:.3f} g/mol'); z.metric('Total atoms',sum(counts.values()))
        st.markdown('### About this molecule'); st.write(desc); st.markdown('**Applications / context:** '+uses)
        st.markdown('### SMILES notation')
        st.caption('Molecular 3D coordinates are generated locally with RDKit; the 3D viewer does not depend on PubChem conformer downloads.')
        refresh_pubchem = st.button('Refresh compound information', key='refresh_pubchem')
        if refresh_pubchem:
            fetch_pubchem_compound.clear()
            generate_local_3d_sdf.clear()
        with st.spinner('Checking compound reference information…'):
            pubchem = fetch_pubchem_compound(name)

        live_smiles = None
        if pubchem.get('ok'):
            live_smiles = pubchem.get('smiles') or pubchem.get('connectivity_smiles')
            if live_smiles:
                st.success(f"Compound information retrieved · PubChem CID {pubchem.get('cid')}")
                st.code(live_smiles, language=None)
            else:
                st.warning('The compound lookup returned no SMILES string; the built-in reference will be used for the 3D model.')
            if pubchem.get('iupac_name'):
                st.caption('IUPAC name: ' + str(pubchem['iupac_name']))
            if pubchem.get('formula'):
                st.caption('Reference formula: ' + str(pubchem['formula']))
            if pubchem.get('molecular_weight'):
                st.caption('Reference molecular weight: ' + str(pubchem['molecular_weight']) + ' g/mol')
            st.markdown(f"[Open compound reference on PubChem]({pubchem.get('source_url')})")
        else:
            st.warning(pubchem.get('error', 'Live compound lookup is unavailable. Using the built-in molecule library where possible.'))

        smiles_for_model = live_smiles or SMILES.get(name)
        if not live_smiles and smiles_for_model:
            st.markdown('**Built-in SMILES used for the model**')
            st.code(smiles_for_model, language=None)
        st.markdown('### Interactive 3D structure')
        if smiles_for_model:
            with st.spinner('Generating a 3D conformer locally with RDKit…'):
                structure_3d = generate_local_3d_sdf(smiles_for_model)
            if structure_3d.get('ok'):
                render_3d_viewer(structure_3d['sdf'], name)
                st.caption('3D coordinates were computationally generated by RDKit from the SMILES structure. This is one plausible modelled conformer, not a claim that the molecule has only one shape.')
            else:
                st.info(structure_3d.get('error', 'A 3D model could not be generated for this molecule.'))
        else:
            st.info('No SMILES string is available to generate a 3D model for this molecule.')
        st.caption('SMILES (Simplified Molecular Input Line Entry System) encodes a molecular structure as text. Compound details may be retrieved from PubChem, but 3D coordinates are generated locally by RDKit.')
        st.markdown('### Element composition')
        comp=[]
        for s,n in counts.items(): comp.append({'Element':E_BY_SYMBOL[s]['Element'],'Symbol':s,'Number of atoms':n,'Atomic mass (u)':MASS[s],'Mass contribution (g/mol)':round(MASS[s]*n,4)})
        st.dataframe(pd.DataFrame(comp),hide_index=True,use_container_width=True)
        st.caption('Mass values are calculated from this app’s reference atomic masses. Molecular properties are educational summaries; check authoritative references for research use.')
    else: st.warning('No matching molecule in the starter library. Use Chemistry Solver to calculate a formula’s molar mass.')
    with st.expander('Browse the complete starter library'):
        st.dataframe(pd.DataFrame([{'Molecule':n,'Formula':v[0],'Built-in fallback SMILES':SMILES.get(n, 'Not available'),'Description':v[1]} for n,v in MOLECULES.items()]),hide_index=True,use_container_width=True)

elif page=='Periodic Table':
    st.markdown('<div class="eyebrow">ELEMENT REFERENCE</div>',unsafe_allow_html=True); st.title('Periodic Table')
    st.write('Search the reference list of all 118 elements. Family labels are simplified for learning.')
    a,b=st.columns([2,1])
    q=a.text_input('Search name, symbol, or atomic number',placeholder='e.g. Carbon, C, or 6')
    fam=b.selectbox('Filter by family',['All families']+sorted(EDF['Family'].unique()))
    df=EDF.copy()
    if q: df=df[df['Element'].str.contains(q,case=False,na=False)|df['Symbol'].str.contains(q,case=False,na=False)|df['Atomic number'].astype(str).eq(q.strip())]
    if fam!='All families': df=df[df['Family']==fam]
    st.dataframe(df,hide_index=True,use_container_width=True,height=380)
    selected=st.selectbox('Element details',[f"{r['Atomic number']} · {r['Symbol']} — {r['Element']}" for _,r in EDF.iterrows()])
    num=int(selected.split(' · ')[0]); row=EDF.iloc[num-1]
    x,y,z=st.columns(3); x.metric('Atomic number',int(row['Atomic number'])); y.metric('Symbol',row['Symbol']); z.metric('Atomic mass',f"{row['Atomic mass (u)']:.4g} u")
    st.write(f"**Element:** {row['Element']} \n**Family:** {row['Family']}")
    st.caption('Atomic masses for some radioactive elements are representative mass numbers. This is a compact educational reference, not a full laboratory database.')

elif page=='Chemistry Solver':
    st.markdown('<div class="eyebrow">CALCULATION DESK</div>',unsafe_allow_html=True); st.title('Chemistry Solver')
    st.write('Get transparent calculations with units and steps.')
    t1,t2,t3=st.tabs(['Molar mass','Moles ↔ grams','Balance equation'])
    with t1:
        f=st.text_input('Chemical formula',value='Ca(OH)2',key='formula_mass')
        if st.button('Calculate molar mass'):
            try:
                m,counts=calc_mass(f); st.success(f'Molar mass of {f}: **{m:.4f} g/mol**')
                rows=[{'Element':s,'Atom count':n,'Atomic mass (g/mol)':MASS[s],'Contribution (g/mol)':round(MASS[s]*n,4)} for s,n in counts.items()]
                st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
                st.write('Sum of the element contributions = **'+f'{m:.4f} g/mol**')
            except Exception as e: st.error(str(e))
    with t2:
        f2=st.text_input('Chemical formula',value='H2O',key='formula_convert')
        mode=st.radio('Known quantity',['Mass in grams','Amount in moles'],horizontal=True)
        amount=st.number_input('Value',min_value=0.0,value=18.0 if mode=='Mass in grams' else 1.0,step=0.1)
        if st.button('Convert quantity'):
            try:
                m,_=calc_mass(f2); st.metric('Molar mass',f'{m:.4f} g/mol')
                if mode=='Mass in grams': st.success(f'n = m ÷ M = {amount:g} g ÷ {m:.4f} g/mol = **{amount/m:.6g} mol**')
                else: st.success(f'm = n × M = {amount:g} mol × {m:.4f} g/mol = **{amount*m:.6g} g**')
            except Exception as e: st.error(str(e))
    with t3:
        eq=st.text_input('Unbalanced equation',value='H2 + O2 -> H2O')
        if st.button('Balance equation'):
            try: st.success(balance_equation(eq)); st.caption('Coefficients are reduced to the smallest whole-number ratio. This basic tool is not a complete ionic or redox balancer.')
            except Exception as e: st.error(str(e))

elif page=='Quiz Arena':
    st.markdown('<div class="eyebrow">KNOWLEDGE CHECK</div>',unsafe_allow_html=True); st.title('Quiz Arena')
    bank={
    'Fundamentals':[
      ('What is the SI unit for amount of substance?',['Gram','Mole','Litre','Kelvin'],1,'The mole (mol) is the SI unit for amount of substance.'),
      ('Which particle has a negative charge?',['Proton','Neutron','Electron','Nucleus'],2,'Electrons are negative, protons positive, and neutrons neutral.'),
      ('What does atomic number count?',['Neutrons','Protons','Protons + neutrons','Electron shells'],1,'Atomic number is the number of protons in the nucleus.')],
    'Molecules & formulas':[
      ('What is the formula of water?',['H2O','HO2','H2O2','OH'],0,'Water contains two hydrogen atoms and one oxygen atom.'),
      ('How many oxygen atoms are in CO2?',['1','2','3','4'],1,'The subscript 2 means there are two oxygen atoms.'),
      ('What is the approximate molar mass of CO2?',['18 g/mol','28 g/mol','44 g/mol','64 g/mol'],2,'12.01 + 2 × 16.00 ≈ 44.01 g/mol.')],
    'Periodic table':[
      ('Which element has symbol Na?',['Nitrogen','Neon','Sodium','Nickel'],2,'Na is sodium, from the Latin name natrium.'),
      ('Which family contains neon?',['Halogens','Noble gases','Alkali metals','Transition metals'],1,'Neon is a Group 18 noble gas.'),
      ('Which element has atomic number 6?',['Oxygen','Carbon','Nitrogen','Boron'],1,'Carbon has six protons.')],
    }
    topic=st.selectbox('Choose a topic',list(bank))
    with st.form('quiz'):
        answers=[]
        for i,(question,options,correct,explain) in enumerate(bank[topic]):
            st.markdown(f'**{i+1}. {question}**')
            answers.append(st.radio('Choose an answer',options,index=None,key=f'{topic}-{i}',label_visibility='collapsed'))
        submitted=st.form_submit_button('Check my answers')
    if submitted:
        score=0
        for i,((question,options,correct,explain),ans) in enumerate(zip(bank[topic],answers)):
            if ans==options[correct]: score+=1; st.success(f'{i+1}. Correct! {explain}')
            else: st.error(f'{i+1}. Correct answer: **{options[correct]}**. {explain}')
        st.metric('Your score',f'{score}/{len(bank[topic])}',f'{round(100*score/len(bank[topic]))}%')
        st.progress(score/len(bank[topic]))
        if score==len(bank[topic]): st.balloons()
        st.caption('Scores are for this session and are not permanently saved.')

elif page=='AI Tutor':
    st.markdown('<div class="eyebrow">GUIDED LEARNING</div>',unsafe_allow_html=True); st.title('AI Chemistry Tutor')
    st.write('Ask for a step-by-step explanation or practice questions. Real AI answers require an API key stored securely in Streamlit secrets.')
    try: key=st.secrets.get('OPENAI_API_KEY')
    except Exception: key=None
    question=st.text_area('What would you like help with?',placeholder='Explain molarity step by step…')
    level=st.selectbox('Explanation level',['Beginner','High-school chemistry','First-year university'])
    if st.button('Ask the tutor'):
        if not question.strip(): st.warning('Enter a question first.')
        elif not key: st.info('AI is not connected yet. The other tools work without an API key. To enable it, add OPENAI_API_KEY under Streamlit app Secrets. Never put a secret key in GitHub.')
        else:
            try:
                from openai import OpenAI
                with st.spinner('Preparing an explanation…'):
                    client=OpenAI(api_key=key)
                    response=client.chat.completions.create(model='gpt-4o-mini',messages=[{'role':'system','content':f'You are a careful chemistry tutor. Explain at {level} level, show steps and units, state assumptions, and flag safety issues.'},{'role':'user','content':question}],temperature=0.3)
                st.markdown('### Tutor response'); st.write(response.choices[0].message.content)
            except Exception: st.error('The AI request failed. Check the secret, API access, and app logs.')

st.markdown('---')
st.markdown("<div style='text-align:center;padding:18px 8px 8px'><h4 style='color:#34D399;margin-bottom:6px'>🧪 Chemistry Explorer</h4><p style='margin:3px 0'>Created by <strong>Nihal S</strong></p><p style='margin:3px 0'>AIML · SRM Institute of Science and Technology (SRM IST)</p><p style='color:#91aaa1;font-size:12px;margin-top:10px'>Exploring chemistry through technology.</p></div>",unsafe_allow_html=True)
