import React from "react";

type Props = {
  title: string;
  body: string;
};

const StatementDetail = ({ title, body }: Props) => (
  <div className="border rounded p-3">
    <h3 className="text-lg font-semibold">{title}</h3>
    <p className="text-sm text-gray-600">{body}</p>
  </div>
);

export default StatementDetail;