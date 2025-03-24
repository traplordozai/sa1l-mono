import React, { useEffect, useState } from "react";
import api from "@/shared/api/apiClient";

const OrganizationList = () => {
  const [orgs, setOrgs] = useState([]);

  useEffect(() => {
    api.get("/organizations/").then((res) => setOrgs(res.data));
  }, []);

  return (
    <ul className="space-y-2">
      {orgs.map((org) => (
        <li key={org.id} className="border p-2 rounded">
          <strong>{org.name}</strong> — {org.description}
        </li>
      ))}
    </ul>
  );
};

export default OrganizationList;