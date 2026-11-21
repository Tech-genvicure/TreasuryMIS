"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import Sidebar from "@/components/sidebar";
import Spreadsheet from "@/components/Spreadsheet";
import { isAuthenticated } from "@/lib/auth";


export default function SpreadsheetPage() {

  const router = useRouter();


  useEffect(() => {

    if (!isAuthenticated()) {
      router.replace("/login");
    }

  }, [router]);


  return (
    <main className="h-screen w-screen overflow-hidden flex bg-[#F4F8FC]">

      <Sidebar />

      <section className="flex-1 min-w-0 h-screen overflow-hidden">

        <Spreadsheet />

      </section>

    </main>
  );
}