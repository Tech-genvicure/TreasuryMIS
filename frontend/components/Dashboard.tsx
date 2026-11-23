
"use client";

import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import {
  Landmark,
  FileText,
  CircleDollarSign,
  Building2,
  CreditCard,
  TrendingUp,
  WalletCards,
  Database,
  CalendarDays,
  RefreshCw,
} from "lucide-react";
import api from "@/lib/api";

interface DashboardData {
  reporting_date: string;
  kpis: {
    total_cash_inr: number;
    total_cash_usd: number;
    total_payables: number;
    total_receivables: number;
    net_cash_position: number;
  };
  borrowings: {
    sanctioned: number;
    disbursed: number;
    outstanding: number;
  };
  fund_summary: {
    company_name: string;
    amount: number;
  }[];
  vendor_exposure: {
    vendor_name: string;
    amount: number;
  }[];
  payable_timeline: {
    bucket: string;
    amount: number;
  }[];
  receivable_timeline: {
    bucket: string;
    amount: number;
  }[];
}

const formatCr = (value: number) =>
  `${(Number(value || 0) / 10000000).toFixed(2)} Cr`;


const formatReportingDate = (value: string) => {
  if (!value) return "--";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";

  // Display the previous day's reporting date
  date.setDate(date.getDate() - 1);

  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};


function getFundIcon(name: string) {
  const normalized = name.toLowerCase();

  if (normalized.includes("mutual")) return TrendingUp;

  if (
    normalized.includes("fd") ||
    normalized.includes("fixed")
  ) {
    return Database;
  }

  if (
    normalized.includes("bank") ||
    normalized.includes("icici") ||
    normalized.includes("america")
  ) {
    return Landmark;
  }

  return WalletCards;
}

