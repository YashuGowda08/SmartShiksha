"use client";

import Link from "next/link";

export default function MobileAuthError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 px-4">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">
        <h1 className="text-2xl font-bold text-slate-900 mb-3">Could not open mobile sign-in</h1>
        <p className="text-sm text-slate-600 mb-6">
          We hit an unexpected error while loading this page. Try again, or continue from the regular sign-in page.
        </p>

        <div className="space-y-3">
          <button
            type="button"
            onClick={reset}
            className="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white"
          >
            Retry
          </button>

          <Link
            href="/sign-in"
            className="block w-full rounded-xl border border-slate-300 px-4 py-3 text-center text-sm font-semibold text-slate-700"
          >
            Open Sign-In Page
          </Link>
        </div>

        <p className="mt-4 text-xs text-slate-500 break-words">{error?.message || "Unexpected error"}</p>
      </div>
    </div>
  );
}
