# examgen
Simple multiple choice exam generation tool.


## Setup
```
git clone https://github.com/cericyeh/examgen.git
cd examgen
python -m spacy download en_core_web_sm
```
## Usage
   ```python -m examgen.bin.generate $SOURCE_FPATH```

where $SOURCE_FPATH is the filepath to the text file used to generate questions. 

## Notes
Currently this supports Cloze-style questions over named entities.

Future extensions:
- Questions generated from copula, appositives, and possessives.
- Date ranges and numeric value quizzes.