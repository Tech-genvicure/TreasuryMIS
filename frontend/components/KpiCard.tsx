interface KpiCardProps {
  title: string;
  value: string;
  subtitle?: string;
  accent?: string;
}

export default function KpiCard({
  title,
  value,
  subtitle,
  accent = "#0db2aa",
}: KpiCardProps) {
  return (
    <div className="relative bg-white rounded-xl border border-gray-200 px-5 py-4 overflow-hidden">

      <div
        className="absolute left-0 top-0 bottom-0 w-1"
        style={{ backgroundColor: accent }}
      />

      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      <p className="text-2xl font-bold text-[#041E42] mt-2">
        {value}
      </p>

      {subtitle && (
        <p className="text-xs text-gray-400 mt-1">
          {subtitle}
        </p>
      )}

    </div>
  );
}