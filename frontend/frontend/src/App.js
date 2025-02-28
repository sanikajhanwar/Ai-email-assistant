import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [emailData, setEmailData] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/emails")
      .then((response) => {
        setEmailData(response.data);
      })
      .catch((error) => {
        console.error("Error fetching emails:", error);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold">📩 AI Email Assistant</h1>
      <div className="mt-6 w-3/4 bg-white p-4 shadow-lg rounded-lg">
        {emailData.length > 0 ? (
          emailData.map((email, index) => (
            <div key={index} className="p-4 border-b">
              <h2 className="font-semibold">{email.sender}</h2>
              <p>{email.summary}</p>
            </div>
          ))
        ) : (
          <p>Loading emails...</p>
        )}
      </div>
    </div>
  );
}

export default App;
