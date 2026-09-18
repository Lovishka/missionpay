export default function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconClass = "bg-blue-100 text-blue-600",
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-md transition">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 font-medium">
            {title}
          </p>

          <h3 className="text-2xl font-bold text-[#071a49] mt-2">
            {value}
          </h3>

          {subtitle && (
            <p className="text-xs text-slate-500 mt-2">
              {subtitle}
            </p>
          )}
        </div>

        {Icon && (
          <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${iconClass}`}>
            <Icon size={21} />
          </div>
        )}
      </div>
    </div>
  );
}