const cardBase =
  "rounded-xl border border-[#E8E5DE] bg-white shadow-[0_2px_8px_rgba(20,38,61,0.025)]";

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  async function loadDashboard(isRefresh = false) {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);

      setError("");

      const response = await api.get("/dashboard");
      setData(response.data);
    } catch (err) {
      console.error(err);
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full min-h-[500px] items-center justify-center bg-[#F6F4EF]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-[#E8E5DE] border-t-[#C4A66A]" />
          <p className="text-sm text-[#526174]">
            Loading financial overview...
          </p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-full min-h-[500px] flex-col items-center justify-center gap-4 bg-[#F6F4EF]">
        <Landmark size={30} className="text-[#B65B55]" />
        <p className="text-sm text-[#526174]">
          {error || "No dashboard data available."}
        </p>
        <button
          onClick={() => loadDashboard(true)}
          className="rounded-lg bg-[#14263D] px-5 py-2.5 text-sm font-medium text-white hover:bg-[#243A52]"
        >
          Try again
        </button>
      </div>
    );
  }

  const vendorData = (data.vendor_exposure || []).map((item) => ({
    name:
      item.vendor_name.length > 25
        ? `${item.vendor_name.slice(0, 25)}...`
        : item.vendor_name,
    amount: Number(item.amount || 0) / 100000,
  }));

  const cashFlowData = (data.payable_timeline || []).map((item) => {
    const receivable = (data.receivable_timeline || []).find(
      (r) => r.bucket === item.bucket
    );

    return {
      bucket: item.bucket,
      payables: Number(item.amount || 0) / 100000,
      receivables: Number(receivable?.amount || 0) / 100000,
    };
  });

  return (
    <div className="h-full min-h-0 w-full overflow-auto bg-[#F6F4EF] p-5 text-[#14263D] lg:overflow-hidden lg:p-6">
      <div className="flex min-h-full flex-col gap-5 lg:h-full">

        {/* HEADER */}
        <header className="flex shrink-0 items-center justify-between gap-4">
          <div>
            <h1 className="text-[32px] font-semibold leading-tight tracking-[-1.2px] text-[#14263D] xl:text-[38px]">
              Daily Fund Position
            </h1>

            <p className="mt-2 text-[15px] text-[#718092] xl:text-[17px]">
              Cash Flow
              <span className="mx-3 text-[#C4A66A]">·</span>
              Liquidity
              <span className="mx-3 text-[#C4A66A]">·</span>
              Investments
            </p>
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-[#DCE5ED] bg-[#EAF1F7] px-4 py-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-[#243A52]">
              <CalendarDays size={21} />
            </div>

            <div>
              <p className="text-[12px] font-medium text-[#718092]">
                Reporting Date
              </p>
              <p className="mt-0.5 text-[19px] font-semibold tracking-tight text-[#14263D]">
                {formatReportingDate(data.reporting_date)}
              </p>
            </div>

            <button
              onClick={() => loadDashboard(true)}
              disabled={refreshing}
              title="Refresh dashboard"
              className="ml-2 flex h-8 w-8 items-center justify-center rounded-lg text-[#718092] transition hover:bg-white hover:text-[#A88950] disabled:opacity-50"
            >
              <RefreshCw
                size={15}
                className={refreshing ? "animate-spin" : ""}
              />
            </button>
          </div>
        </header>

        {/* TOP SECTION: KPI + FUND BREAKDOWN + BORROWINGS */}
        <div className="grid shrink-0 grid-cols-1 gap-5 xl:grid-cols-[1.65fr_1fr]">

          {/* LEFT COLUMN */}
          <div className="min-w-0">

            {/* MAIN KPI CARDS */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">

              {/* FUNDS */}
              <div className="relative h-[190px] overflow-hidden rounded-xl bg-gradient-to-br from-[#1D4265] to-[#14263D] p-5 text-white shadow-sm xl:h-[215px] xl:p-6">
                <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full border border-white/10" />
                <CircleDollarSign size={36} strokeWidth={1.9} className="relative text-[#D8BD88]" />

                <p className="relative mt-5 text-[15px] font-medium text-white/85 xl:text-[17px]">
                  Funds Available
                </p>

                <p className="relative mt-2 text-[30px] font-semibold leading-none tracking-[-1px] tabular-nums xl:text-[36px]">
                  {formatCr(data.kpis.total_cash_inr)}
                </p>

                <div className="absolute bottom-0 left-0 h-[3px] w-full bg-[#C4A66A]" />
              </div>

              {/* PAYABLES */}
              <div className="relative h-[190px] overflow-hidden rounded-xl bg-gradient-to-br from-[#27866F] to-[#1D705E] p-5 text-white shadow-sm xl:h-[215px] xl:p-6">
                <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full border border-white/10" />
                <FileText size={36} strokeWidth={1.9} className="relative text-white/90" />

                <p className="relative mt-5 text-[15px] font-medium text-white/85 xl:text-[17px]">
                  Total Payables
                </p>

                <p className="relative mt-2 text-[30px] font-semibold leading-none tracking-[-1px] tabular-nums xl:text-[36px]">
                  {formatCr(data.kpis.total_payables)}
                </p>

                <div className="absolute bottom-0 left-0 h-[3px] w-full bg-[#9BC8B8]" />
              </div>

              {/* RECEIVABLES */}
              <div className="relative h-[190px] overflow-hidden rounded-xl bg-gradient-to-br from-[#347D83] to-[#245F68] p-5 text-white shadow-sm xl:h-[215px] xl:p-6">
                <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full border border-white/10" />
                <CircleDollarSign size={36} strokeWidth={1.9} className="relative text-[#D6E9E5]" />

                <p className="relative mt-5 text-[15px] font-medium text-white/85 xl:text-[17px]">
                  Total Receivables
                </p>

                <p className="relative mt-2 text-[30px] font-semibold leading-none tracking-[-1px] tabular-nums xl:text-[36px]">
                  {formatCr(data.kpis.total_receivables)}
                </p>

                <div className="absolute bottom-0 left-0 h-[3px] w-full bg-[#A6D0CB]" />
              </div>
            </div>

            {/* FUND BREAKDOWN */}
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {data.fund_summary.slice(0, 4).map((fund, index) => {
                const Icon = getFundIcon(fund.company_name);

                return (
                  <div
                    key={`${fund.company_name}-${index}`}
                    className="flex h-[86px] min-w-0 items-center gap-3 rounded-xl border border-[#E1E7EA] bg-[#EDF1F3] px-3 py-3 transition hover:border-[#C4A66A] xl:h-[94px] xl:px-4"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white text-[#526B7C]">
                      <Icon size={23} strokeWidth={1.8} />
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-[12px] font-medium text-[#526174] xl:text-[14px]">
                        {fund.company_name}
                      </p>
                      <p className="mt-1 truncate text-[19px] font-semibold leading-none tracking-tight text-[#14263D] tabular-nums xl:text-[23px]">
                        {formatCr(fund.amount)}
                      </p>
                    </div>
                  </div>
                );
              })}

              {Array.from({
                length: Math.max(0, 4 - data.fund_summary.length),
              }).map((_, index) => (
                <div
                  key={`empty-${index}`}
                  className="h-[86px] rounded-xl border border-[#E1E7EA] bg-[#EDF1F3] xl:h-[94px]"
                />
              ))}
            </div>
          </div>

          {/* BORROWINGS */}
          <div className={`${cardBase} min-h-[300px] p-5 xl:h-[323px]`}>
            <div className="flex items-center justify-between">
              <h2 className="text-[22px] font-semibold tracking-[-0.5px] text-[#14263D] xl:text-[24px]">
                Borrowings
              </h2>
              <Landmark size={20} className="text-[#A88950]" />
            </div>

            <div className="mt-4 grid grid-cols-3 gap-2.5 xl:gap-3">

              {/* SANCTIONED */}
              <div className="flex h-[175px] flex-col rounded-xl border border-[#E0E8ED] bg-[#EDF2F5] p-3 xl:h-[190px] xl:p-4">
                <Building2 size={30} className="text-[#526B7C] xl:size-[34px]" />

                <p className="mt-4 text-[13px] text-[#526174] xl:text-[15px]">
                  Sanctioned
                </p>

                <p className="mt-auto text-[21px] font-semibold tracking-tight text-[#14263D] tabular-nums xl:text-[27px]">
                  {formatCr(data.borrowings.sanctioned)}
                </p>
              </div>

              {/* DISBURSED */}
              <div className="flex h-[175px] flex-col rounded-xl border border-[#E9E2D4] bg-[#F5F1E8] p-3 xl:h-[190px] xl:p-4">
                <CreditCard size={30} className="text-[#A88950] xl:size-[34px]" />

                <p className="mt-4 text-[13px] text-[#526174] xl:text-[15px]">
                  Disbursed
                </p>

                <p className="mt-auto text-[21px] font-semibold tracking-tight text-[#14263D] tabular-nums xl:text-[27px]">
                  {formatCr(data.borrowings.disbursed)}
                </p>
              </div>

              {/* OUTSTANDING */}
              <div className="flex h-[175px] flex-col rounded-xl border border-[#E8E2DF] bg-[#F4EEEB] p-3 xl:h-[190px] xl:p-4">
                <TrendingUp size={30} className="text-[#A66D55] xl:size-[34px]" />

                <p className="mt-4 text-[13px] text-[#526174] xl:text-[15px]">
                  Outstanding
                </p>

                <p className="mt-auto text-[21px] font-semibold tracking-tight text-[#14263D] tabular-nums xl:text-[27px]">
                  {formatCr(data.borrowings.outstanding)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* BOTTOM CHARTS */}
        <div className="grid min-h-[340px] flex-1 grid-cols-1 gap-5 xl:min-h-0 xl:grid-cols-2">

          {/* TOP VENDOR EXPOSURE */}
          <div className={`${cardBase} flex min-h-[340px] min-w-0 flex-col p-5 xl:min-h-0`}>
            <div className="flex shrink-0 items-center justify-between">
              <div>
                <h2 className="text-[21px] font-semibold tracking-[-0.4px] text-[#14263D] xl:text-[23px]">
                  Top Vendor Exposure
                </h2>
                <p className="mt-1 text-[11px] text-[#8290A0]">
                  Payable concentration by vendor
                </p>
              </div>
              <FileText size={19} className="text-[#A88950]" />
            </div>

            <div className="mt-2 min-h-[260px] flex-1">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={vendorData}
                  layout="vertical"
                  margin={{ top: 5, right: 25, bottom: 5, left: 5 }}
                >
                  <CartesianGrid
                    horizontal={false}
                    stroke="#E8E5DE"
                    strokeDasharray="3 4"
                  />

                  <XAxis
                    type="number"
                    tick={{ fill: "#8290A0", fontSize: 11 }}
                    axisLine={{ stroke: "#E8E5DE" }}
                    tickLine={false}
                    label={{
                      value: "Amount Payable (Lakhs)",
                      position: "insideBottom",
                      offset: -2,
                      fill: "#526174",
                      fontSize: 11,
                    }}
                  />

                  <YAxis
                    type="category"
                    dataKey="name"
                    width={145}
                    tick={{ fill: "#526174", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <Tooltip
                    contentStyle={{
                      borderRadius: "9px",
                      border: "1px solid #E8E5DE",
                      boxShadow: "0 5px 20px rgba(20,38,61,0.08)",
                      fontSize: "12px",
                    }}
                    formatter={(value) =>
                      [`${Number(value).toLocaleString("en-IN")} L`, "Payables"]
                    }
                  />

                  <Bar
                    dataKey="amount"
                    fill="#526FAD"
                    radius={[0, 4, 4, 0]}
                    barSize={15}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* CASH INFLOW VS OUTFLOW */}
          <div className={`${cardBase} flex min-h-[340px] min-w-0 flex-col p-5 xl:min-h-0`}>
            <div className="flex shrink-0 items-center justify-between">
              <div>
                <h2 className="text-[21px] font-semibold tracking-[-0.4px] text-[#14263D] xl:text-[23px]">
                  Cash Inflow Vs Cash Outflow
                </h2>
                <p className="mt-1 text-[11px] text-[#8290A0]">
                  Receivables and payables by due-date bucket
                </p>
              </div>
              <TrendingUp size={19} className="text-[#A88950]" />
            </div>

            {/* LEGEND */}
            <div className="mt-3 flex shrink-0 items-center gap-6 text-[12px]">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[#27866F]" />
                <span className="text-[#526174]">Payables</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[#7188B8]" />
                <span className="text-[#526174]">Receivables</span>
              </div>
            </div>

            <div className="mt-1 min-h-[240px] flex-1">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={cashFlowData}
                  layout="vertical"
                  margin={{ top: 5, right: 25, bottom: 5, left: 10 }}
                >
                  <CartesianGrid
                    horizontal={false}
                    stroke="#E8E5DE"
                    strokeDasharray="3 4"
                  />

                  <XAxis
                    type="number"
                    tick={{ fill: "#8290A0", fontSize: 11 }}
                    axisLine={{ stroke: "#E8E5DE" }}
                    tickLine={false}
                    label={{
                      value: "Amount (Lakhs)",
                      position: "insideBottom",
                      offset: -2,
                      fill: "#526174",
                      fontSize: 11,
                    }}
                  />

                  <YAxis
                    type="category"
                    dataKey="bucket"
                    width={90}
                    tick={{ fill: "#526174", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <Tooltip
                    contentStyle={{
                      borderRadius: "9px",
                      border: "1px solid #E8E5DE",
                      boxShadow: "0 5px 20px rgba(20,38,61,0.08)",
                      fontSize: "12px",
                    }}
                    formatter={(value, name) => [
                      `${Number(value).toLocaleString("en-IN")} L`,
                      name,
                    ]}
                  />

                  <Bar
                    dataKey="payables"
                    name="Payables"
                    fill="#27866F"
                    radius={[0, 3, 3, 0]}
                    barSize={15}
                  />

                  <Bar
                    dataKey="receivables"
                    name="Receivables"
                    fill="#7188B8"
                    radius={[0, 3, 3, 0]}
                    barSize={15}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
