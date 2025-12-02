#!/bin/bash

# Database initialization script for DIO Platform

set -e

echo "🗄️  Initializing DIO Platform Database..."

# Check if database directory exists
if [ ! -d "./db" ]; then
    echo "📁 Creating database directory..."
    mkdir -p ./db
fi

# Set proper permissions
chmod 755 ./db

# Check if database file exists
if [ ! -f "./db/app.db" ]; then
    echo "📄 Creating new database file..."
    touch ./db/app.db
fi

# Set proper permissions for database file
chmod 666 ./db/app.db

# Check if Prisma schema exists
if [ ! -f "./prisma/schema.prisma" ]; then
    echo "❌ Prisma schema not found!"
    exit 1
fi

echo "✅ Database initialization complete!"
echo "📊 Database location: ./db/app.db"
echo "🔗 Database URL: file:./db/app.db"