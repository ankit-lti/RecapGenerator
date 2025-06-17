import React, { useState, useEffect } from 'react';
export default function MoviesTab() {
  // State to store the list of movies fetched from the API
  const [movies, setMovies] = useState([]);
  // State to manage the loading status for the initial data fetch
  const [isLoading, setIsLoading] = useState(true);
  // State to store any error messages during the initial data fetch
  const [error, setError] = useState(null);
  // States for recap generation functionality
  const [generatingRecapMovieId, setGeneratingRecapMovieId] = useState(null);
  const [recapMessage, setRecapMessage] = useState('');
  const [isRecapError, setIsRecapError] = useState(false);
  // Define your REST API endpoint URL for fetching movies
  // IMPORTANT: Replace this with your actual API endpoint for fetching movies.
  const API_MOVIES_URL = 'http://localhost:8080/workflow-config-service/api/movies'; // <<< REPLACE THIS!
  // Example placeholder API (you can use this for testing if you don't have one):
  // const API_MOVIES_URL = 'https://jsonplaceholder.typicode.com/posts?_limit=5'; // This returns generic posts as an example
  // Define your API endpoint for generating movie recaps
  // IMPORTANT: Replace this with your actual API endpoint for generating recaps.
  const API_GENERATE_RECAP_URL = 'http://localhost:8080/workflow-config-service/api/recap'; // <<< REPLACE THIS!
  // useEffect hook to fetch data when the component mounts
  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch(API_MOVIES_URL);
        // Check if the network response was successful
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Assuming your API returns an array of movie objects,
        // and each object has a 'name' or 'title' property.
        // If your API's structure is different, adjust 'movie.title' and 'movie.id' accordingly.
        setMovies(data);
      } catch (e) {
        // Catch any errors during the fetch operation (e.g., network issues)
        console.error("Failed to fetch movies:", e);
        setError(e.message);
      } finally {
        // Set loading to false once the fetch is complete, regardless of success or failure
        setIsLoading(false);
      }
    };
    fetchMovies();
  }, []); // The empty dependency array ensures this effect runs only once after the initial render
  // Handler for the "Generate Recap" button click
  const handleGenerateRecap = async (movieId, movieName) => {
    setGeneratingRecapMovieId(movieId); // Set ID for tracking loading state per button
    setRecapMessage(''); // Clear previous messages
    setIsRecapError(false); // Clear previous error state
    try {
      // Make the API call to generate the recap
      const response = await fetch(API_GENERATE_RECAP_URL, {
        method: 'POST', // Typically POST for actions like this
        headers: {
          'Content-Type': 'application/json',
          // Add authentication headers if your API requires it:
          // 'Authorization': 'Bearer YOUR_AUTH_TOKEN_HERE'
        },
        // Send the movie name (and potentially ID) in the request body
        body: JSON.stringify({ movieId: movieId, movieName: movieName }),
      });
      if (response.ok) {
        const result = await response.json(); // Parse the JSON response from your API
        setRecapMessage(`Recap generation initiated for '${movieName}'. Response: ${JSON.stringify(result)}`);
        setIsRecapError(false);
        // You might want to update a list of generated recaps or trigger a refresh elsewhere
      } else {
        const errorText = await response.text(); // Get response body as text for error details
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
        {/* Movies List Section */}
        <div className="bg-white bg-opacity-80 backdrop-blur-md rounded-2xl shadow-xl p-8 border border-blue-200
                        transform transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl">
          <h2 className="text-3xl font-bold mb-8 text-center text-blue-600">Movies List</h2>
          {/* Recap generation feedback message */}
          {recapMessage && (
            <p className={`mt-4 mb-8 text-center text-md font-medium p-3 rounded-lg
                          ${isRecapError ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
              {recapMessage}
            </p>
          )}
          {isLoading ? (
            <div className="flex justify-center items-center h-48">
              <p className="text-xl text-blue-500 animate-pulse">Loading movies...</p>
            </div>
          ) : error ? (
            <div className="flex justify-center items-center h-48">
              <p className="text-xl text-red-800">Error loading movies: {error}</p>
            </div>
          ) : movies.length === 0 ? (
            <p className="text-center text-gray-600 text-lg py-8">No movies found. Try checking your API endpoint.</p>
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