#!/usr/bin/env python3
"""
Noumi API Server Startup Script
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Noumi API Server...")
    print("📚 API Documentation will be available at:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("💡 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    ) 