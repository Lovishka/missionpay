import { useState } from "react";

import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import CreateMission from "./pages/CreateMission";
import MissionControl from "./pages/MissionControl";
import Approvals from "./pages/Approvals";
import Execution from "./pages/Execution";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("token")
  );

  const [active, setActive] = useState("Dashboard");
  const [mission, setMission] = useState(null);
  const [missionEvaluation, setMissionEvaluation] = useState(null);

  const handleLogin = () => {
    setIsLoggedIn(true);
    setActive("Dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("merchant");

    setIsLoggedIn(false);
    setMission(null);
    setActive("Dashboard");
  };

  const handleMissionCreated = (newMission) => {
    setMission(newMission);
    setActive("Mission Control");
  };

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-slate-50">

      <Sidebar
        active={active}
        setActive={setActive}
        onLogout={handleLogout}
      />

      <main className="min-h-screen pt-16 lg:pt-0 lg:ml-64">

        <div className="w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6">

          {/* DASHBOARD */}
          {active === "Dashboard" && (
            <Dashboard
             mission={mission}
              setActive={setActive}
             
            />
          )}

          {/* CREATE MISSION */}
          {active === "Create Mission" && (
            <CreateMission
              onMissionCreated={handleMissionCreated}
              setActive={setActive}
            />
          )}

          {/* MISSION CONTROL */}
          <MissionControl
  mission={mission}
  onBack={() => setActive("Dashboard")}
  onReviewApproval={() => setActive("Approvals")}
  onEvaluationComplete={setMissionEvaluation}
/>

          {/* APPROVALS */}
          {active === "Approvals" && (
  <Approvals
    mission={mission}
    evaluation={missionEvaluation}
    setActive={setActive}
  />
)}

          {/* EXECUTION */}
          {active === "Execution" && (
            <Execution
              mission={mission}
              onBack={() => setActive("Approvals")}
              onComplete={() => setActive("Dashboard")}
            />
          )}

        </div>

      </main>
    </div>
  );
}

export default App;