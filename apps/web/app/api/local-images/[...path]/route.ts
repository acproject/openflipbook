import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const IMAGES_DIR = path.join(process.cwd(), "..", "..", "data", "images");

export async function GET(
  req: Request,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const pathSegments = await params;
  const filePath = path.join(IMAGES_DIR, ...pathSegments.path);

  if (!fs.existsSync(filePath)) {
    return NextResponse.json({ error: "Image not found" }, { status: 404 });
  }

  const buffer = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const contentType = ext === ".png" ? "image/png" : "image/jpeg";

  return new Response(buffer, {
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
