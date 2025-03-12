# Talk Interactive
### Installing Packages
- Install `Python 3.12` (https://www.python.org/downloads/release/python-3129/) 
- Install `C++ Build Tools` (https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Install `Microsoft Visual C++ Redistributable` (https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
- Install `Node.js` (https://nodejs.org/en)
- Run `pip install flask flask_cors whisper textblob requests together openai-whisper spacy`
- Run `python -m spacy download en_core_web_sm`
- Run `npm install react-scripts`

### Running the project
- Obtain a Perplexity authentication key, find the `utils.py` file in the `claim-analysis` folder, replace `key = os.getenv("PERPLEXITY_KEY")` with `key = "YOUR KEY"`
- To start the flask backend server, cd into the project folder and run `python -m flaskserver`
- To start running the UI, cd into the `front-end` folder within the project folder and run `npm start`
- If using the filtering stage after claim extraction (not default), replace `key = os.getenv("TOGETHER_KEY")` with your Together API authentication key, and uncomment the filtering subprocess in `flaskserver.py`
