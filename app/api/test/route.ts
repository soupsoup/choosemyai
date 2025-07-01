import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    message: 'API is working',
    timestamp: new Date().toISOString(),
    environment: {
      supabaseUrl: process.env.SUPABASE_URL ? 'Set' : 'Not set',
      supabaseKey: process.env.SUPABASE_ANON_KEY ? 'Set' : 'Not set'
    },
    version: 'v2.0 - Error handling update'
  })
} 