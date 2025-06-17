import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import UploadTab from './components/UploadTab';
import MoviesTab from './components/MoviesTab';
import TrailersTab from './components/TrailersTab';

export default function App() {
  const [selectedTab, setSelectedTab] = useState('upload');

  const renderTab = () => {
    switch (selectedTab) {
      case 'upload':
        return <UploadTab />;
      case 'movies':
        return <MoviesTab />;
      case 'trailers':
        return <TrailersTab />;
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
      <div className="flex-1 p-4 overflow-auto">{renderTab()}</div>
    </div>
  );
}
