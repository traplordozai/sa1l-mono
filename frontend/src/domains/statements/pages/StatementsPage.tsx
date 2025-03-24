import React from "react";
import StatementsList from "../components/StatementsList";

const StatementsPage = () => (
  <div className="p-4">
    <h2 className="text-xl font-bold mb-4">All Statements</h2>
    <StatementsList />
  </div>
);

export default StatementsPage;