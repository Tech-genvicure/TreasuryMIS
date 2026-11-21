
"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Eye,
  EyeOff,
  LockKeyhole,
  ArrowRight,
  Landmark,
  ShieldCheck,
} from "lucide-react";

import api from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        username,
        password,
      });

      setToken(response.data.access_token);
      router.push("/dashboard");
    } catch {
      setError("Invalid username or password. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#F6F4EF] px-5 py-10">

      {/* BACKGROUND DECORATION */}
      <div className="pointer-events-none absolute -right-32 -top-32 h-[480px] w-[480px] rounded-full border border-[#DCD5C7]/50" />
      <div className="pointer-events-none absolute -right-20 -top-20 h-[360px] w-[360px] rounded-full border border-[#DCD5C7]/40" />
      <div className="pointer-events-none absolute -bottom-48 -left-36 h-[500px] w-[500px] rounded-full border border-[#DCD5C7]/50" />

      {/* MAIN CONTENT */}
      <div className="relative z-10 w-full max-w-[440px]">

        {/* BRAND */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-5 flex h-[62px] w-[62px] items-center justify-center rounded-2xl border border-[#C4A66A]/40 bg-[#14263D] shadow-[0_8px_20px_rgba(20,38,61,0.15)]">
            <Landmark size={29} strokeWidth={1.6} className="text-[#D8BD88]" />
          </div>

          <h1 className="text-[30px] font-semibold tracking-[-1px] text-[#14263D]">
            Genvicure
          </h1>

          <p className="mt-1 text-[11px] font-semibold uppercase tracking-[3px] text-[#A88950]">
            Treasury MIS
          </p>

          <p className="mt-4 text-[13px] text-[#8290A0]">
            Financial intelligence. Clear decisions.
          </p>
        </div>

        {/* LOGIN CARD */}
        <div className="rounded-2xl border border-[#E8E5DE] bg-white p-7 shadow-[0_15px_50px_rgba(20,38,61,0.07)] sm:p-9">

          <div className="mb-7">
            <div className="mb-2 flex items-center gap-2">
              <span className="h-[2px] w-5 bg-[#C4A66A]" />
              <p className="text-[10px] font-semibold uppercase tracking-[1.8px] text-[#A88950]">
                Secure access
              </p>
            </div>

            <h2 className="text-[25px] font-semibold tracking-[-0.7px] text-[#14263D]">
              Welcome back
            </h2>

            <p className="mt-2 text-[13px] leading-relaxed text-[#8290A0]">
              Sign in to access your treasury workspace.
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-5">

            {/* USERNAME */}
            <div>
              <label
                htmlFor="username"
                className="mb-2 block text-[12px] font-semibold text-[#526174]"
              >
                Username
              </label>

              <input
                id="username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="h-[49px] w-full rounded-lg border border-[#E3E5E7] bg-[#FAFAF8] px-4 text-[13px] text-[#14263D] outline-none transition placeholder:text-[#A5ADB6] focus:border-[#C4A66A] focus:bg-white focus:ring-2 focus:ring-[#C4A66A]/10"
                placeholder="Enter your username"
                required
              />
            </div>

            {/* PASSWORD */}
            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-[12px] font-semibold text-[#526174]"
              >
                Password
              </label>

              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="h-[49px] w-full rounded-lg border border-[#E3E5E7] bg-[#FAFAF8] px-4 pr-12 text-[13px] text-[#14263D] outline-none transition placeholder:text-[#A5ADB6] focus:border-[#C4A66A] focus:bg-white focus:ring-2 focus:ring-[#C4A66A]/10"
                  placeholder="Enter your password"
                  required
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-[#8290A0] transition hover:bg-[#F1EEE7] hover:text-[#14263D]"
                >
                  {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
            </div>

            {/* ERROR */}
            {error && (
              <div
                role="alert"
                className="rounded-lg border border-[#EBD5D1] bg-[#FBF1EF] px-4 py-3 text-[12px] leading-relaxed text-[#A84E48]"
              >
                {error}
              </div>
            )}

            {/* SUBMIT */}
            <button
              type="submit"
              disabled={loading}
              className="group flex h-[50px] w-full items-center justify-center gap-2 rounded-lg bg-[#14263D] text-[13px] font-semibold text-white shadow-[0_4px_12px_rgba(20,38,61,0.12)] transition duration-200 hover:bg-[#243A52] hover:shadow-[0_6px_18px_rgba(20,38,61,0.16)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign in to workspace
                  <ArrowRight
                    size={16}
                    className="transition-transform group-hover:translate-x-1"
                  />
                </>
              )}
            </button>
          </form>

          {/* SECURITY NOTE */}
          <div className="mt-7 flex items-center justify-center gap-2 border-t border-[#EEECE6] pt-5">
            <ShieldCheck size={15} className="text-[#A88950]" />
            <p className="text-[10px] text-[#8290A0]">
              Secure access to your financial workspace
            </p>
          </div>
        </div>

        {/* FOOTER */}
        <div className="mt-7 text-center">
          <div className="flex items-center justify-center gap-2">
            <LockKeyhole size={12} className="text-[#A88950]" />
            <p className="text-[10px] font-medium tracking-wide text-[#8290A0]">
              GEN VICURE · TREASURY MIS
            </p>
          </div>

          <p className="mt-2 text-[10px] text-[#A5ADB6]">
            Authorized personnel only
          </p>
        </div>
      </div>
    </main>
  );
}
