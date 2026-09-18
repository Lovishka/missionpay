import { Target, Clock, ArrowUpRight } from "lucide-react";

export default function MissionCard() {
  const progress = 62;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6">

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center">
              <Target size={19} />
            </div>

            <span className="text-xs font-semibold uppercase tracking-wider text-blue-600">
              Active Mission
            </span>
          </div>

          <h2 className="text-xl font-bold mt-4 text-[#071a49]">
            Achieve ₹20,000 sales today
          </h2>

          <p className="text-sm text-slate-500 mt-1">
            AI agents are working toward your business goal.
          </p>
        </div>

        <span className="px-3 py-1 rounded-full bg-green-50 text-green-600 text-xs font-semibold">
          Running
        </span>
      </div>

      {/* Revenue */}
      <div className="mt-7 flex items-end justify-between">
        <div>
          <p className="text-sm text-slate-500">
            Current Revenue
          </p>

          <p className="text-3xl font-bold text-[#071a49] mt-1">
            ₹12,400
          </p>
        </div>

        <div className="text-right">
          <p className="text-sm text-slate-500">
            Remaining
          </p>

          <p className="text-xl font-bold text-blue-600">
            ₹7,600
          </p>
        </div>
      </div>

      {/* Progress */}
      <div className="mt-5">
        <div className="flex justify-between text-xs mb-2">
          <span className="font-medium text-slate-600">
            Mission Progress
          </span>

          <span className="font-bold text-blue-600">
            {progress}%
          </span>
        </div>

        <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Bottom */}
      <div className="flex items-center justify-between mt-6 pt-5 border-t border-slate-100">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Clock size={16} />
          6 hours remaining
        </div>

        <button className="flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-700">
          View Mission
          <ArrowUpRight size={16} />
        </button>
      </div>
    </div>
  );
}