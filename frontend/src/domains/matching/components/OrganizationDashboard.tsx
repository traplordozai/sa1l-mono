import React from "react";
import OrganizationList from "./OrganizationList";

const OrganizationDashboard = () => {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Organizations</h2>
      <OrganizationList />
    </div>
  );
};

export default OrganizationDashboard;