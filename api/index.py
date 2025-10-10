# This file serves as the serverless function entry point for Vercel.
from app import create_app

app = create_app()