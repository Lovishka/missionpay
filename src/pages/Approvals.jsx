import { useState } from "react";
import { approveMissionAction } from "../services/api";

export default function Approvals({
  mission,
  evaluation,
  setActive,
}) {
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState("");

  // ---------------------------------------
  // Data received from Mission Control
  // ---------------------------------------

  const product = evaluation?.selected_product || {};

const offerResponse = evaluation?.offer || {};

const offer =
  offerResponse.offer ||
  offerResponse;

const guardrails =
  evaluation?.guardrails || {};

  const reasoning = Array.isArray(offer.reasoning)
    ? offer.reasoning
    : Array.isArray(offer.reasons)
      ? offer.reasons
      : [];

  const checks = Array.isArray(guardrails.checks)
    ? guardrails.checks
    : [];

  // ---------------------------------------
  // Approve
  // ---------------------------------------
console.log("APPROVAL PAGE DATA:", {
  evaluation,
  product,
  offer,
  guardrails,
});
  
const handleApprove = async () => {
  console.log("APPROVE BUTTON CLICKED");

  console.log("FINAL OFFER:", offer);
  console.log("FINAL PRODUCT:", product);

  if (!product?.product_id) {
    setActionError("Product information is missing.");
    return;
  }

  if (offer?.proposed_price == null) {
    setActionError("Proposed price is missing.");
    return;
  }

  try {
    setActionLoading(true);
    setActionError("");

    const result = await approveMissionAction({
      product_id: String(product.product_id),

      proposed_price: Number(
        offer.proposed_price
      ),

      discount_percentage: Number(
        offer.discount_percentage ?? 0
      ),

      decision: "approved",
    });

    console.log(
      "APPROVAL RESULT:",
      result
    );

    if (setActive) {
      setActive("Execution");
    }

  } catch (err) {

    console.error(
      "Approval error:",
      err
    );

    setActionError(
      err.message ||
      "Approval action failed."
    );

  } finally {

    setActionLoading(false);

  }
};

  // ---------------------------------------
  // Reject
  // ---------------------------------------

  const handleReject = async () => {
    if (!offer || !product) {
      setActionError("No offer proposal available.");
      return;
    }

    try {
      setActionLoading(true);
      setActionError("");

      const result = await approveMissionAction({
        product_id: product.product_id,
        proposed_price: Number(offer.proposed_price),
        discount_percentage: Number(
          offer.discount_percentage
        ),
        decision: "rejected",
      });

      console.log("REJECTION RESULT:", result);

      // Return to Mission Control
      if (setActive) {
        setActive("Mission Control");
      }

    } catch (err) {
      console.error("Rejection error:", err);

      setActionError(
        err.message || "Rejection failed."
      );
    } finally {
      setActionLoading(false);
    }
  };

  // ---------------------------------------
  // No evaluation available
  // ---------------------------------------

  if (!evaluation) {
    return (
      <div className="max-w-5xl mx-auto p-8">

        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center">

          <h2 className="text-xl font-semibold text-slate-900">
            No approval proposal available
          </h2>

          <p className="text-sm text-slate-500 mt-2">
            Run the AI mission analysis before opening the
            Approval Center.
          </p>

          <button
            onClick={() => setActive("Mission Control")}
            className="mt-6 px-5 py-3 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-500"
          >
            Back to Mission Control
          </button>

        </div>

      </div>
    );
  }

  // ---------------------------------------
  // Main UI
  // ---------------------------------------

  return (
    <div className="max-w-6xl mx-auto p-6 sm:p-8 space-y-6">

      {/* -------------------------------- */}
      {/* HEADER */}
      {/* -------------------------------- */}

      <div>

        <p className="text-sm font-semibold text-blue-600">
          MissionPay
        </p>

        <h1 className="text-3xl font-bold text-slate-900 mt-1">
          Approval Center
        </h1>

        <p className="text-sm sm:text-base text-slate-500 mt-2">
          Review AI-generated actions before execution.
        </p>

      </div>


      {/* -------------------------------- */}
      {/* APPROVAL STATUS */}
      {/* -------------------------------- */}

      <div className="border border-yellow-200 bg-yellow-50 rounded-2xl p-5">

        <div className="flex items-center gap-2">

          <div className="h-3 w-3 rounded-full bg-yellow-500" />

          <span className="font-semibold text-yellow-700 text-sm">
            APPROVAL REQUIRED
          </span>

        </div>

        <h2 className="text-lg sm:text-xl font-semibold text-slate-900 mt-2 break-words">
          {mission?.goal ||
            evaluation?.mission?.goal ||
            "Mission action requires approval"}
        </h2>

        <p className="text-sm text-yellow-700 mt-2">
          MissionPay has analyzed the available signals and
          generated a proposed action. Review the details before
          allowing execution.
        </p>

      </div>


      {/* -------------------------------- */}
      {/* RECOMMENDED ACTION */}
      {/* -------------------------------- */}

      <div className="bg-white border border-slate-200 rounded-2xl p-6">

        <div className="flex items-center justify-between mb-6">

          <div>

            <p className="text-xs uppercase tracking-wider text-blue-600 font-semibold">
              AI Recommendation
            </p>

            <h2 className="text-xl font-bold text-slate-900 mt-1">
              AI Recommended Action
            </h2>

          </div>

          <div className="px-3 py-1.5 rounded-full bg-blue-50 text-blue-600 text-xs font-semibold">
            AI Generated
          </div>

        </div>


        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">

          {/* Product */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Product
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {offer.product_name ||
                product.product_name ||
                "—"}
            </p>

          </div>


          {/* Available Stock */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Available Stock
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {offer.available_stock ??
                product.current_stock ??
                "—"}
            </p>

          </div>


          {/* Stock Coverage */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Stock Coverage
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {product.stock_days != null
                ? `${Number(product.stock_days).toFixed(1)} days`
                : "—"}
            </p>

          </div>


          {/* Original Price */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Original Price
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {offer.original_price != null
                ? `₹${Number(
                    offer.original_price
                  ).toLocaleString("en-IN")}`
                : "—"}
            </p>

          </div>


          {/* Proposed Price */}

          <div className="bg-blue-50 rounded-xl p-4">

            <p className="text-xs text-blue-600">
              Proposed Price
            </p>

            <p className="text-2xl font-bold text-blue-700 mt-1">
              {offer.proposed_price != null
                ? `₹${Number(
                    offer.proposed_price
                  ).toLocaleString("en-IN")}`
                : "—"}
            </p>

          </div>


          {/* Discount */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Discount
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {offer.discount_percentage != null
                ? `${offer.discount_percentage}%`
                : "—"}
            </p>

          </div>


          {/* Cost Price */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Cost Price
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {offer.cost_price != null
                ? `₹${Number(
                    offer.cost_price
                  ).toLocaleString("en-IN")}`
                : "—"}
            </p>

          </div>


          {/* Margin Before */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Margin Before
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {offer.margin_before != null
                ? `${offer.margin_before}%`
                : "—"}
            </p>

          </div>


          {/* Margin After */}

          <div className="bg-slate-50 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Margin After
            </p>

            <p className="text-lg font-semibold text-slate-900 mt-1">
              {offer.margin_after != null
                ? `${offer.margin_after}%`
                : "—"}
            </p>

          </div>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* PRODUCT INTELLIGENCE */}
      {/* -------------------------------- */}

      <div className="bg-white border border-slate-200 rounded-2xl p-6">

        <h2 className="text-xl font-semibold text-slate-900 mb-5">
          Product Intelligence
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

          {/* Opportunity Score */}

          <div className="border border-slate-200 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Opportunity Score
            </p>

            <p className="text-2xl font-bold text-slate-900 mt-1">
              {product.score ?? "—"}
            </p>

          </div>


          {/* Predicted Demand */}

          <div className="border border-slate-200 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Predicted Demand
            </p>

            <p className="text-2xl font-bold text-slate-900 mt-1">

              {product.predicted_demand != null
                ? Math.round(
                    product.predicted_demand
                  ).toLocaleString("en-IN")
                : "—"}

            </p>

            <p className="text-xs text-slate-400 mt-1">
              units
            </p>

          </div>


          {/* Sales Trend */}

          <div className="border border-slate-200 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Sales Trend
            </p>

            <p className="text-2xl font-bold text-slate-900 mt-1">
              {product.trend != null
                ? `${product.trend}%`
                : "—"}
            </p>

          </div>


          {/* Inventory Risk */}

          <div className="border border-slate-200 rounded-xl p-4">

            <p className="text-xs text-slate-500">
              Inventory Risk
            </p>

            <p className="text-2xl font-bold text-slate-900 mt-1 capitalize">
              {product.stock_risk || "—"}
            </p>

          </div>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* AI REASONING */}
      {/* -------------------------------- */}

      <div className="bg-white border border-slate-200 rounded-2xl p-6">

        <h2 className="text-xl font-semibold text-slate-900">
          Why MissionPay Chose This
        </h2>

        <p className="text-sm text-slate-500 mt-1 mb-5">
          Signals used by the decision pipeline.
        </p>


        {reasoning.length > 0 ? (

          <ul className="space-y-3">

            {reasoning.map((reason, index) => (

              <li
                key={index}
                className="flex items-start gap-3"
              >

                <span className="mt-1 text-blue-600 font-bold">
                  •
                </span>

                <span className="text-sm text-slate-700">
                  {reason}
                </span>

              </li>

            ))}

          </ul>

        ) : (

          <p className="text-sm text-slate-500">
            No reasoning details were returned by the
            recommendation pipeline.
          </p>

        )}

      </div>


      {/* -------------------------------- */}
      {/* GUARDRAILS */}
      {/* -------------------------------- */}

      <div className="bg-white border border-slate-200 rounded-2xl p-6">

        <div className="flex items-center justify-between mb-5">

          <div>

            <h2 className="text-xl font-semibold text-slate-900">
              Automated Guardrails
            </h2>

            <p className="text-sm text-slate-500 mt-1">
              Business rules checked before approval.
            </p>

          </div>

          <div className="px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-600 text-xs font-semibold">
            Protected
          </div>

        </div>


        <div className="space-y-3">

          {checks.length > 0 ? (

            checks.map((check, index) => {

              const passed =
                check.status === "passed";

              return (

                <div
                  key={index}
                  className="flex items-center justify-between border-b border-slate-100 pb-3"
                >

                  <span className="text-sm text-slate-700 capitalize">
                    {(check.rule || "")
                      .replaceAll("_", " ")}
                  </span>

                  <span
                    className={
                      passed
                        ? "font-semibold text-emerald-600 text-sm"
                        : "font-semibold text-red-600 text-sm"
                    }
                  >
                    {passed
                      ? "✓ PASSED"
                      : "✕ FAILED"}
                  </span>

                </div>

              );
            })

          ) : (

            <p className="text-sm text-slate-500">
              No guardrail checks returned.
            </p>

          )}

        </div>

      </div>


      {/* -------------------------------- */}
      {/* SYSTEM DECISION */}
      {/* -------------------------------- */}

      <div className="bg-slate-900 rounded-2xl p-6 text-white">

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">

          <div>

            <p className="text-xs text-slate-400 uppercase tracking-wider">
              System Decision
            </p>

            <p className="text-xl font-bold mt-2 capitalize">
              {(guardrails.decision ||
                guardrails.status ||
                "Pending"
              ).replaceAll("_", " ")}
            </p>

          </div>


          <div>

            <p className="text-xs text-slate-400 uppercase tracking-wider">
              Execution Status
            </p>

            <p className="text-xl font-bold mt-2">
              {offer.execution_status ||
                "NOT EXECUTED"}
            </p>

          </div>

        </div>


        {guardrails.reason && (

          <div className="mt-5 pt-5 border-t border-slate-700">

            <p className="text-sm text-slate-300">
              {guardrails.reason}
            </p>

          </div>

        )}

      </div>


      {/* -------------------------------- */}
      {/* ACTION ERROR */}
      {/* -------------------------------- */}

      {actionError && (

        <div className="border border-red-200 bg-red-50 rounded-xl p-4">

          <p className="text-sm font-medium text-red-700">
            {actionError}
          </p>

        </div>

      )}


      {/* -------------------------------- */}
      {/* ACTION BUTTONS */}
      {/* -------------------------------- */}

      <div className="bg-white border border-slate-200 rounded-2xl p-6">

        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">

          <button
  type="button"
  onClick={handleApprove}
  disabled={actionLoading}
  className="flex-1 px-6 py-3 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
>
  {actionLoading ? "Processing..." : "Approve & Execute"}
</button>


          <button
            onClick={handleReject}
            disabled={actionLoading}
            className="flex-1 px-6 py-3 rounded-xl border border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 disabled:opacity-50 transition"
          >
            Reject
          </button>

        </div>


        <p className="text-xs text-slate-400 text-center mt-4">
          Approval authorizes the proposed prototype action.
          External campaign execution is not performed by this
          demo.
        </p>

      </div>

    </div>
  );
}