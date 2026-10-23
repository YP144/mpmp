// src/app/login/page.tsx

import LoginClient from "../LoginClient";

interface LoginPageProps {
  searchParams: Promise<{
    [key: string]:
      | string
      | string[]
      | undefined;
  }>;
}

export default async function LoginPage({
  searchParams,
}: LoginPageProps) {

  const resolvedSearchParams = await searchParams;

  const getParam = (
    value:
      | string
      | string[]
      | undefined
  ): string | undefined => {
    if (Array.isArray(value)) {
      return value[0] ? decodeURIComponent(value[0]).trim() : undefined;
    }
    return value ? decodeURIComponent(value).trim() : undefined;
  };

  const errorCode = getParam(resolvedSearchParams.error);
  const userId = getParam(resolvedSearchParams.userId);
  const userIc = getParam(resolvedSearchParams.userIc);
  const email = getParam(resolvedSearchParams.email);

  return (
    <LoginClient
      errorCode={errorCode}
      userId={userId}
      userIc={userIc}
      emailParam={email}
    />
  );
}