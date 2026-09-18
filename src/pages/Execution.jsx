import { useEffect, useState } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  LoaderCircle,
  Users,
  Tag,
  Package,
  Megaphone,
  BarChart3,
  Zap,
  Target,
} from "lucide-react";

export default function Execution({
  mission,
  onBack,
  onComplete,
}) {
  const target = mission?.target || 20000;
  const startingRevenue = mission?.current_revenue || 12400;

  const executionSteps = [
    {
      name: "Customer Agent",
      description: "Selecting relevant customers",
      result: "Customer segment prepared",
      icon: Users,
    },
    {
      name: "Offer Agent",
      description: "Applying approved offer",
      result: "Offer ready for execution",
      icon: Tag,
    },
    {
      name: "Inventory Agent",
      description: "Optimizing inventory recommendation",
      result: "Inventory action prepared",
      icon: Package,
    },
    {
      name: "Campaign Agent",
      description: "Preparing merchant campaign",
      result: "Campaign ready to launch",
      icon: Megaphone,
    },
    {
      name: "Revenue Analyst",
      description: "Monitoring mission performance",
      result: "Tracking mission outcome",
      icon: BarChart3,
    },
  ];

  const [currentStep, setCurrentStep] = useState(0);
  const [revenue, setRevenue] = useState(startingRevenue);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    if (currentStep < executionSteps.length) {
      const timer = setTimeout(() => {
        setCurrentStep((prev) => prev + 1);
      }, 1300);

      return () => clearTimeout(timer);
    }

    if (
      currentStep === executionSteps.length &&
      !completed
    ) {
      const timer = setTimeout(() => {
        // Prototype execution outcome
        const simulatedRevenue = Math.max(
          target + 650,
          startingRevenue
        );

        setRevenue(simulatedRevenue);
        setCompleted(true);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [
    currentStep,
    completed,
    target,
    startingRevenue,
    executionSteps.length,
  ]);

  const progress = Math.min(
    100,
    Math.round(
      (currentStep / executionSteps.length) * 100
    )
  );

  const amountAboveTarget = Math.max(
    revenue - target,
    0
  );

  return (
    <div className="w-full max-w-6xl mx-auto">

      {/* Back */}
      {!completed && (
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 mb-5 transition"
        >
          <ArrowLeft size={17} />
          Back to Approval
        </button>
      )}

      {/* Header */}
      <div className="text-center mb-6 sm:mb-8">

        {!completed ? (
          <>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-600 text-xs sm:text-sm font-semibold">
              <Zap size={16} />
              MissionPay is executing
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-[#071a49] mt-4 sm:mt-5">
              Executing Your Mission
            </h1>

            <p className="text-sm sm:text-base text-slate-500 mt-2">
              AI agents are coordinating actions toward your goal.
            </p>
          </>
        ) : (
          <>
            <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto rounded-full bg-green-100 text-green-600 flex items-center justify-center">
              <CheckCircle2
                size={36}
                className="sm:hidden"
              />

              <CheckCircle2
                size={42}
                className="hidden sm:block"
              />
            </div>

            <h1 className="text-3xl sm:text-4xl font-bold text-[#071a49] mt-5 sm:mt-6">
              Mission Achieved
            </h1>

            <p className="text-sm sm:text-base text-slate-500 mt-2">
              MissionPay reached your sales target.
            </p>
          </>
        )}

      </div>


      {/* Revenue */}
      <div className="bg-white border border-slate-200 rounded-2xl sm:rounded-3xl p-5 sm:p-7">

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5">

          <div>
            <p className="text-sm text-slate-500">
              Mission Revenue
            </p>

            <p className="text-3xl sm:text-4xl font-bold text-[#071a49] mt-2">
              ₹{revenue.toLocaleString("en-IN")}
            </p>
          </div>


          <div className="sm:text-right">

            <p className="text-sm text-slate-500">
              Target
            </p>

            <p className="text-xl sm:text-2xl font-bold text-blue-600">
              ₹{target.toLocaleString("en-IN")}
            </p>

            {completed && (
              <p className="text-sm font-semibold text-green-600 mt-1">
                +₹{amountAboveTarget.toLocaleString("en-IN")} above target
              </p>
            )}

          </div>

        </div>


        {/* Progress */}
        <div className="mt-6">

          <div className="flex justify-between text-xs mb-2">

            <span className="text-slate-500">
              Execution Progress
            </span>

            <span className="font-semibold text-blue-600">
              {completed ? 100 : progress}%
            </span>

          </div>

          <div className="h-2.5 sm:h-3 bg-slate-100 rounded-full overflow-hidden">

            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-700"
              style={{
                width: `${completed ? 100 : progress}%`,
              }}
            />

          </div>

        </div>

      </div>


      {/* Agent execution */}
      <div className="bg-white border border-slate-200 rounded-2xl sm:rounded-3xl p-5 sm:p-7 mt-5 sm:mt-6">

        <div className="flex items-center gap-3 mb-5 sm:mb-6">

          <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
            <Target size={20} />
          </div>

          <div>
            <h2 className="font-bold text-[#071a49]">
              Agent Execution
            </h2>

            <p className="text-xs text-slate-500">
              Coordinated actions for your mission
            </p>
          </div>

        </div>


        <div className="space-y-3 sm:space-y-4">

          {executionSteps.map((step, index) => {

            const Icon = step.icon;

            const isComplete =
              index < currentStep || completed;

            const isRunning =
              index === currentStep && !completed;

            return (
              <div
                key={step.name}
                className={`border rounded-2xl p-4 sm:p-5 transition-all duration-500 ${
                  isRunning
                    ? "border-blue-300 bg-blue-50/50"
                    : "border-slate-200"
                }`}
              >

                <div className="flex items-start sm:items-center gap-3 sm:gap-4">

                  <div
                    className={`w-10 h-10 sm:w-12 sm:h-12 shrink-0 rounded-xl flex items-center justify-center ${
                      isComplete
                        ? "bg-green-100 text-green-600"
                        : isRunning
                        ? "bg-blue-100 text-blue-600"
                        : "bg-slate-100 text-slate-400"
                    }`}
                  >

                    {isComplete ? (
                      <CheckCircle2 size={21} />
                    ) : isRunning ? (
                      <LoaderCircle
                        size={21}
                        className="animate-spin"
                      />
                    ) : (
                      <Icon size={21} />
                    )}

                  </div>


                  <div className="flex-1 min-w-0">

                    <div className="flex flex-wrap items-center gap-2">

                      <h3 className="font-semibold text-[#071a49]">
                        {step.name}
                      </h3>

                      {isComplete && (
                        <span className="text-[11px] px-2 py-1 rounded-full bg-green-50 text-green-600 font-medium">
                          Completed
                        </span>
                      )}

                      {isRunning && (
                        <span className="text-[11px] px-2 py-1 rounded-full bg-blue-50 text-blue-600 font-medium">
                          Running
                        </span>
                      )}

                    </div>

                    <p className="text-sm text-slate-500 mt-1">
                      {step.description}
                    </p>

                  </div>


                  <div className="hidden sm:block text-right max-w-[180px]">

                    <p className="text-xs text-slate-400">
                      Result
                    </p>

                    <p className="text-sm font-semibold text-[#071a49] mt-1">
                      {step.result}
                    </p>

                  </div>

                </div>


                {/* Mobile result */}
                <div className="sm:hidden ml-[52px] mt-3">

                  <p className="text-xs text-slate-400">
                    Result
                  </p>

                  <p className="text-sm font-semibold text-[#071a49] mt-1">
                    {step.result}
                  </p>

                </div>

              </div>
            );
          })}

        </div>

      </div>


      {/* Completed */}
      {completed && (
        <div className="mt-5 sm:mt-6">

          <div className="bg-[#06153f] text-white rounded-2xl sm:rounded-3xl p-6 sm:p-8 text-center">

            <p className="text-blue-200 text-xs sm:text-sm">
              FINAL MISSION OUTCOME
            </p>

            <p className="text-4xl sm:text-5xl font-black mt-3">
              ₹{revenue.toLocaleString("en-IN")}
            </p>

            <p className="text-blue-200 text-sm sm:text-base mt-2">
              ₹{target.toLocaleString("en-IN")} target achieved
            </p>


            <div className="flex flex-wrap justify-center gap-2 sm:gap-3 mt-5 sm:mt-6">

              {[
                "Goal ✓",
                "Sense ✓",
                "Plan ✓",
                "Execute ✓",
                "Outcome ✓",
              ].map((item) => (
                <div
                  key={item}
                  className="px-3 sm:px-4 py-2 rounded-xl bg-white/10 text-xs sm:text-sm"
                >
                  {item}
                </div>
              ))}

            </div>

          </div>


          <button
            onClick={onComplete}
            className="w-full mt-4 sm:mt-5 py-3.5 sm:py-4 rounded-2xl bg-blue-600 text-white font-semibold hover:bg-blue-700 transition"
          >
            Back to Dashboard
          </button>

        </div>
      )}

    </div>
  );
}