import React, { useState, useEffect } from 'react';
export default function UploadTab() {
  // State to hold the selected file for upload
  const [selectedFile, setSelectedFile] = useState(null);
  // State to manage loading status during file upload
  const [isUploading, setIsUploading] = useState(false);
  // State for upload success and error messages
  const [uploadMessage, setUploadMessage] = useState('');
  const [isUploadError, setIsUploadError] = useState(false);
  // States for fetching and displaying the list of movies
  const [movies, setMovies] = useState([]);
  const [isMoviesLoading, setIsMoviesLoading] = useState(false);
  const [moviesError, setMoviesError] = useState(null);
  // States for recap generation functionality
  const [generatingRecapMovieId, setGeneratingRecapMovieId] = useState(null); // Changed to ID for better tracking
  const [recapMessage, setRecapMessage] = useState('');
  const [isRecapError, setIsRecapError] = useState(false);
  // Define your API Gateway endpoint URL for file upload
  // IMPORTANT: Replace this with your actual API Gateway URL.
  const API_GATEWAY_UPLOAD_URL = 'http://localhost:8080/workflow-config-service/api/upload'; // <<< REPLACE THIS!
  // Define your REST API endpoint URL for fetching movies
  // IMPORTANT: Replace this with your actual API endpoint for fetching movies.
  const API_MOVIES_URL = 'http://localhost:8080/workflow-config-service/api/movies'; // <<< REPLACE THIS!
  // Example placeholder API (you can use this for testing if you don't have one):
  // const API_MOVIES_URL = 'https://jsonplaceholder.typicode.com/posts?_limit=5'; // This returns generic posts as an example
  // Define your API endpoint for generating movie recaps
  // IMPORTANT: Replace this with your actual API endpoint for generating recaps.
  const API_GENERATE_RECAP_URL = 'http://localhost:8080/workflow-config-service/api/recap'; // <<< REPLACE THIS!
  // Function to fetch the list of movies
  const fetchMovies = async () => {
    setIsMoviesLoading(true);
    setMoviesError(null);
    try {
      const response = await fetch(API_MOVIES_URL);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMovies(data);
    } catch (e) {
      console.error("Failed to fetch movies after upload:", e);
      setMoviesError(e.message);
    } finally {
      setIsMoviesLoading(false);
    }
  };
  // useEffect hook to fetch movies when the component mounts
  // This ensures the list is populated when the tab is first opened
  useEffect(() => {
    fetchMovies();
  }, []); // Empty dependency array means it runs once on mount
  // Event handler for when a file is selected for upload
  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setUploadMessage(''); // Clear any previous upload messages
      setIsUploadError(false);
    } else {
      setSelectedFile(null);
    }
  };
  // Event handler for the upload button click
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage('Please select a file first.');
      setIsUploadError(true);
      return;
    }
    setUploadMessage('');
    setIsUploadError(false);
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile); // 'file' should match your Lambda's expected field name
    try {
      const response = await fetch(API_GATEWAY_UPLOAD_URL, {
        method: 'POST',
        body: formData,
        // headers: { 'Authorization': 'Bearer YOUR_AUTH_TOKEN_HERE' } // Add auth if needed
      });
      if (response.ok) {
        const result = await response.json();
        setUploadMessage(`Upload successful! Response: ${JSON.stringify(result)}`);
        setSelectedFile(null); // Clear the selected file after successful upload
        // IMPORTANT: After successful upload, fetch the updated list of movies
        await fetchMovies();
      } else {
        const errorText = await response.text();
        setUploadMessage(`Upload failed: ${response.status} - ${errorText}`);
        setIsUploadError(true);
      }
    } catch (error) {
      console.error('Error during file upload:', error);
      setUploadMessage(`An error occurred during upload: ${error.message}`);
      setIsUploadError(true);
    } finally {
      setIsUploading(false);
    }
  };
  // Handler for the "Generate Recap" button click (reused from MoviesTab logic)
  const handleGenerateRecap = async (movieId, movieName) => {
    setGeneratingRecapMovieId(movieId); // Set ID for tracking loading state per button
    setRecapMessage('');
    setIsRecapError(false);
    try {
      const response = await fetch(API_GENERATE_RECAP_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // 'Authorization': 'Bearer YOUR_AUTH_TOKEN_HERE' // Add auth if needed
        },
        body: JSON.stringify({ movieId: movieId, movieName: movieName }),
      });
      if (response.ok) {
        const result = await response.json();
        setRecapMessage(`Recap generation initiated for '${movieName}'. Response: ${JSON.stringify(result)}`);
        setIsRecapError(false);
      } else {
        const errorText = await response.text();
        setRecapMessage(`Recap generation failed for '${movieName}': ${response.status} - ${errorText}`);
        setIsRecapError(true);
      }
    } catch (e) {
      console.error(`Error generating recap for '${movieName}':`, e);
      setRecapMessage(`An error occurred while generating recap for '${movieName}': ${e.message}`);
      setIsRecapError(true);
    } finally {
      setGeneratingRecapMovieId(null);
    }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-blue-200 text-gray-800 p-8 font-inter">
      <div className="container mx-auto py-12">
        <h1 className="text-5xl font-extrabold text-center mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-700 drop-shadow-lg animate-fade-in">
          Smart Recap Generator
        </h1>
        {/* Upload Section */}
        <div className="bg-white bg-opacity-80 backdrop-blur-md rounded-2xl shadow-xl p-8 mb-12 border border-blue-200
                        transform transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl">
          <h2 className="text-3xl font-bold mb-8 text-center text-blue-600">Upload a New Video</h2>
          <div className="mb-8 p-6 bg-blue-50 rounded-lg border border-blue-200 shadow-inner">
            <label htmlFor="video-upload" className="block text-lg font-medium text-gray-700 mb-4 cursor-pointer">
              Select Video File:
            </label>
            <input
              type="file"
              id="video-upload"
              onChange={handleFileChange}
              accept="video/*"
              className="block w-full text-md text-gray-600
                         file:mr-5 file:py-3 file:px-6
                         file:rounded-full file:border-0
                         file:text-md file:font-semibold
                         file:bg-gradient-to-r file:from-blue-500 file:to-indigo-600 file:text-white
                         hover:file:from-blue-600 hover:file:to-indigo-700 cursor-pointer
                         transition-all duration-300 ease-in-out transform hover:scale-105"
            />
            {selectedFile && (
              <p className="mt-4 text-sm text-gray-600">
                Selected: <span className="font-semibold text-blue-500">{selectedFile.name}</span>
              </p>
            )}
          </div>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className={`w-full py-3 px-6 rounded-full text-xl font-bold
                        transition-all duration-300 ease-in-out transform hover:scale-105
                        ${!selectedFile || isUploading
                          ? 'bg-gray-300 text-gray-600 cursor-not-allowed opacity-70'
                          : 'bg-gradient-to-r from-green-400 to-teal-500 hover:from-green-500 hover:to-teal-600 text-white shadow-lg hover:shadow-xl'
                        }`}
          >
            {isUploading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </span>
            ) : 'Upload Video'}
          </button>
          {/* Upload feedback message */}
          {uploadMessage && (
            <p className={`mt-6 text-center text-md font-medium p-3 rounded-lg
                          ${isUploadError ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
              {uploadMessage}
            </p>
          )}
        </div>
        {/* Uploaded Movies List Section */}
        <div className="bg-white bg-opacity-80 backdrop-blur-md rounded-2xl shadow-xl p-8 border border-blue-200
                        transform transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl">
          <h3 className="text-3xl font-bold mb-8 text-center text-blue-600">Your Uploaded Movies</h3>
          {/* Recap generation feedback message */}
          {recapMessage && (
            <p className={`mt-4 mb-8 text-center text-md font-medium p-3 rounded-lg
                          ${isRecapError ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
              {recapMessage}
            </p>
          )}
          {isMoviesLoading ? (
            <div className="flex justify-center items-center h-48">
              <p className="text-xl text-blue-500 animate-pulse">Loading uploaded movies...</p>
            </div>
          ) : moviesError ? (
            <div className="flex justify-center items-center h-48">
              <p className="text-xl text-red-800">Error loading movies: {moviesError}</p>
            </div>
          ) : movies.length === 0 ? (
            <p className="text-center text-gray-600 text-lg py-8">No movies uploaded yet. Upload one above!</p>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-blue-200 shadow-lg">
              <table className="min-w-full divide-y divide-blue-200">
                <thead className="bg-blue-100">
                  <tr>
                    <th className="py-4 px-6 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider rounded-tl-lg">Serial No</th>
                    <th className="py-4 px-6 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Movie Name</th>
                    <th className="py-4 px-6 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider rounded-tr-lg">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-blue-100">
                  {movies.map((movie, index) => (
                    <tr key={movie.id || index} className="hover:bg-blue-50 transition-colors duration-200 ease-in-out">
                      <td className="py-4 px-6 text-sm text-gray-700">{index + 1}</td>
                      {/* Adjust 'movie.title' or 'movie.name' based on your API response */}
                      <td className="py-4 px-6 text-sm text-gray-700 font-medium">{movie.title || movie.name || `Movie ${index + 1}`}</td>
                      <td className="py-4 px-6 text-sm">
                        <button
                          onClick={() => handleGenerateRecap(movie.id || `movie-${index}`, movie.title || movie.name || `Movie ${index + 1}`)}
                          disabled={generatingRecapMovieId === (movie.id || `movie-${index}`)} // Disable if this specific movie's recap is generating
                          className={`bg-gradient-to-r from-purple-400 to-pink-500 hover:from-purple-500 hover:to-pink-600 text-white font-semibold py-2 px-5 rounded-full
                                     shadow-md transition-all duration-300 ease-in-out transform hover:scale-105
                                     focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-75
                                     ${generatingRecapMovieId === (movie.id || `movie-${index}`) ? 'opacity-60 cursor-not-allowed' : ''}`}
                        >
                          {generatingRecapMovieId === (movie.id || `movie-${index}`) ? (
                            <span className="flex items-center justify-center">
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Generating...
                            </span>
                          ) : 'Generate Recap'}
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