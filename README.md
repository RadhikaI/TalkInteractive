# Talk Interactive
### Installing Packages
- Make sure `Python 3.12` is installed (not compatible with 3.13) 
- Make sure `C++ Build Tools` is installed (https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Run `pip3 install -r requirements.txt`

[[
- Run `pip install flask flask_cors whisper textblob requests together openai-whisper spacy` and then `python -m spacy download en_core_web_sm`
]]

### Running the project
- Start flask server by running `python -m flaskserver` 
- cd into the `front-end` folder and run `npm start`