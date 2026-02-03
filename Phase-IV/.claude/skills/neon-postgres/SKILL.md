# Neon PostgreSQL Database Skill

## Overview
Specialized skill for working with Neon - a serverless PostgreSQL platform with autoscaling, branching, and modern developer experience. Focuses on Neon-specific features, connection patterns, and optimization strategies.

## Core Capabilities

### 1. Neon Connection Management
- Configure connection pooling with Neon
- Use connection strings correctly (pooled vs direct)
- Implement serverless-friendly connections
- Handle connection limits and pooling
- Configure SSL/TLS connections

### 2. Database Branching
- Create and manage database branches
- Use branches for development/staging/preview
- Implement branch-per-preview deployments
- Reset and delete branches
- Copy production data to branches

### 3. Serverless Optimization
- Optimize for cold starts
- Use Neon's autoscaling features
- Implement connection pooling for serverless
- Reduce connection overhead
- Handle scale-to-zero efficiently

### 4. Schema Management
- Design efficient database schemas
- Create indexes for query optimization
- Implement migrations with Drizzle/Prisma
- Use PostgreSQL features (JSON, arrays, full-text search)
- Manage schema versioning

## Neon-Specific Features

### Connection Strings
Neon provides two types of connection strings:

```typescript
// Pooled connection (recommended for serverless)
// Use with @neondatabase/serverless or connection poolers
DATABASE_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

// Direct connection (for long-running processes)
// Use for migrations, admin tasks
DATABASE_URL_UNPOOLED="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require&options=endpoint%3Dep-xxx"
```

### Environment Variables Setup
```bash
# .env or .env.local
DATABASE_URL="postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
DATABASE_URL_UNPOOLED="postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require&options=endpoint%3Dep-xxx"
```

## Connection Patterns

### Using @neondatabase/serverless (Recommended)
```typescript
// lib/db.ts
import { neon, neonConfig } from '@neondatabase/serverless'

// Enable for Vercel Edge/Cloudflare Workers
neonConfig.fetchConnectionCache = true

// Create a query function
export const sql = neon(process.env.DATABASE_URL!)

// Usage
const users = await sql`SELECT * FROM users WHERE id = ${userId}`
```

### Using with Drizzle ORM
```typescript
// lib/db.ts
import { drizzle } from 'drizzle-orm/neon-http'
import { neon } from '@neondatabase/serverless'

const sql = neon(process.env.DATABASE_URL!)
export const db = drizzle(sql)

// Define schema
import { pgTable, serial, text, timestamp, boolean } from 'drizzle-orm/pg-core'

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  passwordHash: text('password_hash').notNull(),
  emailVerified: boolean('email_verified').default(false),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
})

// Usage
import { db } from './db'
import { users } from './schema'
import { eq } from 'drizzle-orm'

const user = await db.select().from(users).where(eq(users.email, email))
```

### Using with Prisma
```typescript
// lib/db.ts
import { PrismaClient } from '@prisma/client'
import { Pool } from '@neondatabase/serverless'
import { PrismaNeon } from '@prisma/adapter-neon'

// Create connection pool
const pool = new Pool({ connectionString: process.env.DATABASE_URL })
const adapter = new PrismaNeon(pool)

// Create Prisma client
export const prisma = new PrismaClient({ adapter })

// Prisma schema.prisma
/*
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  name          String
  passwordHash  String
  emailVerified Boolean   @default(false)
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}
*/
```

### Using with node-postgres (pg)
```typescript
// lib/db.ts
import { Pool } from '@neondatabase/serverless'

const pool = new Pool({ 
  connectionString: process.env.DATABASE_URL,
  ssl: true,
})

export async function query(text: string, params?: any[]) {
  const start = Date.now()
  const res = await pool.query(text, params)
  const duration = Date.now() - start
  console.log('Executed query', { text, duration, rows: res.rowCount })
  return res
}

// Usage
const result = await query('SELECT * FROM users WHERE email = $1', [email])
```

