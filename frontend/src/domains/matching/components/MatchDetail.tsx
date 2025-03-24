import React from "react";

type Props = {
  match: { id: number; student_id: number; organization_id: number; score: number };
};

const MatchDetail = ({ match }: Props) => {
  return (
    <div className="border rounded p-2 text-sm">
      Student #{match.student_id} → Org #{match.organization_id} [Score: {match.score}]
    </div>
  );
};

export default MatchDetail;