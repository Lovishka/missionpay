import { useState } from "react";
import { Target, ArrowRight } from "lucide-react";
import { createMission } from "../services/api";

export default function CreateMission({ onMissionCreated, setActive }) {
  const [goal, setGoal] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCreateMission = async () => {
    if (!goal.trim()) {
      setError("Please enter a business goal.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await createMission(goal);

      console.log("MISSION CREATED:", data);

      onMissionCreated(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to create mission.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">

      <button
        onClick={() => setActive("Dashboard")}
        className="text-sm text-slate-500 hover:text-blue-600 mb-6"
      >
        ← Back to Dashboard
      </button>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8">

        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
            <Target className="text-blue-600" size={24} />
          </div>

          <div>
            <h1 className="text-2xl font-bold text-[#071a49]">
              Create a Mission
            </h1>

            <p className="text-sm text-slate-500 mt-1">
              Tell MissionPay what business outcome you want.
            </p>
          </div>
        </div>

        <label className="block text-sm font-semibold text-slate-700 mb-2">
          What do you want to achieve?
        </label>

        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="Example: Mujhe aaj ₹20,000 ki sales karni hain."
          rows={5}
          className="w-full border border-slate-300 rounded-xl p-4 outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />

        {goal && (
          <div className="mt-4 bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-xs text-blue-600 font-semibold">
              MISSION PREVIEW
            </p>

            <p className="text-sm text-slate-700 mt-2">
              {goal}
            </p>
          </div>
        )}

        {error && (
          <p className="text-sm text-red-600 mt-4">
            {error}
          </p>
        )}

        <button
          onClick={handleCreateMission}
          disabled={loading}
          className="mt-6 w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-3.5 rounded-xl font-semibold transition"
        >
          {loading ? "Creating Mission..." : "Create Mission"}

          {!loading && <ArrowRight size={18} />}
        </button>

      </div>
    </div>
  );
}