import React, { useState, useEffect } from 'react';
export default function TrailersTab() {
  // State to store the list of trailers fetched from the API
  const [trailers, setTrailers] = useState([]);
  // State to manage the loading status for the initial data fetch
  const [isLoading, setIsLoading] = useState(true);
  // State to store any error messages during the initial data fetch
  const [error, setError] = useState(null);
  // State to track loading status for individual download actions
  const [downloadingTrailerId, setDownloadingTrailerId] = useState(null);
  // State for download-specific messages (success/failure)
  const [downloadMessage, setDownloadMessage] = useState('');
  const [isDownloadError, setIsDownloadError] = useState(false);
  // Define your REST API endpoint URL for fetching trailers
  // IMPORTANT: Replace this with your actual API endpoint for fetching trailers.
  const API_TRAILERS_LIST_URL = 'http://localhost:8080/workflow-config-service/api/movies'; // <<< REPLACE THIS!
  // Example placeholder API (you can use this for testing if you don't have one):
  // const API_TRAILERS_LIST_URL = 'https://jsonplaceholder.typicode.com/todos?_limit=5'; // Returns generic todos as an example
  // Define your REST API endpoint URL for initiating a trailer download
  // This API might return a direct download URL or a confirmation.
  // IMPORTANT: Replace this with your actual API endpoint for downloading trailers.
  const API_TRAILER_DOWNLOAD_URL = 'http://localhost:8080/workflow-config-service/api/download'; // <<< REPLACE THIS!
  // Example: 'https://your-api-gateway-id.execute-api.region.amazonaws.com/prod/download-trailer';
  // useEffect hook to fetch data when the component mounts
  useEffect(() => {
    const fetchTrailers = async () => {
      try {
        const response = await fetch(API_TRAILERS_LIST_URL);
        // Check if the network response was successful
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Assuming your API returns an array of trailer objects,
        // and each object has an 'id' and a 'name' or 'title' property.
        // Adjust 'trailer.title' and 'trailer.id' accordingly if your API structure differs.
        setTrailers(data);
      } catch (e) {
        // Catch any errors during the fetch operation (e.g., network issues)
        console.error("Failed to fetch trailers:", e);
        setError(e.message);
      } finally {
        // Set loading to false once the fetch is complete, regardless of success or failure
        setIsLoading(false);
      }
    };
    fetchTrailers();
  }, []); // The empty dependency array ensures this effect runs only once after the initial render
  // Handler for the "Download" button click
  const handleDownload = async (trailerId, trailerName) => {
    setDownloadingTrailerId(trailerId); // Set the ID of the trailer being downloaded
    setDownloadMessage(''); // Clear previous messages
    setIsDownloadError(false); // Clear previous error state
    try {
      // Make the API call to initiate the download.
      // We pass both trailerId and trailerName in the request body.
      const response = await fetch(API_TRAILER_DOWNLOAD_URL+trailerName, {
        method: 'POST', // Typically POST for actions that trigger a process or get a resource
        headers: {
          'Content-Type': 'application/json',
          // Add authentication headers if your API requires it:
          // 'Authorization': 'Bearer YOUR_AUTH_TOKEN_HERE'
        },
        body: JSON.stringify({ trailerId: trailerId, trailerName: trailerName }),
      });
      if (response.ok) {
        // Assuming the API returns a JSON object with a download URL or a success message
        const result = await response.json();
        setDownloadMessage(`Download initiated for '${trailerName}'.`);
        setIsDownloadError(false);
        // If the API directly returns a download URL, you can open it:
        if (result.downloadUrl) {
          window.open(result.downloadUrl, '_blank');
        } else {
          console.log("Download API response (no direct URL found):", result);
          setDownloadMessage(`Download for '${trailerName}' process started. Check your downloads or API response.`);
        }
      } else {
        const errorText = await response.text();
        setDownloadMessage(`Failed to download '${trailerName}': ${response.status} - ${errorText}`);
        setIsDownloadError(true);
      }
    } catch (e) {
      console.error(`Error downloading trailer '${trailerName}':`, e);
      setDownloadMessage(`An error occurred while trying to download '${trailerName}': ${e.message}`);
      setIsDownloadError(true);
    } finally {
      setDownloadingTrailerId(null); // Reset downloading state
    }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-blue-200 text-gray-800 p-8 font-inter">
      <div className="container mx-auto py-12">
        <h1 className="text-5xl font-extrabold text-center mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-700 drop-shadow-lg animate-fade-in">
          Smart Recap Generator
        </h1>
        {/* Trailers List Section */}
        <div className="bg-white bg-opacity-80 backdrop-blur-md rounded-2xl shadow-xl p-8 border border-blue-200
                        transform transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl">
          <h2 className="text-3xl font-bold mb-8 text-center text-blue-600">Trailers List</h2>
          {/* Download feedback message */}
          {downloadMessage && (
            <p className={`mt-4 mb-8 text-center text-md font-medium p-3 rounded-lg
                          ${isDownloadError ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
              {downloadMessage}
            </p>
          )}
          {isLoading ? (
            <div className="flex justify-center items-center h-48">
              <p className="text-xl text-blue-500 animate-pulse">Loading trailers...</p>
            </div>
          ) : error ? (
            <div className="flex justify-center items-center h-48">
              <p className="text-xl text-red-800">Error loading trailers: {error}</p>
            </div>
          ) : trailers.length === 0 ? (
            <p className="text-center text-gray-600 text-lg py-8">No trailers found. Try checking your API endpoint.</p>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-blue-200 shadow-lg">
              <table className="min-w-full divide-y divide-blue-200">
                <thead className="bg-blue-100">
                  <tr>
                    <th className="py-4 px-6 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider rounded-tl-lg">Sequence</th>
                    <th className="py-4 px-6 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Trailer Name</th>
                    <th className="py-4 px-6 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider rounded-tr-lg">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-blue-100">
                  {trailers.map((trailer, index) => (
                    // Use a unique ID for the key if available from your API (e.g., trailer.id)
                    <tr key={trailer.id || index} className="hover:bg-blue-50 transition-colors duration-200 ease-in-out">
                      <td className="py-4 px-6 text-sm text-gray-700">{index + 1}</td>
                      {/*
                        IMPORTANT: Replace 'trailer.title' with the actual property name
                        from your API response that holds the trailer's name/title.
                        Common names are 'name', 'title', 'trailerName', etc.
                      */}
                      <td className="py-4 px-6 text-sm text-gray-700 font-medium">{trailer.title || trailer.name || `Trailer ${index + 1}`}</td>
                      <td className="py-4 px-6 text-sm">
                        <button
                          // Pass both the trailer's ID (for the API call) and name (for messages)
                          onClick={() => handleDownload(trailer.id || `trailer-${index}`, trailer.title || trailer.name || `Trailer ${index + 1}`)}
                          disabled={downloadingTrailerId === (trailer.id || `trailer-${index}`)} // Disable if this specific trailer is downloading
                          className={`bg-gradient-to-r from-blue-400 to-cyan-500 hover:from-blue-500 hover:to-cyan-600 text-white font-semibold py-2 px-5 rounded-full
                                     shadow-md transition-all duration-300 ease-in-out transform hover:scale-105
                                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75
                                     ${downloadingTrailerId === (trailer.id || `trailer-${index}`) ? 'opacity-60 cursor-not-allowed' : ''}`}
                        >
                          {downloadingTrailerId === (trailer.id || `trailer-${index}`) ? (
                            <span className="flex items-center justify-center">
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Downloading...
                            </span>
                          ) : 'Download'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}