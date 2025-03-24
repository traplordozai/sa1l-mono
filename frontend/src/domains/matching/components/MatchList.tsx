// MatchList.tsx
import React, { useEffect, useState } from "react";
import api from "@/shared/api/apiClient";
import MatchDetail from "./MatchDetail";

const MatchList = () => {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    api.get("/matches/").then((res) => setMatches(res.data));
  }, []);

  return (
    <div className="space-y-2">
      {matches.map((match: any) => (
        <MatchDetail key={match.id} match={match} />
      ))}
    </div>
  );
};

export default MatchList;