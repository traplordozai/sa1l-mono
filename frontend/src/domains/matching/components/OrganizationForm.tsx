import React, { useState } from "react";
import api from "@/shared/api/apiClient";
import Button from "@/shared/components/button/Button";
import Input from "@/shared/components/Input/Input";

const OrganizationForm = () => {
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/organizations/", { name, description: desc });
    setName(""); setDesc("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 w-full max-w-md">
      <Input placeholder="Org Name" value={name} onChange={(e) => setName(e.target.value)} />
      <Input placeholder="Description" value={desc} onChange={(e) => setDesc(e.target.value)} />
      <Button type="submit">Create</Button>
    </form>
  );
};

export default OrganizationForm;