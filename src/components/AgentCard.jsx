export default function AgentCard({
  name,
  status,
  description,
  reasoning,
}) {

  const statusClass = {
    Completed: "text-emerald-400",
    Ready: "text-blue-400",
    Waiting: "text-slate-400",
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5">

      <div className="flex items-center justify-between">

        <div>
          <h3 className="text-white font-semibold">
            {name}
          </h3>

          <p className="text-xs text-slate-500 mt-1">
            {description}
          </p>
        </div>

        <span
          className={`text-xs font-medium ${
            statusClass[status] || "text-slate-400"
          }`}
        >
          {status}
        </span>

      </div>

      {reasoning && (
        <div className="mt-4 bg-slate-950 rounded-xl p-3">

          <p className="text-[11px] uppercase tracking-wider text-slate-500">
            Agent Output
          </p>

          <p className="text-sm text-slate-300 mt-1">
            {reasoning}
          </p>

        </div>
      )}

    </div>
  );
}