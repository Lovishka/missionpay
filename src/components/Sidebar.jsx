import { useState } from "react";
import {
  LayoutDashboard,
  Target,
  Bot,
  Radio,
  Package,
  ShieldCheck,
  BarChart3,
  Settings,
  Menu,
  X,
  LogOut,
} from "lucide-react";

const menuItems = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Missions", icon: Target },
  { name: "AI Agents", icon: Bot },
  { name: "Commerce Radar", icon: Radio },
  { name: "Inventory", icon: Package },
  { name: "Approvals", icon: ShieldCheck },
  { name: "Analytics", icon: BarChart3 },
];

export default function Sidebar({
  active,
  setActive,
  onLogout,
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const merchantData = JSON.parse(
    localStorage.getItem("merchant") || "{}"
  );

  const businessName =
    merchantData.business_name || "Sakuja Traders";

  const initial =
    businessName.charAt(0).toUpperCase();

  const handleNavigation = (name) => {
    setActive(name);
    setMobileOpen(false);
  };

  return (
    <>
      {/* ================= MOBILE TOP BAR ================= */}

      <header className="lg:hidden fixed top-0 left-0 right-0 z-50 h-16 bg-[#06153f] text-white flex items-center justify-between px-4 shadow-lg">

        <div>
          <div className="text-xl font-black tracking-tight">
            MISSION<span className="text-blue-400">PAY</span>
          </div>

          <p className="text-[10px] text-blue-200">
            Local Commerce Autopilot
          </p>
        </div>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-lg hover:bg-white/10 transition"
          aria-label="Toggle navigation"
        >
          {mobileOpen ? (
            <X size={24} />
          ) : (
            <Menu size={24} />
          )}
        </button>

      </header>


      {/* ================= MOBILE OVERLAY ================= */}

      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/40"
          onClick={() => setMobileOpen(false)}
        />
      )}


      {/* ================= SIDEBAR ================= */}

      <aside
        className={`
          fixed
          left-0
          top-0
          z-50
          h-screen
          w-64
          bg-[#06153f]
          text-white
          flex
          flex-col
          transition-transform
          duration-300

          lg:translate-x-0

          ${
            mobileOpen
              ? "translate-x-0"
              : "-translate-x-full"
          }
        `}
      >

        {/* Logo */}

        <div className="px-7 py-7 border-b border-white/10">

          <div className="text-2xl font-black tracking-tight">
            MISSION<span className="text-blue-400">
              PAY
            </span>
          </div>

          <p className="text-xs text-blue-200 mt-1">
            Local Commerce Autopilot
          </p>

        </div>


        {/* Navigation */}

        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">

          {menuItems.map((item) => {

            const Icon = item.icon;
            const isActive =
              active === item.name;

            return (
              <button
                key={item.name}
                onClick={() =>
                  handleNavigation(item.name)
                }
                className={`
                  w-full
                  flex
                  items-center
                  gap-3
                  px-4
                  py-3
                  rounded-xl
                  text-sm
                  font-medium
                  transition

                  ${
                    isActive
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-900/30"
                      : "text-blue-100 hover:bg-white/10"
                  }
                `}
              >

                <Icon size={19} />

                <span>
                  {item.name}
                </span>

              </button>
            );
          })}

        </nav>


        {/* Merchant */}

        <div className="p-4 border-t border-white/10">

          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5">

            <div className="w-10 h-10 shrink-0 rounded-full bg-blue-500 flex items-center justify-center font-bold">
              {initial}
            </div>


            <div className="flex-1 min-w-0">

              <p className="text-sm font-semibold truncate">
                {businessName}
              </p>

              <p className="text-xs text-blue-200">
                Merchant Account
              </p>

            </div>


            <Settings
              size={17}
              className="text-blue-200 shrink-0"
            />

          </div>


          {/* Logout */}

          {onLogout && (
            <button
              onClick={onLogout}
              className="w-full mt-3 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-blue-100 hover:bg-red-500/20 hover:text-red-200 transition"
            >
              <LogOut size={17} />
              Sign Out
            </button>
          )}

        </div>

      </aside>
    </>
  );
}