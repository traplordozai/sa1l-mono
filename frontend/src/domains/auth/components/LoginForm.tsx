// src/domains/auth/components/LoginForm.tsx
import React, { useState } from 'react';
import { useAuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

interface LoginFormProps {
  onModeChange?: (mode: "login" | "signup") => void;
  mode?: "login" | "signup";
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onModeChange,
  mode = "login"
}) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState<"Student" | "Faculty" | "Organization">("Student");
  const [orgName, setOrgName] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const { login, register, isLoading } = useAuthContext();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      if (mode === "login") {
        await login(email, password);
        // Navigate based on user role (handled in useAuth)
      } else {
        // Register new user
        await register({
          email,
          password,
          firstName,
          lastName,
          role,
          ...(role === "Organization" && { orgName }),
        });
        // Navigate based on user role (handled in useAuth)
      }
    } catch (error: any) {
      console.error('Authentication error:', error);

      setErrorMessage(
        error.response?.data?.detail ||
        error.response?.data?.error ||
        (mode === "login"
          ? "Invalid email or password. Please try again."
          : "Registration failed. Please try again.")
      );
    }
  };

  return (
    <div>
      {mode === "login" ? (
        <>
          <h2 className="mt-8 text-2xl font-bold tracking-tight text-gray-900">
            Sign in to your account
          </h2>
          {onModeChange && (
            <p className="mt-2 text-sm text-gray-500">
              or{" "}
              <button
                type="button"
                onClick={() => onModeChange("signup")}
                className="text-indigo-600 font-semibold hover:underline focus:outline-none"
              >
                create an account
              </button>
            </p>
          )}
        </>
      ) : (
        <>
          <h2 className="mt-8 text-2xl font-bold tracking-tight text-gray-900">
            Create a new account
          </h2>
          {onModeChange && (
            <p className="mt-2 text-sm text-gray-500">
              or{" "}
              <button
                type="button"
                onClick={() => onModeChange("login")}
                className="text-indigo-600 font-semibold hover:underline focus:outline-none"
              >
                sign in to your account
              </button>
            </p>
          )}
        </>
      )}

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-900">
            Email address
          </label>
          <div className="mt-2">
            <input
              id="email"
              name="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              pattern={role === "Student" || role === "Faculty" ? ".*@uwo\\.ca$" : undefined}
              title={role === "Student" || role === "Faculty"
                ? "Email must be a @uwo.ca address"
                : "Any valid email address"}
              className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2
                        text-gray-900 placeholder:text-gray-400
                        focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-900">
            Password
          </label>
          <div className="mt-2">
            <input
              id="password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2
                        text-gray-900 placeholder:text-gray-400
                        focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
        </div>

        {mode === "signup" && (
          <>
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-900">
                First Name
              </label>
              <div className="mt-2">
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2
                           text-gray-900 placeholder:text-gray-400
                           focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-900">
                Last Name
              </label>
              <div className="mt-2">
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2
                           text-gray-900 placeholder:text-gray-400
                           focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-900">
                Role
              </label>
              <div className="mt-2">
                <select
                  id="role"
                  name="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value as "Student" | "Faculty" | "Organization")}
                  className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2
                           text-gray-900 placeholder:text-gray-400
                           focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm"
                >
                  <option value="Student">Student</option>
                  <option value="Faculty">Faculty</option>
                  <option value="Organization">Organization</option>
                </select>
              </div>
            </div>

            {role === "Organization" && (
              <div>
                <label htmlFor="orgName" className="block text-sm font-medium text-gray-900">
                  Organization Name
                </label>
                <div className="mt-2">
                  <input
                    id="orgName"
                    name="orgName"
                    type="text"
                    required
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2
                             text-gray-900 placeholder:text-gray-400
                             focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm"
                  />
                </div>
              </div>
            )}
          </>
        )}

        {errorMessage && (
          <div className="text-red-500 bg-red-50 p-3 rounded border border-red-200 text-sm mt-2">
            {errorMessage}
          </div>
        )}

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm
                     font-semibold text-white shadow-sm hover:bg-indigo-500
                     focus-visible:outline focus-visible:outline-2
                     focus-visible:outline-offset-2 focus-visible:outline-indigo-600
                     disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading
              ? (mode === "login" ? "Signing in..." : "Creating account...")
              : (mode === "login" ? "Sign in" : "Sign up")}
          </button>
        </div>
      </form>
    </div>
  );
};