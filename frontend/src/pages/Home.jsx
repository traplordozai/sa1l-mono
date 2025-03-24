import { Dialog, Transition } from "@headlessui/react";
import { Fragment, useState } from "react";
import Login from "./Login";
import Register from "./Register";

export default function Home() {
  const [open, setOpen] = useState(false);
  const [formType, setFormType] = useState("login");

  return (
    <div className="h-screen bg-gradient-to-br from-western-deep to-western-purple flex items-center justify-center text-white">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold">Welcome to Western Platform</h1>
        <p className="text-lg">
          Empowering student-organization success through matching.
        </p>
        <div className="flex justify-center gap-4">
          <button
            className="px-4 py-2 rounded bg-white text-purple-700 font-semibold shadow"
            onClick={() => {
              setFormType("login");
              setOpen(true);
            }}
          >
            Login
          </button>
          <button
            className="px-4 py-2 rounded bg-white text-purple-700 font-semibold shadow"
            onClick={() => {
              setFormType("register");
              setOpen(true);
            }}
          >
            Register
          </button>
        </div>
      </div>

      <Transition show={open} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={setOpen}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>
          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    {formType === "login" ? "Login" : "Register"}
                  </Dialog.Title>
                  <div className="mt-4">
                    {formType === "login" ? <Login /> : <Register />}
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}
