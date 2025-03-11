import sys
import os

# Add the parent directory (transcription) to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from transcription import remove_trailing_punc 

def test_remove_trailing_punc():
    assert remove_trailing_punc("Hello World!") == ("Hello World", "!")
    assert remove_trailing_punc("Test...&^") == ("Test", "...&^")
    assert remove_trailing_punc("NoPunc") == ("NoPunc", "")
    assert remove_trailing_punc("") == ("", "")


test_remove_trailing_punc()