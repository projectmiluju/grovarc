import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">Grovarc</h1>
        <p className="mt-3 text-lg text-muted-foreground">
          매일 작업 로그를 기록하면 AI가 회고 초안과 성장 로드맵을 만들어줍니다.
        </p>
      </div>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="rounded-md bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          로그인
        </Link>
        <Link
          href="/signup"
          className="rounded-md border border-input px-6 py-2.5 text-sm font-medium hover:bg-accent"
        >
          회원가입
        </Link>
      </div>
    </main>
  );
}
