import {
  IndianRupee,
  TrendingUp,
  Target,
  Clock,
  ArrowUpRight,
  ShieldCheck,
} from "lucide-react";

import { useEffect, useState } from "react";
import {
  getDataSummary,
  getSalesHistory,
  getAgentActivity,
} from "../services/api";

import MetricCard from "../components/MetricCard";
import MissionCard from "../components/MissionCard";
import AgentCard from "../components/AgentCard";

export default function Dashboard({
  mission,
  setActive,
}) {
  const target = mission?.target ?? null;
  const currentRevenue = mission?.current_revenue ?? null;
  const revenueGap = mission?.revenue_gap ?? null;
  const [salesHistory, setSalesHistory] = useState([]);
  const [agents, setAgents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);

 useEffect(() => {
  async function loadDashboardData() {
    try {
      const [
        summaryData,
        historyData,
        agentData,
      ] = await Promise.all([
        getDataSummary(),
        getSalesHistory(),
        getAgentActivity(),
      ]);

      console.log(
        "REAL DATABASE SUMMARY:",
        summaryData
      );

      console.log(
        "REAL SALES HISTORY:",
        historyData
      );

      console.log(
        "REAL AGENT ACTIVITY:",
        agentData
      );

      setSummary(summaryData);
      setSalesHistory(historyData);
      setAgents(agentData.agents || []);

    } catch (error) {
      console.error(
        "Dashboard data error:",
        error
      );
    } finally {
      setLoadingSummary(false);
    }
  }

  loadDashboardData();
}, []);

  

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return "—";

    return `₹${Number(value).toLocaleString("en-IN")}`;
  };

  return (
    <div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">

        <div>
          <p className="text-sm text-slate-500">
            MissionPay Dashboard
          </p>

          <h1 className="text-3xl font-bold text-[#071a49] mt-1">
            Hi, Merchant 👋
          </h1>

          <p className="text-sm text-slate-500 mt-2">
            MissionPay is working toward your business goals.
          </p>
        </div>

        <button
          onClick={() => setActive("Create Mission")}
          className="px-5 py-3 rounded-xl bg-blue-600 text-white text-sm font-semibold shadow-lg shadow-blue-600/20 hover:bg-blue-700 transition"
        >
          + Create Mission
        </button>

      </div>

     {/* Metrics */}
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">

  <MetricCard
    title="Historical Units Sold"
    value={
      loadingSummary
        ? "..."
        : (summary?.total_units_sold ?? 0).toLocaleString("en-IN")
    }
    subtitle={
      summary
        ? `${summary.unique_products} products analyzed`
        : "Loading database data"
    }
    icon={IndianRupee}
  />

  <MetricCard
    title="Mission Target"
    value={formatCurrency(target)}
    subtitle={
      target !== null
        ? "Current mission goal"
        : "No active mission"
    }
    icon={Target}
  />

  <MetricCard
    title="Revenue Gap"
    value={formatCurrency(revenueGap)}
    subtitle={
      revenueGap !== null
        ? "Remaining to reach target"
        : "Live revenue required"
    }
    icon={TrendingUp}
    iconClass="bg-orange-100 text-orange-600"
  />

  <MetricCard
    title="Mission Status"
    value={mission?.status || "Idle"}
    subtitle={
      mission
        ? "Mission currently active"
        : "Create a mission to begin"
    }
    icon={Clock}
    iconClass="bg-purple-100 text-purple-600"
  />

</div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left */}
        <div className="lg:col-span-2">

          <MissionCard mission={mission} />


          {/* Revenue */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 mt-6">

            <div className="flex items-center justify-between">

              <div>
                <h2 className="font-bold text-[#071a49]">
  Historical Sales Volume
</h2>

                <p className="text-xs text-slate-500 mt-1">
  Monthly units sold from merchant data
</p>
              </div>

            </div>


          <div className="mt-6">

  {salesHistory.length === 0 ? (
    <div className="h-56 flex items-center justify-center border border-dashed border-slate-200 rounded-xl">
      <div className="text-center">
        <TrendingUp
          size={30}
          className="mx-auto text-slate-300 mb-3"
        />

        <p className="text-sm font-semibold text-slate-500">
          No historical sales data
        </p>

        <p className="text-xs text-slate-400 mt-1">
          Upload merchant sales data to generate analytics.
        </p>
      </div>
    </div>
  ) : (
    <>
      <div className="h-56 flex items-end gap-2 px-2">

        {salesHistory.map((item, index) => {
          const maxSales = Math.max(
            ...salesHistory.map(
              (x) => x.total_units
            )
          );

          const height =
            maxSales > 0
              ? (item.total_units / maxSales) * 100
              : 0;

          return (
            <div
              key={index}
              className="flex-1 flex flex-col justify-end"
            >

              <div
                className="bg-blue-500 rounded-t-lg hover:bg-blue-600 transition"
                style={{
                  height: `${height}%`,
                  minHeight: "4px",
                }}
                title={`${item.month}: ${item.total_units.toLocaleString("en-IN")} units`}
              />

            </div>
          );
        })}

      </div>

      <div className="flex justify-between text-xs text-slate-400 mt-3">

        {salesHistory.map((item, index) => (
          <span key={index}>
            {item.month}
          </span>
        ))}

      </div>
    </>
  )}

</div>

          </div>

        </div>


        {/* Right column */}
        <div className="space-y-6">


          {/* Agent Activity */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5">

            <div className="flex items-center justify-between mb-4">

              <div>
                <h2 className="font-bold text-[#071a49]">
                  AI Agent Activity
                </h2>

                <p className="text-xs text-slate-500 mt-1">
                  Mission intelligence pipeline
                </p>
              </div>

              <ArrowUpRight
                size={18}
                className="text-slate-400"
              />

            </div>


            <div className="space-y-1">

             {agents.length === 0 ? (
  <div className="text-sm text-slate-400 py-4">
    Loading agent activity...
  </div>
) : (
  agents.map((agent) => (
  <AgentCard
    key={agent.name}
    name={agent.name}
    status={agent.status}
    description={agent.description}
    reasoning={agent.reasoning}
  />
))
)}
            </div>

          </div>


          {/* Approval */}
          <div className="bg-[#06153f] text-white rounded-2xl p-5">

            <div className="flex items-center gap-3">

              <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">

                <ShieldCheck
                  className="text-blue-300"
                  size={20}
                />

              </div>

              <div>

                <p className="font-semibold">
                  Approval Center
                </p>

                <p className="text-xs text-blue-200 mt-1">
                  AI actions requiring merchant approval
                </p>

              </div>

            </div>


            <div className="mt-5 p-4 rounded-xl bg-white/5 border border-white/10">

              <p className="text-sm font-semibold">
                {mission
                  ? "AI action available for review"
                  : "No actions yet"}
              </p>

              <p className="text-xs text-blue-200 mt-2">
                {mission
                  ? "Review the recommendation generated for this mission."
                  : "Create a mission to generate AI recommendations."}
              </p>

            </div>


            <button
              onClick={() => setActive("Approvals")}
              disabled={!mission}
              className="w-full mt-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 py-3 rounded-xl text-sm font-semibold transition"
            >
              Review & Approve
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}