import React, { useEffect, useState, useMemo, useCallback } from "react";
import "./TranscriptReader.css";
import transcriptA from "../data/TestTranscript-A.txt";
import transcriptB from "../data/TestTranscript-B.txt";
import transcriptC from "../data/TestTranscript-C.txt";
import transcriptD from "../data/RecentTranscript.txt";
import factChecks from "../data/formatted.json";

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

// memoised TranscriptBox to avoid unnecessary re-renders
const TranscriptBox = React.memo(({ typedLines }) => (
  <div className="transcript-box">
    <h2>Radio Transcript</h2>
    {typedLines}
  </div>
));

function TranscriptReader() {
  const [combinedTranscript, setCombinedTranscript] = useState("");
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedClaim, setSelectedClaim] = useState(null);

  // fetch and combine transcripts
  useEffect(() => {
    Promise.all([
      fetch(transcriptA).then((res) => res.text()),
      fetch(transcriptB).then((res) => res.text()),
      fetch(transcriptC).then((res) => res.text()),
      fetch(transcriptD).then((res) => res.text()),
    ])
      .then(([textA, textB, textC, textD]) => {
        const combined = textA + "\n\n" + textB + "\n\n" + textC + "\n\n" + textD;
        setCombinedTranscript(combined);
      })
      .catch((err) => console.error("Error fetching transcripts:", err));
  }, []);

  // reset typewriter effect if transcript changes
  useEffect(() => {
    if (combinedTranscript) {
      setDisplayedText("");
      setCurrentIndex(0);
    }
  }, [combinedTranscript]);

  // typewriter effect
  useEffect(() => {
    if (!combinedTranscript) return;
    if (currentIndex < combinedTranscript.length) {
      const timer = setTimeout(() => {
        setDisplayedText((prev) => prev + combinedTranscript[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, 2); // change this number to change ms per character
      return () => clearTimeout(timer);
    }
  }, [combinedTranscript, currentIndex]);

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
                onClick={() => setSelectedClaim(factChecks[seg.claimIndex])}
              >
                {seg.text}
              </span>
            )
          )}
        </p>
      );
    },
    []
  );

  // memoise typed lines so they update only when lines change
  const typedLines = useMemo(
    () => lines.map((line, idx) => renderLineWithHighlights(line, idx)),
    [lines, renderLineWithHighlights]
  );

  return (
    <div className="transcript-container">
      <TranscriptBox typedLines={typedLines} />

      <div className="right-panel">
        {selectedClaim ? (
          <div className="factcheck-panel">
            <button className="close-btn" onClick={() => setSelectedClaim(null)}>
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
        ) : ( // this updates what it says in that right panel
          <div className="sidebar">
            <h3>Talk Interactive</h3> 
            <p>
              Click on any{" "}
              <span style={{ color: "var(--highlight-color)" }}>
                bold, underlined claim
              </span>{" "}
              to view more details.
            </p>
            <p>
              Fact checks are carried out by Perplexity AI.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default TranscriptReader;