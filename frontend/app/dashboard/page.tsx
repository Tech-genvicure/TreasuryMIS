
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import Sidebar from "@/components/sidebar";
import Dashboard from "@/components/Dashboard";
import { isAuthenticated } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-[#F6F4EF]">
      <Sidebar />

      <section className="h-screen min-w-0 flex-1 overflow-hidden">
        <Dashboard />
      </section>
    </main>
  );
}