### Using with Kysely
```typescript
// lib/db.ts
import { Kysely, PostgresDialect } from 'kysely'
import { Pool } from '@neondatabase/serverless'

interface Database {
  users: {
    id: number
    email: string
    name: string
    password_hash: string
    email_verified: boolean
    created_at: Date
    updated_at: Date
  }
}

export const db = new Kysely<Database>({
  dialect: new PostgresDialect({
    pool: new Pool({ connectionString: process.env.DATABASE_URL }),
  }),
})

// Usage
const users = await db
  .selectFrom('users')
  .selectAll()
  .where('email', '=', email)
  .execute()
```

## Database Branching Workflows

### Branch Management with Neon CLI
```bash
# Install Neon CLI
npm install -g neonctl

# Authenticate
neonctl auth

# List projects
neonctl projects list

# Create a new branch from main
neonctl branches create --project-id <project-id> --name dev

# Create branch for preview deployment
neonctl branches create --project-id <project-id> --name preview-pr-123

# List branches
neonctl branches list --project-id <project-id>

# Delete a branch
neonctl branches delete <branch-id> --project-id <project-id>

# Get connection string for a branch
neonctl connection-string <branch-id>
```

### Preview Deployments (Vercel Example)
```typescript
// scripts/create-preview-branch.ts
import { execSync } from 'child_process'

const branchName = `preview-${process.env.VERCEL_GIT_COMMIT_REF}`
const projectId = process.env.NEON_PROJECT_ID

// Create branch
const output = execSync(
  `neonctl branches create --project-id ${projectId} --name ${branchName} --parent main --output json`
)

const branch = JSON.parse(output.toString())

// Set environment variable for this deployment
console.log(`DATABASE_URL=${branch.connection_uri}`)
```

### GitHub Actions Integration
```yaml
# .github/workflows/preview.yml
name: Create Preview Branch

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  create-branch:
    runs-on: ubuntu-latest
    steps:
      - name: Create Neon Branch
        id: create-branch
        uses: neondatabase/create-branch-action@v4
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          branch_name: preview/pr-${{ github.event.pull_request.number }}
          api_key: ${{ secrets.NEON_API_KEY }}
          
      - name: Run migrations
        run: |
          DATABASE_URL=${{ steps.create-branch.outputs.db_url }} npm run migrate
```

## Migration Strategies

### Drizzle Migrations
```typescript
// drizzle.config.ts
import type { Config } from 'drizzle-kit'

export default {
  schema: './lib/schema.ts',
  out: './drizzle/migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL_UNPOOLED!,
  },
} satisfies Config

// package.json scripts
{
  "db:generate": "drizzle-kit generate:pg",
  "db:migrate": "drizzle-kit push:pg",
  "db:studio": "drizzle-kit studio"
}
```

### Prisma Migrations
```bash
# Generate migration
DATABASE_URL_UNPOOLED="..." npx prisma migrate dev --name init

# Apply migrations in production
DATABASE_URL_UNPOOLED="..." npx prisma migrate deploy

# Generate Prisma Client
npx prisma generate
```

### Custom SQL Migrations
```typescript
// migrations/001_init.sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

// migrations/run.ts
import { Pool } from '@neondatabase/serverless'
import fs from 'fs'
import path from 'path'

const pool = new Pool({ connectionString: process.env.DATABASE_URL_UNPOOLED })

async function runMigrations() {
  const migrationsDir = path.join(__dirname, 'migrations')
  const files = fs.readdirSync(migrationsDir)
    .filter(f => f.endsWith('.sql'))
    .sort()

  for (const file of files) {
    const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf8')
    console.log(`Running migration: ${file}`)
    await pool.query(sql)
  }
}

runMigrations()
```

## Performance Optimization

### Connection Pooling Best Practices
```typescript
// For serverless functions, use singleton pattern
import { Pool } from '@neondatabase/serverless'

declare global {
  var pgPool: Pool | undefined
}

let pool: Pool

if (process.env.NODE_ENV === 'production') {
  pool = new Pool({ connectionString: process.env.DATABASE_URL })
} else {
  if (!global.pgPool) {
    global.pgPool = new Pool({ connectionString: process.env.DATABASE_URL })
  }
  pool = global.pgPool
}

export { pool }
```

