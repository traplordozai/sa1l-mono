import * as React from "react";

type Props = {
  children: React.ReactNode;
  onClose: () => void;
};

const Modal = ({ children, onClose }: Props) => (
  <div className="fixed inset-0 bg-black/50 flex justify-center items-center">
    <div className="bg-white p-4 rounded shadow-lg w-[400px] relative">
      <button onClick={onClose} className="absolute top-2 right-2">
        ✕
      </button>
      {children}
    </div>
  </div>
);

export default Modal;
