import LoginForm from "@/components/login-form";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ mode?: string }>;
}) {
  const params = await searchParams;
  return <LoginForm initialMode={params.mode === "register" ? "register" : "login"} />;
}
