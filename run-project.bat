@echo off
:: Replace the line below with your actual Supabase Connection String (Transaction Pooler or Session Pooler URI)
set DATABASE_URL=postgresql://postgres.ryewzzdytcehcizcqshc:aadhihdya2905@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require

echo Starting Bangalore Luxury Salon Finder on Supabase...
.\venv\Scripts\python.exe app.py
pause
