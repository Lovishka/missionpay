import {
  ArrowLeft,
  Brain,
  Users,
  Tag,
  Package,
  Megaphone,
  CheckCircle2,
  Clock3,
  Sparkles,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";
import { useEffect, useState } from "react";
import { evaluateOffer } from "../services/api";

export default function MissionControl({
  mission,
  onBack,
  onReviewApproval,
  onEvaluationComplete,
}) {

  const currentRevenue = mission?.current_revenue ?? null;

  const [evaluation, setEvaluation] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");  

  const target =
    mission?.target ??
    0;

const progress =
  target > 0 && currentRevenue !== null
    ? Math.min(
        Math.round((currentRevenue / target) * 100),
        100
      )
    : null;

const gap =
  target > 0 && currentRevenue !== null
    ? Math.max(target - currentRevenue, 0)
    : null;

const selectedProduct = evaluation?.selected_product;

const offerResponse = evaluation?.offer || {};

const offer =
  offerResponse.offer ||
  offerResponse;

const guardrails = evaluation?.guardrails;

const agents = [
  {
    name: "Demand Radar",
    icon: Brain,
    status: evaluation ? "Completed" : loading ? "Running" : "Pending",
    description: "Analyzes historical demand and inventory signals",
    result: selectedProduct
      ? `${selectedProduct.product_name} • Score ${selectedProduct.score}`
      : "Waiting for demand analysis",
  },

  {
    name: "Customer Agent",
    icon: Users,
    status: "Pending",
    description: "Identifies relevant customer segments",
    result: "Customer analysis pending",
  },

  {
    name: "Offer Agent",
    icon: Tag,
    status: offer ? "Completed" : loading ? "Running" : "Waiting",
    description: "Creates a financially valid offer",
    result: offer
      ? `${offer.discount_percentage}% off • ₹${offer.proposed_price}`
      : "Offer evaluation pending",
  },

  {
    name: "Inventory Agent",
    icon: Package,
    status: selectedProduct ? "Completed" : "Pending",
    description: "Checks product inventory",
    result: selectedProduct
      ? `${selectedProduct.current_stock} units • ${selectedProduct.stock_days} days`
      : "Inventory analysis pending",
  },

  {
    name: "Campaign Agent",
    icon: Megaphone,
    status: guardrails?.decision === "request_approval"
      ? "Waiting Approval"
      : "Pending",
    description: "Prepares campaign execution",
    result: guardrails?.decision === "request_approval"
      ? "Ready for merchant approval"
      : "Waiting for approved offer",
  },
];

   
const analyzeMission = async () => {
    const result = await evaluateOffer(mission.goal);

console.log("MISSION AI RESULT:", result);

setEvaluation(result);

if (onEvaluationComplete) {
  onEvaluationComplete(result);
}
  if (!mission?.goal) return;

  setLoading(true);
  setError("");

  try {
    const result = await evaluateOffer(mission.goal);

    console.log("MISSION AI RESULT:", result);

    setEvaluation(result);
  } catch (err) {
    console.error(err);
    setError(err.message || "Failed to analyze mission.");
  } finally {
    setLoading(false);
  }
};
 useEffect(() => {
  if (!mission?.goal) return;

  analyzeMission();
}, [mission]);
  return (
    <div className="max-w-7xl mx-auto">

      {/* Back */}

      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 mb-6"
      >
        <ArrowLeft size={17} />
        Back to Dashboard
      </button>
      


      {/* Header */}

      <div className="flex items-center justify-between mb-7">

        <div>

          <div className="flex items-center gap-2 text-blue-600 text-sm font-semibold">
            <Sparkles size={16} />
            AI Mission Control
          </div>

          <h1 className="text-3xl font-bold text-[#071a49] mt-2">
            {mission?.goal || "No mission created yet"}
          </h1>

          <p className="text-slate-500 mt-2">
            Your AI agents are coordinating actions toward your goal.
          </p>

        </div>
<button
  onClick={analyzeMission}
  disabled={loading}
  className="px-5 py-3 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50"
>
  {loading ? "Evaluating..." : "Re-run AI Analysis"}
</button>
 
        <div className="px-4 py-2 rounded-full bg-green-50 text-green-600 text-sm font-semibold">
          ● Mission Running
        </div>

      </div>


      {/* Progress */}

      <div className="bg-white border border-slate-200 rounded-2xl p-6 mb-6">

        <div className="flex justify-between items-end">

          <div>

            <p className="text-sm text-slate-500">
              Mission Progress
            </p>

           <p className="text-3xl font-bold text-[#071a49] mt-2">
  {currentRevenue !== null
    ? `₹${currentRevenue.toLocaleString("en-IN")}`
    : "Not available"}
</p>

            <p className="text-sm text-slate-500 mt-1">
              of ₹{target.toLocaleString("en-IN")} target
            </p>

          </div>


          <div className="text-right">

           <p className="text-2xl font-bold text-blue-600">
  {progress !== null ? `${progress}%` : "—"}
</p>

           <p className="text-xs text-slate-400">
  {gap !== null
    ? `₹${gap.toLocaleString("en-IN")} remaining`
    : "Live revenue data unavailable"}
</p>

          </div>

        </div>


        <div className="h-4 bg-slate-100 rounded-full mt-6 overflow-hidden">
  {progress !== null && (
    <div
      className="h-full bg-blue-600 rounded-full transition-all"
      style={{ width: `${progress}%` }}
    />
  )}
</div>


        <div className="flex justify-between mt-3 text-xs text-slate-400">

          <span>
            Mission started
          </span>

          <span>
            Goal: ₹{target.toLocaleString("en-IN")}
          </span>

        </div>

      </div>


      {/* Main */}

      <div className="grid grid-cols-3 gap-6">

{selectedProduct && (
  <div className="bg-white border border-slate-200 rounded-2xl p-6 mb-6">

    <div className="flex items-center justify-between">

      <div>
        <p className="text-sm text-slate-500">
          AI Opportunity Detected
        </p>

        <h2 className="text-2xl font-bold text-[#071a49] mt-1">
          {selectedProduct.product_name}
        </h2>

        <p className="text-sm text-slate-500 mt-1">
          {selectedProduct.reasons?.join(" ")}
        </p>
      </div>

      <div className="text-right">

        <p className="text-3xl font-bold text-blue-600">
          {selectedProduct.score}
        </p>

        <p className="text-xs text-slate-400">
          Opportunity Score
        </p>

      </div>

    </div>

    <div className="grid grid-cols-3 gap-4 mt-5">

      <div className="bg-slate-50 rounded-xl p-4">
        <p className="text-xs text-slate-500">
          Current Stock
        </p>

        <p className="text-lg font-bold text-[#071a49] mt-1">
          {selectedProduct.current_stock}
        </p>
      </div>

      <div className="bg-slate-50 rounded-xl p-4">
        <p className="text-xs text-slate-500">
          Stock Coverage
        </p>

        <p className="text-lg font-bold text-[#071a49] mt-1">
          {selectedProduct.stock_days} days
        </p>
      </div>

      <div className="bg-slate-50 rounded-xl p-4">
        <p className="text-xs text-slate-500">
          Predicted Demand
        </p>

        <p className="text-lg font-bold text-[#071a49] mt-1">
          {Math.round(
            selectedProduct.predicted_demand
          ).toLocaleString("en-IN")}
        </p>
      </div>

    </div>

  </div>
)}
        {/* Agents */}

        <div className="col-span-2 bg-white border border-slate-200 rounded-2xl p-6">

          <div className="flex items-center justify-between mb-6">

            <div>

              <h2 className="text-lg font-bold text-[#071a49]">
                AI Agent Team
              </h2>

              <p className="text-sm text-slate-500 mt-1">
                Multiple agents working toward one outcome.
              </p>

            </div>

            <span className="text-xs bg-blue-50 text-blue-600 px-3 py-1.5 rounded-full font-semibold">
              5 Agents
            </span>

          </div>


          <div className="space-y-3">

            {agents.map((agent) => {

              const Icon = agent.icon;

              const waiting =
                agent.status === "Waiting Approval" ||
                agent.status === "Waiting" ||
                agent.status === "Pending";

              return (

                <div
                  key={agent.name}
                  className="border border-slate-200 rounded-xl p-4"
                >

                  <div className="flex items-center gap-4">

                    <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">

                      <Icon size={20} />

                    </div>


                    <div className="flex-1">

                      <div className="flex items-center gap-2">

                        <h3 className="font-semibold text-[#071a49]">
                          {agent.name}
                        </h3>

                        {!waiting && (
                          <CheckCircle2
                            size={16}
                            className="text-green-500"
                          />
                        )}

                      </div>

                      <p className="text-xs text-slate-500 mt-1">
                        {agent.description}
                      </p>

                    </div>


                    <div className="text-right">

                      <span
                        className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          waiting
                            ? "bg-amber-50 text-amber-600"
                            : "bg-green-50 text-green-600"
                        }`}
                      >
                        {agent.status}
                      </span>

                      <p className="text-xs font-semibold text-[#071a49] mt-2">
                        {agent.result}
                      </p>

                    </div>

                  </div>

                </div>

              );
            })}

          </div>

        </div>


        {/* Right */}

        <div className="space-y-6">

{/* Context */}

<div className="bg-white border border-slate-200 rounded-2xl p-5">

  <h2 className="font-bold text-[#071a49]">
    Local Context
  </h2>

  <p className="text-xs text-slate-500 mt-1">
    Signals detected by MissionPay
  </p>

  <div className="space-y-3 mt-5">

    <div className="flex justify-between p-3 rounded-xl bg-slate-50">
      <span className="text-sm">
        🌡 Temperature
      </span>

      <span className="font-semibold text-sm">
        Live
      </span>
    </div>

    <div className="flex justify-between p-3 rounded-xl bg-slate-50">
      <span className="text-sm">
        📍 Nearby Events
      </span>

      <span className="font-semibold text-sm">
        Live
      </span>
    </div>

    <div className="flex justify-between p-3 rounded-xl bg-slate-50">
      <span className="text-sm">
        📈 Demand Signal
      </span>

      <span className="font-semibold text-blue-600 text-sm">
        {selectedProduct ? "AI analyzed" : "Analyzing..."}
      </span>
    </div>

  </div>

</div>
          {/* Approval */}

          <div className="bg-[#06153f] rounded-2xl p-5 text-white">

            <div className="flex items-center gap-3">

              <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">

                <ShieldCheck
                  size={20}
                  className="text-blue-300"
                />

              </div>


              <div>

                <h2 className="font-bold">
                  Approval Required
                </h2>

                <p className="text-xs text-blue-200 mt-1">
                  One action is waiting
                </p>

              </div>

            </div>


            <div className="mt-5">

  {loading && (
    <p className="text-sm text-blue-200">
      AI agents are evaluating the mission...
    </p>
  )}

  {error && (
    <p className="text-sm text-red-300">
      {error}
    </p>
  )}

  {!loading && !error && offer && (
    <>
      <p className="font-semibold text-sm">
        {offer.product_name}
      </p>

      <div className="mt-4 space-y-2 text-sm">

        <div className="flex justify-between">
          <span className="text-blue-200">
            Original price
          </span>

          <span>
            ₹{offer.original_price}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-blue-200">
            Proposed price
          </span>

          <span className="font-semibold">
            ₹{offer.proposed_price}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-blue-200">
            Discount
          </span>

          <span>
            {offer.discount_percentage}%
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-blue-200">
            Margin after
          </span>

          <span>
            {offer.margin_after}%
          </span>
        </div>

      </div>

      <p className="text-xs text-blue-200 mt-4">
        {guardrails?.reason}
      </p>
    </>
  )}

  {!loading && !error && !offer && (
    <p className="text-xs text-blue-200">
      No offer proposal is currently available.
    </p>
  )}

</div>


            <button
              onClick={onReviewApproval}
              className="w-full mt-5 bg-blue-600 hover:bg-blue-500 py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 transition"
            >

              Review Action

              <ArrowRight size={16} />

            </button>

          </div>

        </div>

      </div>


      {/* Timeline */}

      <div className="bg-white border border-slate-200 rounded-2xl p-6 mt-6">

        <h2 className="font-bold text-[#071a49]">
          Mission Timeline
        </h2>


        <div className="grid grid-cols-5 gap-4 mt-6">

          {[
           
  ["Goal", mission ? "Completed" : "Pending"],

  [
    "Sense",
    evaluation
      ? "Completed"
      : loading
      ? "Running"
      : "Pending",
  ],

  [
    "Plan",
    evaluation?.offer
      ? "Completed"
      : "Pending",
  ],

  [
    "Execute",
    guardrails?.decision === "request_approval"
      ? "Waiting"
      : "Pending",
  ],

  ["Adapt", "Pending"],
].map(([step, status]) => (
         

            <div
              key={step}
              className="relative"
            >

              <div className="flex items-center gap-3">

                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center ${
                    status === "Completed"
                      ? "bg-green-100 text-green-600"
                      : status === "Waiting"
                      ? "bg-amber-100 text-amber-600"
                      : "bg-slate-100 text-slate-400"
                  }`}
                >

                  {status === "Completed" ? (
                    <CheckCircle2 size={18} />
                  ) : (
                    <Clock3 size={18} />
                  )}

                </div>


                <div>

                  <p className="text-sm font-semibold text-[#071a49]">
                    {step}
                  </p>

                  <p className="text-xs text-slate-400">
                    {status}
                  </p>

                </div>

              </div>

            </div>

          ))}

        </div>
                
      </div>

    </div>
  );
}