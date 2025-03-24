import React, { useEffect, useState } from "react";
import api from "@/shared/api/apiClient";

const StatementsList = () => {
  const [statements, setStatements] = useState([]);

  useEffect(() => {
    api.get("/statements/").then((res) => setStatements(res.data));
  }, []);

  return (
    <ul>
      {statements.map((s) => (
        <li key={s.id} className="p-2 border-b">
          {s.title}
        </li>
      ))}
    </ul>
  );
};

export default StatementsList;