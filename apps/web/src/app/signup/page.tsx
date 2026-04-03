"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { signup, login } from "@/lib/auth";

const schema = z
  .object({
    email: z.string().email("올바른 이메일을 입력하세요"),
    nickname: z.string().min(2, "닉네임은 2자 이상이어야 합니다").max(20, "닉네임은 20자 이하"),
    password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다"),
    passwordConfirm: z.string(),
  })
  .refine((d) => d.password === d.passwordConfirm, {
    message: "비밀번호가 일치하지 않습니다",
    path: ["passwordConfirm"],
  });

type FormValues = z.infer<typeof schema>;

export default function SignupPage() {
  const router = useRouter();
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async ({ email, password, nickname }: FormValues) => {
    try {
      setServerError("");
      await signup({ email, password, nickname });
      await login({ email, password });
      router.replace("/dashboard");
    } catch {
      setServerError("회원가입에 실패했습니다. 이미 사용 중인 이메일일 수 있습니다.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Grovarc</h1>
          <p className="mt-1 text-sm text-muted-foreground">개발자 성장 트래커 시작하기</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              type="email"
              placeholder="dev@example.com"
              autoComplete="email"
              {...register("email")}
            />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="nickname">닉네임</Label>
            <Input
              id="nickname"
              placeholder="개발자닉네임"
              autoComplete="nickname"
              {...register("nickname")}
            />
            {errors.nickname && (
              <p className="text-xs text-destructive">{errors.nickname.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="password">비밀번호</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              {...register("password")}
            />
            {errors.password && (
              <p className="text-xs text-destructive">{errors.password.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="passwordConfirm">비밀번호 확인</Label>
            <Input
              id="passwordConfirm"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              {...register("passwordConfirm")}
            />
            {errors.passwordConfirm && (
              <p className="text-xs text-destructive">{errors.passwordConfirm.message}</p>
            )}
          </div>

          {serverError && (
            <p className="text-center text-sm text-destructive">{serverError}</p>
          )}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "가입 중..." : "회원가입"}
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          이미 계정이 있으신가요?{" "}
          <Link href="/login" className="font-medium text-primary hover:underline">
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
