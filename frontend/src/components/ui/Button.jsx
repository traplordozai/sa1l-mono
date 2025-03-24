export default function Button({ children, onClick, type = 'button', className = '' }) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={\`bg-western-purple text-white py-2 px-4 rounded-xl shadow hover:bg-orchid transition \${className}\`}
    >
      {children}
    </button>
  );
}