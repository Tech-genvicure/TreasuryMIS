
"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Table2,
  LogOut,
  ChevronRight,
  Landmark,
} from "lucide-react";
import { removeToken } from "@/lib/auth";

const navigation = [
  {
    label: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Financial Records",
    href: "/spreadsheet",
    icon: Table2,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    removeToken();
    router.push("/login");
  }

  return (
    <aside className="flex h-screen w-[248px] shrink-0 flex-col border-r border-white/5 bg-[#14263D] text-white">

      {/* BRAND */}
      <div className="flex h-[88px] items-center border-b border-white/10 px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#C4A66A]/50 bg-[#C4A66A]/10">
            <Landmark size={21} className="text-[#D8BD88]" />
          </div>

          <div>
            <h1 className="text-[17px] font-semibold tracking-wide text-white">
              Genvicure
            </h1>
            <p className="mt-0.5 text-[10px] font-medium uppercase tracking-[2px] text-[#C4A66A]">
              Treasury MIS
            </p>
          </div>
        </div>
      </div>

      {/* NAVIGATION */}
      <div className="px-4 pt-8">
        <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[1.8px] text-white/35">
          Workspace
        </p>

        <nav className="space-y-1">
          {navigation.map((item) => {
            const active = pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));

            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`group relative flex h-[46px] items-center gap-3 rounded-lg px-3 transition-all duration-200 ${
                  active
                    ? "bg-white/10 text-[#E3C98F]"
                    : "text-white/65 hover:bg-white/5 hover:text-white"
                }`}
              >
                {active && (
                  <span className="absolute left-0 top-2.5 h-[26px] w-[3px] rounded-r-full bg-[#C4A66A]" />
                )}

                <Icon
                  size={18}
                  strokeWidth={active ? 2 : 1.7}
                  className={active ? "text-[#D8BD88]" : "text-white/55 group-hover:text-white"}
                />

                <span className="flex-1 text-[13px] font-medium">
                  {item.label}
                </span>

                {active && (
                  <ChevronRight size={15} className="text-[#C4A66A]" />
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* BOTTOM SECTION */}
      <div className="mt-auto px-4 pb-5">

        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-white/55 transition hover:bg-white/5 hover:text-white"
        >
          <LogOut size={17} />
          <span className="text-[13px] font-medium">
            Sign out
          </span>
        </button>

        <div className="mt-4 border-t border-white/10 pt-4">
          <p className="text-center text-[10px] tracking-wide text-white/30">
            GEN VICURE · TREASURY MIS
          </p>
        </div>
      </div>
    </aside>
  );
}
