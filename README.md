![](https://github.com/lvermunt/spotify_analysis/workflows/Test%20package/badge.svg)
![](https://img.shields.io/github/license/lvermunt/spotify_analysis)

Package to analyse your Spotify Streaming history

This code is meant to play a bit around with coding conventions, while analysing something interesting, i.e. my Spotify's account streaming history of the last years. This can be requested in the *Extended streaming history* in [Spotify's privacy settings](https://www.spotify.com/us/account/privacy/): 

The package requires python 3.11. To install (assuming macOS here, and python 3.11 installed via brew)
```bash
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
git clone https://github.com/lvermunt/spotify_analysis.git
cd spotify_analysis
pip3 install -e .
```

Using the [`black`](https://github.com/psf/black) package to automatically format the Python code.
