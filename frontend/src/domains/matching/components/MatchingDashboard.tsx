import React from "react";
import MatchList from "./MatchList";

const MatchingDashboard = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Matching Dashboard</h1>
      <MatchList />
    </div>
  );
};

export default MatchingDashboard;