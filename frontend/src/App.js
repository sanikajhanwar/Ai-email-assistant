import React, { useState, useEffect } from "react";

function App() {
  const [emailData, setEmailData] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/fetch-email") // Change if your backend is running on a different port
      .then((res) => res.json())
      .then((data) => setEmailData(data))
      .catch((err) => console.error("Error fetching emails:", err));
  }, []);

  return (
    <div>
      <h1>AI Email Assistant</h1>
      {emailData ? (
        <div>
          <h2>Sender: {emailData.sender}</h2>
          <p><strong>Date:</strong> {emailData.date}</p>
          <p><strong>Summary:</strong> {emailData.summary}</p>
          <h3>Reply Suggestions:</h3>
          <ul>
            {emailData.reply_suggestions.split("\n").map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p>Loading email data...</p>
      )}
    </div>
  );
}

export default App;
