import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a PDF file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL || window.location.origin}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setUploadStatus(`File processed successfully with ${response.data.num_chunks} chunks`);
      setFile(null);
      // Clear the file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      setError(error.response?.data?.detail || 'Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/query', {
        query: query.trim()
      });
      setResponse(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Error processing query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PDF Question Answering System</h1>
      </header>
      
      <main className="App-main">
        <section className="upload-section">
          <h2>1. Upload PDF Document</h2>
          <div className="file-upload">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={loading}
            />
            <button 
              onClick={handleUpload}
              disabled={!file || loading}
              className={!file || loading ? 'disabled' : ''}
            >
              {loading ? 'Uploading...' : 'Upload PDF'}
            </button>
          </div>
          {uploadStatus && (
            <div className="success-message">
              {uploadStatus}
            </div>
          )}
        </section>

        <section className="query-section">
          <h2>2. Ask Questions</h2>
          <div className="query-input">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your question about the document..."
              disabled={loading || !uploadStatus}
            />
            <button
              onClick={handleQuery}
              disabled={loading || !query.trim() || !uploadStatus}
              className={loading || !query.trim() || !uploadStatus ? 'disabled' : ''}
            >
              {loading ? 'Processing...' : 'Ask Question'}
            </button>
          </div>
        </section>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {response && (
          <section className="response-section">
            <h2>Answer</h2>
            <div className="response-content">
              <p>{response.response}</p>
              
              <h3>Relevant Context</h3>
              <div className="context-list">
                {response.context.map((ctx, index) => (
                  <div key={index} className="context-item">
                    <div className="context-score">
                      Relevance: {(ctx[1] * 100).toFixed(1)}%
                    </div>
                    <div className="context-text">
                      {ctx[0]}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App; 