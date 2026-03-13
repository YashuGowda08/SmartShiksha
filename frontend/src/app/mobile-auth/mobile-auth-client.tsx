"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useMemo, useState } from "react";

type SyncState = "loading" | "missing-device" | "sign-in" | "syncing" | "done" | "error";

type MobileAuthClientProps = {
  deviceId: string;
};

export default function MobileAuthClient({ deviceId }: MobileAuthClientProps) {
  const { getToken, isLoaded, userId } = useAuth();
  const [state, setState] = useState<SyncState>(deviceId ? "loading" : "missing-device");
  const [error, setError] = useState<string | null>(null);

  const redirectUrl = useMemo(() => {
    if (!deviceId) return "/mobile-auth";
    return `/mobile-auth?device_id=${encodeURIComponent(deviceId)}`;
  }, [deviceId]);

  const signInUrl = useMemo(() => {
    return `/sign-in?redirect_url=${encodeURIComponent(redirectUrl)}`;
  }, [redirectUrl]);

  useEffect(() => {
    async function syncMobileSession() {
      if (!deviceId) {
        setState("missing-device");
        return;
      }
      if (!isLoaded) {
        setState("loading");
        return;
      }
      if (!userId) {
        setState("sign-in");
        return;
      }

      setState("syncing");
      setError(null);

      try {
        const token = await getToken();
        if (!token) throw new Error("No Clerk session token was returned.");

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/mobile/session`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ device_id: deviceId }),
        });

        if (!response.ok) {
          const payload = await response.json().catch(() => ({}));
          throw new Error(payload.detail || "Failed to sync mobile sign-in.");
        }

        setState("done");
      } catch (err) {
        setState("error");
        setError(err instanceof Error ? err.message : "Failed to sync mobile sign-in.");
      }
    }

    void syncMobileSession();
  }, [deviceId, getToken, isLoaded, userId]);

  useEffect(() => {
    if (state !== "sign-in") return;

    const timer = window.setTimeout(() => {
      window.location.replace(signInUrl);
    }, 150);

    return () => window.clearTimeout(timer);
  }, [signInUrl, state]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 px-4">
      <div className="w-full max-w-md">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold gradient-text mb-2">SmartShiksha Mobile Sign-In</h1>
            <p className="text-slate-600">Authenticate once in the browser and return to the app.</p>
          </div>

          {state === "loading" && <p className="text-sm text-slate-600">Checking your Clerk session...</p>}

          {state === "missing-device" && (
            <div className="rounded-2xl bg-amber-50 p-4 text-sm text-amber-900">
              This page needs a valid mobile device session id from the app.
            </div>
          )}

          {state === "sign-in" && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
                Redirecting you to the secure Clerk sign-in page...
              </div>
              <a
                href={signInUrl}
                className="block w-full rounded-xl bg-slate-900 px-4 py-3 text-center text-sm font-semibold text-white"
              >
                Continue to Sign-In
              </a>
            </div>
          )}

          {state === "syncing" && <p className="text-sm text-slate-600">Syncing your session back to the app...</p>}

          {state === "done" && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-emerald-50 p-4 text-sm text-emerald-900">
                Sign-in completed. Return to SmartShiksha and the app will continue automatically.
              </div>
              <button
                type="button"
                onClick={() => window.close()}
                className="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white"
              >
                Close This Tab
              </button>
            </div>
          )}

          {state === "error" && (
            <div className="rounded-2xl bg-rose-50 p-4 text-sm text-rose-900">
              {error || "Failed to sync mobile sign-in."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}