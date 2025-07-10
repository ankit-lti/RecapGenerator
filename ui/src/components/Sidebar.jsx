import React from 'react';

export default function Sidebar({ selectedTab, setSelectedTab }) {
  const tabs = ['upload', 'movies', 'trailers'];

  return (
    <div className="w-48 bg-gray-800 text-white p-4 space-y-4">
      {tabs.map(tab => (
        <button
          key={tab}
          className={`block w-full text-left px-2 py-1 rounded ${
            selectedTab === tab ? 'bg-gray-700 font-bold' : ''
          }`}
          onClick={() => setSelectedTab(tab)}
        >
          {tab.charAt(0).toUpperCase() + tab.slice(1)}
        </button>
      ))}
    </div>
  );
}