### Query Optimization
```typescript
// Use indexes effectively
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

// Composite indexes for common queries
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);

// Partial indexes for filtered queries
CREATE INDEX idx_active_users ON users(email) WHERE email_verified = true;

// Use EXPLAIN ANALYZE to check query performance
const result = await sql`
  EXPLAIN ANALYZE
  SELECT * FROM posts 
  WHERE user_id = ${userId} 
  ORDER BY created_at DESC 
  LIMIT 10
`
```

### Full-Text Search
```typescript
// Add tsvector column
ALTER TABLE posts ADD COLUMN search_vector tsvector;

// Create index
CREATE INDEX idx_posts_search ON posts USING GIN(search_vector);

// Update trigger to maintain search vector
CREATE TRIGGER posts_search_update 
BEFORE INSERT OR UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);

// Search query
const posts = await sql`
  SELECT * FROM posts
  WHERE search_vector @@ plainto_tsquery('english', ${searchTerm})
  ORDER BY ts_rank(search_vector, plainto_tsquery('english', ${searchTerm})) DESC
  LIMIT 20
`
```

### JSONB for Flexible Data
```typescript
// Schema with JSONB
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

// Create index on JSONB fields
CREATE INDEX idx_products_metadata ON products USING GIN(metadata);

// Query JSONB
const products = await sql`
  SELECT * FROM products
  WHERE metadata->>'category' = ${category}
  AND (metadata->'price')::numeric < ${maxPrice}
`

// Update JSONB field
await sql`
  UPDATE products
  SET metadata = metadata || '{"featured": true}'::jsonb
  WHERE id = ${productId}
`
```

## Security Best Practices

### Row-Level Security (RLS)
```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policy for users to see only their own posts
CREATE POLICY user_posts_policy ON posts
  FOR SELECT
  USING (user_id = current_setting('app.user_id')::integer);

-- Policy for inserting posts
CREATE POLICY user_insert_policy ON posts
  FOR INSERT
  WITH CHECK (user_id = current_setting('app.user_id')::integer);

-- Set user context in application
await sql`SET app.user_id = ${userId}`
```

### Prepared Statements (SQL Injection Prevention)
```typescript
// Always use parameterized queries
// ✅ CORRECT
const user = await sql`
  SELECT * FROM users WHERE email = ${email}
`

// ❌ WRONG - vulnerable to SQL injection
const user = await sql`SELECT * FROM users WHERE email = '${email}'`

// With node-postgres
const result = await pool.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
)
```

### Database Encryption
```sql
-- Use pgcrypto for sensitive data
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE sensitive_data (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  encrypted_ssn BYTEA,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert encrypted data
INSERT INTO sensitive_data (user_id, encrypted_ssn)
VALUES (1, pgp_sym_encrypt('123-45-6789', 'encryption-key'));

-- Query encrypted data
SELECT id, user_id, pgp_sym_decrypt(encrypted_ssn, 'encryption-key') as ssn
FROM sensitive_data
WHERE user_id = 1;
```

## Monitoring & Debugging

### Query Logging
```typescript
// Enable query logging in development
import { drizzle } from 'drizzle-orm/neon-http'

export const db = drizzle(sql, {
  logger: process.env.NODE_ENV === 'development',
})

// Custom logger
const customLogger = {
  logQuery(query: string, params: unknown[]) {
    console.log('[DB Query]', { query, params, timestamp: new Date() })
  },
}

export const db = drizzle(sql, { logger: customLogger })
```

### Performance Monitoring
```typescript
// Measure query execution time
async function queryWithMetrics<T>(
  queryFn: () => Promise<T>,
  queryName: string
): Promise<T> {
  const start = Date.now()
  try {
    const result = await queryFn()
    const duration = Date.now() - start
    
    console.log(`[${queryName}] completed in ${duration}ms`)
    
    // Send to monitoring service
    if (duration > 1000) {
      console.warn(`[${queryName}] slow query: ${duration}ms`)
    }
    
    return result
  } catch (error) {
    const duration = Date.now() - start
    console.error(`[${queryName}] failed after ${duration}ms:`, error)
    throw error
  }
}

// Usage
const users = await queryWithMetrics(
  () => db.select().from(users).where(eq(users.email, email)),
  'getUserByEmail'
)
```

