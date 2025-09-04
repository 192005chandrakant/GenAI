import NextAuth from 'next-auth';
import { authOptions as nextAuthOptions } from '@/lib/auth';

// Use the authOptions from our centralized config
export const authOptions = nextAuthOptions;

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
