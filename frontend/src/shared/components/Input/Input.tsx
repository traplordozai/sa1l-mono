import React from "react";

type Props = React.InputHTMLAttributes<HTMLInputElement>;

const Input = (props: Props) => {
  return <input className="border px-3 py-2 rounded" {...props} />;
};

export default Input;