## Common Patterns

### Transactions
```typescript
// Drizzle transactions
await db.transaction(async (tx) => {
  const user = await tx.insert(users).values({
    email: 'user@example.com',
    name: 'John Doe',
  }).returning()

  await tx.insert(profiles).values({
    userId: user[0].id,
    bio: 'Hello world',
  })
})

// node-postgres transactions
const client = await pool.connect()
try {
  await client.query('BEGIN')
  
  const userResult = await client.query(
    'INSERT INTO users(email, name) VALUES($1, $2) RETURNING id',
    ['user@example.com', 'John Doe']
  )
  
  await client.query(
    'INSERT INTO profiles(user_id, bio) VALUES($1, $2)',
    [userResult.rows[0].id, 'Hello world']
  )
  
  await client.query('COMMIT')
} catch (e) {
  await client.query('ROLLBACK')
  throw e
} finally {
  client.release()
}
```

### Pagination
```typescript
// Cursor-based pagination
async function getPosts(cursor?: number, limit = 20) {
  let query = db
    .select()
    .from(posts)
    .orderBy(desc(posts.createdAt))
    .limit(limit + 1)

  if (cursor) {
    query = query.where(lt(posts.id, cursor))
  }

  const results = await query
  const hasMore = results.length > limit
  const items = hasMore ? results.slice(0, -1) : results

  return {
    items,
    nextCursor: hasMore ? items[items.length - 1].id : null,
  }
}

// Offset-based pagination
async function getPostsOffset(page = 1, pageSize = 20) {
  const offset = (page - 1) * pageSize

  const [items, countResult] = await Promise.all([
    db.select().from(posts).limit(pageSize).offset(offset),
    db.select({ count: sql<number>`count(*)` }).from(posts),
  ])

  return {
    items,
    total: countResult[0].count,
    page,
    pageSize,
    totalPages: Math.ceil(countResult[0].count / pageSize),
  }
}
```

### Soft Deletes
```typescript
// Add deleted_at column
ALTER TABLE posts ADD COLUMN deleted_at TIMESTAMP;

// Soft delete implementation
export async function softDelete(id: number) {
  return db
    .update(posts)
    .set({ deletedAt: new Date() })
    .where(eq(posts.id, id))
}

// Query only non-deleted records
export async function getPosts() {
  return db
    .select()
    .from(posts)
    .where(isNull(posts.deletedAt))
}

// Restore soft-deleted record
export async function restore(id: number) {
  return db
    .update(posts)
    .set({ deletedAt: null })
    .where(eq(posts.id, id))
}
```

## Testing

### Test Database Setup
```typescript
// tests/setup.ts
import { sql } from '@neondatabase/serverless'

export async function setupTestDb() {
  // Use a separate test database or branch
  const testSql = neon(process.env.DATABASE_URL_TEST!)
  
  // Run migrations
  await testSql`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) UNIQUE NOT NULL,
      name VARCHAR(255) NOT NULL
    )
  `
  
  return testSql
}

export async function cleanupTestDb(testSql: ReturnType<typeof neon>) {
  await testSql`TRUNCATE TABLE users RESTART IDENTITY CASCADE`
}
```

## Backup & Recovery

### Using Neon Branches for Backups
```bash
# Create a backup branch before major changes
neonctl branches create \
  --project-id <project-id> \
  --name backup-$(date +%Y%m%d-%H%M%S) \
  --parent main

# Restore from branch if needed
neonctl branches promote <backup-branch-id> --project-id <project-id>
```

---

**When to use this skill:**
- Building applications with Neon PostgreSQL
- Implementing database branching workflows
- Optimizing serverless database connections
- Setting up preview environments
- Managing database migrations
- Implementing complex queries and indexes
- Building scalable database architectures
- Setting up monitoring and performance tracking