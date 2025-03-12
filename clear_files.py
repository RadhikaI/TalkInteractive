files = {
    "front-end/src/data/scorer_output.json":'[]'  ,
    "front-end/src/data/transcript_whole.txt":"",
    "transcript_whole.json":'""',
    "extracted_claims.json":"[]",
    "transcript_chunks.json":"[]", 
    "claim-analysis/cited_claims.json":"[]", 
    "claim-analysis/scorer_output.json":"[]"
}

def clear():
    for (path, content) in files.items():
        try:
            with open(path, "w") as f:  
                f.write(content)
        except Exception as e:
            print("Error with clearing files before start.")
if __name__ == "__main__":
    clear()
