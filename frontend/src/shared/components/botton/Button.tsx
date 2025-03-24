import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement>;

const Button = ({ children, ...rest }: Props) => (
  <button className="bg-blue-600 text-white py-2 px-4 rounded" {...rest}>
    {children}
  </button>
);

export default Button;