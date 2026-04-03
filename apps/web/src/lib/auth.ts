import api from "./api";
import { useAuthStore } from "@/store/authStore";
import type { LoginRequest, SignupRequest, TokenResponse, User } from "@/types";

export async function login(body: LoginRequest): Promise<void> {
  const { data } = await api.post<TokenResponse>("/api/v1/auth/login", body);
  useAuthStore.getState().setAccessToken(data.accessToken);

  const { data: user } = await api.get<User>("/api/v1/users/me");
  useAuthStore.getState().setUser(user);
}

export async function signup(body: SignupRequest): Promise<void> {
  await api.post("/api/v1/auth/signup", body);
}

export async function logout(): Promise<void> {
  try {
    await api.post("/api/v1/auth/logout");
  } finally {
    useAuthStore.getState().logout();
  }
}
