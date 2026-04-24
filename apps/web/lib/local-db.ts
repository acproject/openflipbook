import fs from "fs";
import path from "path";

const DATA_DIR = path.join(process.cwd(), "..", "..", "data");
const NODES_FILE = path.join(DATA_DIR, "nodes.json");
const IMAGES_DIR = path.join(DATA_DIR, "images");

function ensureDataDir(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
  if (!fs.existsSync(IMAGES_DIR)) {
    fs.mkdirSync(IMAGES_DIR, { recursive: true });
  }
  if (!fs.existsSync(NODES_FILE)) {
    fs.writeFileSync(NODES_FILE, JSON.stringify([], null, 2));
  }
}

function readNodes(): NodeDoc[] {
  ensureDataDir();
  const raw = fs.readFileSync(NODES_FILE, "utf-8");
  return JSON.parse(raw) as NodeDoc[];
}

function writeNodes(nodes: NodeDoc[]): void {
  ensureDataDir();
  fs.writeFileSync(NODES_FILE, JSON.stringify(nodes, null, 2));
}

export interface NodeDoc {
  id: string;
  parent_id: string | null;
  session_id: string;
  query: string;
  page_title: string;
  image_key: string;
  image_model: string;
  prompt_author_model: string;
  aspect_ratio: string;
  final_prompt: string | null;
  created_at: string;
}

export interface NodeInsert {
  parent_id: string | null;
  session_id: string;
  query: string;
  page_title: string;
  image_key: string;
  image_model: string;
  prompt_author_model: string;
  aspect_ratio: string;
  final_prompt: string | null;
}

export interface NodeRow {
  id: string;
  parent_id: string | null;
  session_id: string;
  query: string;
  page_title: string;
  image_key: string;
  image_model: string;
  prompt_author_model: string;
  aspect_ratio: string;
  final_prompt: string | null;
  created_at: string;
}

function toRow(doc: NodeDoc): NodeRow {
  return { ...doc };
}

export async function insertNode(n: NodeInsert): Promise<NodeRow> {
  const nodes = readNodes();
  const doc: NodeDoc = {
    id: crypto.randomUUID(),
    parent_id: n.parent_id,
    session_id: n.session_id,
    query: n.query,
    page_title: n.page_title,
    image_key: n.image_key,
    image_model: n.image_model,
    prompt_author_model: n.prompt_author_model,
    aspect_ratio: n.aspect_ratio,
    final_prompt: n.final_prompt,
    created_at: new Date().toISOString(),
  };
  nodes.push(doc);
  writeNodes(nodes);
  return toRow(doc);
}

export async function getNode(id: string): Promise<NodeRow | null> {
  const nodes = readNodes();
  const doc = nodes.find((n) => n.id === id);
  return doc ? toRow(doc) : null;
}

export async function listNodesBySession(
  sessionId: string,
  limit = 50
): Promise<NodeRow[]> {
  const nodes = readNodes();
  return nodes
    .filter((n) => n.session_id === sessionId)
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    .slice(0, limit)
    .map(toRow);
}

export function getImagePath(imageKey: string): string {
  return path.join(IMAGES_DIR, imageKey);
}

export async function saveImage(imageKey: string, buffer: Buffer): Promise<string> {
  ensureDataDir();
  const filePath = path.join(IMAGES_DIR, imageKey);
  const dirPath = path.dirname(filePath);
  
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  
  fs.writeFileSync(filePath, buffer);
  return filePath;
}

export function getImageUrl(imageKey: string): string {
  return `/local-images/${imageKey}`;
}
