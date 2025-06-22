#!/usr/bin/env python3
"""
Simple test script to start the FastAPI server
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Noumi API Server...")
    print("📍 Current working directory:", sys.path[0])
    
    try:
        print("📚 API Documentation will be available at:")
        print("   - Swagger UI: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
        print("   - API Root: http://localhost:8000/")
        print("💡 Press Ctrl+C to stop the server")
        print("🔄 Starting server now...")
        
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1) 