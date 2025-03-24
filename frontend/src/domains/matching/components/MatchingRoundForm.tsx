import React from "react";
import Button from "@/shared/components/button/Button";

const MatchingRoundForm = () => {
  return (
    <form className="flex flex-col gap-4 p-4 border rounded">
      <input placeholder="Matching Title" className="border px-2 py-1" />
      <Button type="submit">Create Round</Button>
    </form>
  );
};

export default MatchingRoundForm;