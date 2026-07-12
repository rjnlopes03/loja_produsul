import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Produsul Cereais - Estoque",
  description: "Controle de estoque de rações",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>
        <nav
          style={{
            display: "flex",
            gap: 16,
            padding: "16px 24px",
            borderBottom: "1px solid #ddd",
          }}
        >
          <strong>Produsul Cereais</strong>
          <Link href="/">Início</Link>
          <Link href="/marcas">Marcas</Link>
          <Link href="/produtos">Produtos</Link>
          <Link href="/estoque">Estoque</Link>
        </nav>
        <main style={{ padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}
