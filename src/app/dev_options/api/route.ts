// src/app/dev_options/api/route.ts
import { MongoClient } from 'mongodb';
import { NextRequest, NextResponse } from 'next/server';

const DB_NAME = 'resultreport';
const COLLECTION_NAME = 'result27Y';

const uri =
  'mongodb://resultreport-admin:a7kjzyALwazGrWxyYPJ2kUgP@resultreport-0.resultreport-svc.mongodb.svc.cluster.local:27017/admin?replicaSet=resultreport&ssl=false';

let client: MongoClient | undefined;

async function getClient() {
  if (!client) {
    client = new MongoClient(uri);
    await client.connect();
  }
  return client;
}

export async function GET(req: NextRequest) {
  if (!uri) {
    return new Response('MONGODB_URI environment variable is missing', { status: 500 });
  }

  try {
    const mongoClient = await getClient();
    const db = mongoClient.db(DB_NAME);
    const collection = db.collection(COLLECTION_NAME);

    // 1. If 'mode=history', return previous existing documents as JSON
    const searchParams = req.nextUrl.searchParams;
    if (searchParams.get('mode') === 'history') {
      const limit = parseInt(searchParams.get('limit') || '20', 10);
      const historyDocs = await collection.find({}).sort({ _id: -1 }).limit(limit).toArray();
      return NextResponse.json({ history: historyDocs });
    }

    // 2. Otherwise, return the SSE Live Change Stream
    const stream = new ReadableStream({
      async start(controller) {
        const sendSSE = (event: string, data: any) => {
          const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
          controller.enqueue(new TextEncoder().encode(payload));
        };

        const initialCount = await collection.estimatedDocumentCount();
        sendSSE('init', { totalDocuments: initialCount });

        const changeStream = collection.watch([], { fullDocument: 'updateLookup' });

        changeStream.on('change', (change) => {
          sendSSE('change', change);
        });

        changeStream.on('error', (err) => {
          console.error('MongoDB Change Stream Error:', err);
        });

        req.signal.addEventListener('abort', () => {
          changeStream.close();
        });
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
      },
    });
  } catch (err: any) {
    console.error('Failed to handle route request:', err);
    return new Response(`Database Error: ${err.message}`, { status: 500 });
  }
}