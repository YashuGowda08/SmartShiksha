import { SignUp } from "@clerk/nextjs";

type SignUpPageProps = {
  searchParams: Promise<{ redirect_url?: string | string[] }>;
};

export default async function SignUpPage({ searchParams }: SignUpPageProps) {
  const params = await searchParams;
  const rawRedirectUrl = params.redirect_url;
  const redirectUrl = Array.isArray(rawRedirectUrl)
    ? rawRedirectUrl[0] ?? undefined
    : rawRedirectUrl;
  const signInUrl = redirectUrl
    ? `/sign-in?redirect_url=${encodeURIComponent(redirectUrl)}`
    : "/sign-in";

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold gradient-text mb-2">Join Smart Shiksha</h1>
          <p className="text-slate-600">Start your learning journey today</p>
        </div>
        <SignUp
          forceRedirectUrl={redirectUrl}
          signInUrl={signInUrl}
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl border border-slate-200 rounded-2xl",
            },
          }}
        />
      </div>
    </div>
  );
}
