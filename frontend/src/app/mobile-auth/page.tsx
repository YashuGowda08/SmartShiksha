import MobileAuthClient from "./mobile-auth-client";

type MobileAuthPageProps = {
  searchParams: Promise<{ device_id?: string | string[] }>;
};

export default async function MobileAuthPage({ searchParams }: MobileAuthPageProps) {
  const params = await searchParams;
  const rawDeviceId = params.device_id;
  const deviceId = Array.isArray(rawDeviceId) ? rawDeviceId[0] ?? "" : rawDeviceId ?? "";
  return <MobileAuthClient deviceId={deviceId} />;
}