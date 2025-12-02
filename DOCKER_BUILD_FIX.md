# Docker Build Fix Instructions

## Issue Fixed

The Docker build was failing because:
1. The runner stage was trying to install production dependencies while also copying node_modules from deps stage
2. This created a conflict where package.json wasn't available during the npm install

## Solution Applied

### Updated Dockerfile.frontend

```dockerfile
# Production Dockerfile for Frontend
FROM node:18-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm install

# Copy source code
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

# Install Prisma CLI for production
RUN npm install -g prisma

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application and dependencies
COPY --from=deps /app/.next ./.next
COPY --from=deps /app/public ./public
COPY --from=deps /app/prisma ./prisma
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/node_modules ./node_modules

# Set permissions
RUN mkdir -p db && chown -R nextjs:nodejs db

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"
ENV NODE_ENV=production

CMD ["npm", "start"]
```

### Key Changes Made

1. **Removed redundant npm install**: The runner stage no longer tries to install production dependencies since we're copying the complete node_modules from the deps stage
2. **Maintained dependency copying**: We still copy node_modules from the deps stage to ensure all dependencies are available
3. **Kept Prisma CLI installation**: Still needed for production database operations

## Build Commands

### Production Build
```bash
docker compose --profile production up -d --build
```

### Development Build
```bash
docker compose --profile development up -d --build
```

### Manual Build Test
```bash
docker build -f Dockerfile.frontend -t dio-frontend .
```

## Expected Output

The build should now complete successfully with output similar to:
```
[+] Building 3.5s (50/50) ✓
 => [frontend internal] load build definition from Dockerfile.frontend
 => => transferring context: 984.82kB
 => => [frontend deps 1/7] FROM docker.io/library/node:18-alpine
 => => [frontend deps 2/7] WORKDIR /app
 => => [frontend deps 3/7] COPY package.json package-lock.json ./
 => => [frontend deps 4/7] RUN npm install
 => => [frontend deps 5/7] COPY . .
 => => [frontend deps 6/7] RUN npx prisma generate
 => => [frontend deps 7/7] RUN npm run build
 => => [frontend runner 1/11] FROM docker.io/library/node:18-alpine
 => => [frontend runner 2/11] WORKDIR /app
 => => [frontend runner 3/11] RUN npm install -g prisma
 => => [frontend runner 4/11] RUN addgroup --system --gid 1001 nodejs
 => => [frontend runner 5/11] RUN adduser --system --uid 1001 nextjs
 => => [frontend runner 6/11] COPY --from=deps /app/.next ./.next
 => => [frontend runner 7/11] COPY --from=deps /app/public ./public
 => => [frontend runner 8/11] COPY --from=deps /app/prisma ./prisma
 => => [frontend runner 9/11] COPY --from=deps /app/package.json ./package.json
 => => [frontend runner 10/11] COPY --from=deps /app/node_modules ./node_modules
 => => [frontend runner 11/11] RUN mkdir -p db && chown -R nextjs:nodejs db
 => => [frontend runner] exporting to image
 => => => exporting layers
 => => => writing image
 => => => naming to docker.io/library/dio-frontend
```

## Verification

After the build completes successfully, you can verify the container is running:

```bash
# Check container status
docker compose ps

# View logs
docker compose logs frontend

# Test the application
curl http://localhost:3000
```

## Troubleshooting

If you still encounter issues:

1. **Clean build cache**:
   ```bash
   docker system prune -f
   docker compose down --volumes
   docker compose --profile production up -d --build
   ```

2. **Check file permissions**:
   ```bash
   ls -la Dockerfile.frontend
   ```

3. **Verify package.json exists**:
   ```bash
   cat package.json | head -5
   ```

4. **Manual build test**:
   ```bash
   docker build -f Dockerfile.frontend -t test-frontend .
   docker run -p 3000:3000 test-frontend
   ```

## Next Steps

Once the build is successful:

1. **Access the dashboard**: http://localhost:3000
2. **Check API endpoints**: http://localhost:3000/api/agents
3. **Monitor agent registration**: Check logs for agent connections
4. **Test attack simulator**: Use the attack.sh script

The DIO Platform should now be fully operational with all the fixes applied:
- ✅ Agent connection reliability
- ✅ Configurable agent counts
- ✅ Dark theme functionality
- ✅ Real-time threat detection
- ✅ Production-ready deployment