"use server";

import { revalidatePath } from "next/cache";
import { prisma } from "@/lib/prisma";

export async function createProduct(formData: FormData) {
  const name = String(formData.get("name") ?? "").trim();
  const brandId = String(formData.get("brandId") ?? "");
  const categoryId = String(formData.get("categoryId") ?? "");
  if (!name || !brandId || !categoryId) return;

  await prisma.product.create({ data: { name, brandId, categoryId } });
  revalidatePath("/produtos");
}

export async function deleteProduct(id: string) {
  await prisma.product.delete({ where: { id } });
  revalidatePath("/produtos");
}

export async function addPackage(productId: string, formData: FormData) {
  const type = String(formData.get("type") ?? "SACO_FECHADO") as
    | "SACO_FECHADO"
    | "GRANEL";
  const weightKgRaw = String(formData.get("weightKg") ?? "");
  const price = Number(formData.get("price") ?? 0);
  const stockQty = Number(formData.get("stockQty") ?? 0);

  await prisma.productPackage.create({
    data: {
      productId,
      type,
      weightKg: type === "SACO_FECHADO" ? Number(weightKgRaw) : null,
      price,
      stockQty,
    },
  });
  revalidatePath("/produtos");
}

export async function deletePackage(id: string) {
  await prisma.productPackage.delete({ where: { id } });
  revalidatePath("/produtos");
}
