// This is a placeholder file to prevent 404 errors during transition
// from NextAuth to Firebase Authentication
// In the future, this can be removed completely

export async function GET(request) {
  return new Response(JSON.stringify({ message: 'Using Firebase Authentication instead of NextAuth' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}

export async function POST(request) {
  return new Response(JSON.stringify({ message: 'Using Firebase Authentication instead of NextAuth' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}
