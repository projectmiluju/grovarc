import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/", "/login", "/signup"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 공개 경로는 통과
  if (PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith("/api"))) {
    return NextResponse.next();
  }

  // 정적 파일, Next.js 내부 경로 통과
  if (pathname.startsWith("/_next") || pathname.includes(".")) {
    return NextResponse.next();
  }

  // grovarc-auth 쿠키로 로그인 여부 확인 (서버 사이드)
  const authCookie = request.cookies.get("grovarc-auth");
  if (!authCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
