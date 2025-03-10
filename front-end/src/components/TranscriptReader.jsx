import React, { useEffect, useState, useMemo, useCallback, useRef } from "react";
import "./TranscriptReader.css";
import transcript from "../data/transcript_whole.txt";
import factChecks from "../data/scorer_output.json";

// function that cleans up URLs by removing the "www." at the start
function formatUrl(url) {
  try {
    const u = new URL(url);
    let hostname = u.hostname.replace(/^www\./, "");
    let path = u.pathname;
    if (path === "/" || path === "") {
      return hostname;
    } else {
      return hostname + path;
    }
  } catch (err) {
    return url;
  }
}

// helper functions for color interpolation
function hexToRgb(hex) {
  hex = hex.replace("#", "");
  if (hex.length === 3) {
    hex = hex.split("").map((c) => c + c).join("");
  }
  const bigint = parseInt(hex, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return { r, g, b };
}

function rgbToHex(r, g, b) {
  return (
    "#" +
    [r, g, b]
      .map((x) => {
        const hex = x.toString(16);
        return hex.length === 1 ? "0" + hex : hex;
      })
      .join("")
  );
}

function interpolateColor(color1, color2, factor) {
  const c1 = hexToRgb(color1);
  const c2 = hexToRgb(color2);
  const r = Math.round(c1.r + (c2.r - c1.r) * factor);
  const g = Math.round(c1.g + (c2.g - c1.g) * factor);
  const b = Math.round(c1.b + (c2.b - c1.b) * factor);
  return rgbToHex(r, g, b);
}

// function to compute a background color based on score (-100 to 100)
function getScoreColor(score) {
  if (score <= 0) {
    // for negative scores, interpolate between dark red and grey (-100 = dark red, 0 = grey)
    const factor = (score + 100) / 100; // 0 for -100, 1 for 0
    return interpolateColor("#8B0000", "#808080", factor);
  } else {
    // for positive scores, interpolate between grey and bright minty green (0 = grey, 100 = turquoise)
    const factor = score / 100; // 0 for 0, 1 for 100
    return interpolateColor("#808080", "#00FF7F", factor);
  }
}

// helper function to get the score label based on the score range
function getScoreLabel(score) {
  if (score >= -15 && score <= 15) return "Unsure";
  else if (score < -15) {
    if (score >= -49) return "Partly False";
    else if (score >= -74) return "Mostly False";
    else return "False";
  } else {
    if (score <= 49) return "Partly True";
    else if (score <= 74) return "Mostly True";
    else return "True";
  }
}

// memoised TranscriptBox to avoid unnecessary re-renders
const TranscriptBox = React.memo(({ typedLines, isStarted, handleStartClick }) => (
  <div className="transcript-box">
    <h2>Radio Transcript</h2>
    {/* if transcript hasn't started, show the "Start Transcript" button below the header */}
    {!isStarted ? (
      <div style={{ width: "100%", textAlign: "center", marginTop: "2rem" }}>
        <button className="start-btn" onClick={handleStartClick}>
          Start Transcript
        </button>
      </div>
    ) : (
      typedLines
    )}
  </div>
));

function TranscriptReader() {
  const [combinedTranscript, setCombinedTranscript] = useState("");
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // track if user has clicked the "Start Transcript" button
  const [isStarted, setIsStarted] = useState(false);
  // state to hold the vertical offset of the clicked claim (relative to transcript container)
  const [claimOffset, setClaimOffset] = useState(0);
  // state to hold the final top value for factcheck-panel
  const [factCheckTop, setFactCheckTop] = useState(0);

  const transcriptContainerRef = useRef(null);
  const factcheckPanelRef = useRef(null);

  // fetch and combine transcripts
  useEffect(() => {
    Promise.all([
      fetch(transcript).then((res) => res.text()),
    ])
      .then(([textA]) => {
        const combined = textA + "\n\n";
        setCombinedTranscript(combined);
      })
      .catch((err) => console.error("Error fetching transcripts:", err));
  }, []);

  // // reset typewriter effect if transcript changes
  // useEffect(() => {
  //   // only reset if user has clicked the start transcript button
  //   if (combinedTranscript && isStarted) {
  //     setDisplayedText("");
  //     setCurrentIndex(0);
  //   }
  // }, [combinedTranscript, isStarted]);

  // // typewriter effect
  // useEffect(() => {
  //   //only run if button is pressed (isStarted state)
  //   if (!combinedTranscript || !isStarted) return;
  //   if (currentIndex < combinedTranscript.length) {
  //     const timer = setTimeout(() => {
  //       setDisplayedText((prev) => prev + combinedTranscript[currentIndex]);
  //       setCurrentIndex((prev) => prev + 1);
  //     }, 0); // change this number to change ms per character
  //     return () => clearTimeout(timer);
  //   }
  // }, [combinedTranscript, currentIndex, isStarted]);

  // Stop typewriter effect reset on every update
useEffect(() => {
  if (isStarted && currentIndex === 0) {
    setDisplayedText("");
    setCurrentIndex(0);
  }
}, [isStarted]);

useEffect(() => {
  // only run if button is pressed (isStarted state) 
  if (!combinedTranscript || !isStarted || currentIndex >= combinedTranscript.length) return;

  const timer = setTimeout(() => {
    setDisplayedText((prev) => prev + combinedTranscript[currentIndex]);
    setCurrentIndex((prev) => prev + 1);
  }, 0); // change this number to adjust the typing speed

  return () => clearTimeout(timer);
}, [combinedTranscript, currentIndex, isStarted]);


  // split displayed text into lines
  const lines = displayedText.split("\n");

  // helper function to split segments by a claim substring
  const splitSegments = (segments, claim, claimIndex) => {
    let newSegments = [];
    for (let seg of segments) {
      if (typeof seg === "string") {
        let startIndex = 0;
        let idx = seg.indexOf(claim);
        while (idx !== -1) {
          if (idx > startIndex) {
            newSegments.push(seg.substring(startIndex, idx));
          }
          newSegments.push({ text: claim, claimIndex });
          startIndex = idx + claim.length;
          idx = seg.indexOf(claim, startIndex);
        }
        if (startIndex < seg.length) {
          newSegments.push(seg.substring(startIndex));
        }
      } else {
        newSegments.push(seg);
      }
    }
    return newSegments;
  };

  // memoised callback to process a line with inline highlights
  const renderLineWithHighlights = useCallback(
    (line, lineIndex) => {
      let segments = [line];
      factChecks.forEach((check, claimIndex) => {
        const claim = check.original_claim;
        if (claim) {
          segments = splitSegments(segments, claim, claimIndex);
        }
      });
      return (
        <p key={lineIndex}>
          {segments.map((seg, i) =>
            typeof seg === "string" ? (
              seg
            ) : (
              <span
                key={i}
                className="claim-highlight"
                onClick={(e) => {
                  // get bounding rectangles of the clicked claim and transcript container
                  const claimRect = e.target.getBoundingClientRect();
                  const containerRect = transcriptContainerRef.current.getBoundingClientRect();
                  // store the offset of the claim relative to the container
                  const offset = claimRect.top - containerRect.top;
                  setClaimOffset(offset);
                  setSelectedClaim(factChecks[seg.claimIndex]);
                }}
              >
                {seg.text}
              </span>
            )
          )}
        </p>
      );
    },
    [factChecks]
  );

  // memoise typed lines so they update only when lines change
  const typedLines = useMemo(
    () => lines.map((line, idx) => renderLineWithHighlights(line, idx)),
    [lines, renderLineWithHighlights]
  );

  // when a claim is selected, calculate the new top offset for the factcheck-panel
  // so its center aligns with the clicked claim
  useEffect(() => {
    if (selectedClaim && factcheckPanelRef.current) {
      const panelHeight = factcheckPanelRef.current.offsetHeight;
      let newTop = (claimOffset - panelHeight / 2) - 25; // adjust this value to move the box higher or lower
      if (newTop < 0) newTop = 0; // ensure it doesn't go off the top
      setFactCheckTop(newTop);
    }
  }, [selectedClaim, claimOffset]);

  // button click functionality
  const handleStartClick = async () => {
    setIsProcessing(true);
    
    try {
      const response = await fetch('http://localhost:5000/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        console.log(response)
      } else {
        console.error('Failed to start Flask');
      }
    } catch (error) {
      console.error('Error connecting to Flask server:', error);
    }
    
    setIsProcessing(false);
    setIsStarted(true);
  };

  return (
    <div className="transcript-container" ref={transcriptContainerRef}>
      <TranscriptBox
        typedLines={typedLines}
        isStarted={isStarted}
        handleStartClick={handleStartClick}
      />

      <div className="right-panel">
        {selectedClaim ? (
          <div
            className="factcheck-panel"
            ref={factcheckPanelRef}
            style={{ top: factCheckTop }}
          >
            <button
              className="close-btn"
              onClick={() => setSelectedClaim(null)}
            >
              X
            </button>
            <h3>Fact Check</h3>
            <div className="fact-check-content">
              <div className="fact-check-claim">
                <h4>Claim</h4>
                <p>{selectedClaim.original_claim}</p>
              </div>
              <div className="fact-check-response">
                <h4>Response</h4>
                <p>{selectedClaim.perplexity_response}</p>
              </div>
              {/* New Score Box */}
              <div className="fact-check-score">
                <p
                  className="score-value"
                  style={{
                    color: getScoreColor(selectedClaim.score),
                    fontWeight: "bold"
                  }}
                >
                  {getScoreLabel(selectedClaim.score)} ({selectedClaim.score})
                </p>
              </div>
              <div className="fact-check-sources">
                <h4>Sources</h4>
                <ul className="source-list">
                  {selectedClaim.citations.map((c, i) => (
                    <li key={i}>
                      <span className="source-number">{i + 1}.</span>
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link truncated"
                      >
                        {formatUrl(c.url)}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ) : (
          // this updates what it says in that right panel
          <div className="sidebar">
            <h3>Talk Interactive</h3>
            <p>
                                Click on any{" "}
                  <span style={{ color: "var(--highlight-color)" }}>
                    bold, underlined claim
                  </span>{" "}
                  to view more details.
                            </p>
            <p>Fact checks (citations) are carried out by Perplexity's Sonar model.</p>
            <p> It may take a few minutes to see a transcript. </p>

          </div>
        )}
      </div>
    </div>
  );
}

export default TranscriptReader;