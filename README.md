# Molecule Lab — Chemistry Explorer

A Streamlit chemistry learning app featuring:
- PubChem compound lookup and real chemical property records
- Interactive 3D SDF viewer powered by 3Dmol.js
- Searchable starter molecule list
- Explanations for common chemical descriptors
- CSV and JSON property downloads; SDF structure download
- Two-compound descriptor comparison

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Publish for free with Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and this README.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select your repository, branch, and `app.py`.
4. Deploy and wait for the app URL to become available.
5. Open the public `*.streamlit.app` link on your phone and test it before submitting.

## Data and visualization

- Compound properties and SDF records: PubChem PUG REST, National Library of Medicine / NIH.
- Molecular visualization: 3Dmol.js (loaded from its public CDN).
- This app requires internet access to retrieve chemical records and load the viewer.
- PubChem may not provide a 3D conformer for every compound. The app reports this rather than fabricating coordinates.
- Public hosting and upstream APIs can occasionally be slow; test the deployment before the deadline.

## Academic note

Credit PubChem and 3Dmol.js in your submission. This is an educational exploration tool, not a substitute for authoritative safety or clinical evaluation.
