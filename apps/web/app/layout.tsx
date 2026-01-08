import type { ReactNode } from "react";

import "./globals.css";
import { Providers } from "./providers";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-black text-zinc-100 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
