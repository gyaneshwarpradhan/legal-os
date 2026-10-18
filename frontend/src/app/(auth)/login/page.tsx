"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Lock, Mail, Scale } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("attorney@legalos.local");
  const [password, setPassword] = useState("attorney123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const resp = await api.login(email, password);
      await login(resp.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <Card className="border-slate-800 bg-slate-950 text-white shadow-2xl">
        <CardHeader className="space-y-2 text-center pb-6">
          <div className="mx-auto h-12 w-12 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg mb-2">
            <Scale className="h-6 w-6" />
          </div>
          <CardTitle className="text-xl font-bold tracking-tight text-white">
            Apex Litigation Operating System
          </CardTitle>
          <CardDescription className="text-slate-400 text-xs">
            Private, matter-isolated firm intelligence platform
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-200 text-xs flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">
                Firm Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <Input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-9 bg-slate-900 border-slate-800 text-white placeholder:text-slate-600 focus-visible:ring-blue-600"
                  placeholder="attorney@legalos.local"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <Input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-9 bg-slate-900 border-slate-800 text-white placeholder:text-slate-600 focus-visible:ring-blue-600"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="pt-2 text-[11px] text-slate-400 bg-slate-900/50 p-2.5 rounded border border-slate-800/80">
              <span className="font-semibold text-slate-300">Demo Logins:</span>
              <div className="mt-1 flex flex-col space-y-0.5">
                <span>Senior Trial Attorney: <code className="text-blue-400">attorney@legalos.local</code> / <code className="text-slate-300">attorney123</code></span>
                <span>Managing Partner: <code className="text-blue-400">admin@legalos.local</code> / <code className="text-slate-300">admin123</code></span>
              </div>
            </div>
          </CardContent>

          <CardFooter className="pt-2">
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium"
            >
              {loading ? "Authenticating..." : "Sign In to Workspace"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
