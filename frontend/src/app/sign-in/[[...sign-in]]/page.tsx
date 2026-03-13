import { SignIn } from "@clerk/nextjs";

type SignInPageProps = {
  searchParams: Promise<{ redirect_url?: string | string[] }>;
};

export default async function SignInPage({ searchParams }: SignInPageProps) {
  const params = await searchParams;
  const rawRedirectUrl = params.redirect_url;
  const redirectUrl = Array.isArray(rawRedirectUrl)
    ? rawRedirectUrl[0] ?? undefined
    : rawRedirectUrl;
  const signUpUrl = redirectUrl
    ? `/sign-up?redirect_url=${encodeURIComponent(redirectUrl)}`
    : "/sign-up";

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold gradient-text mb-2">Welcome Back</h1>
          <p className="text-slate-600">Sign in to continue learning</p>
        </div>
        <SignIn
          forceRedirectUrl={redirectUrl}
          signUpUrl={signUpUrl}
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
