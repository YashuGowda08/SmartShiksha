# SmartShiksha — Task Tracking

## Current Status
- Backend: FastAPI running on SQLite (verified healthy, 99 subjects, 39 tests)
- Frontend: Next.js 16, 15/15 pages compiling
- Multi-DB: sqlite/postgres/mongodb switching implemented
- Docker: 4 profiles (sqlite, postgres, mongodb, full)

## Completed (Previous Sessions)
- [x] MongoDB → SQLite migration
- [x] Fix all frontend compilation errors
- [x] Create missing lib files (api.ts, i18n.ts, offline-db.ts)
- [x] Fix dashboard 404 race condition
- [x] Multi-database support (sqlite/postgres/mongodb)
- [x] Docker multi-profile compose
- [x] MongoSession adapter for MongoDB compatibility
- [x] Verify SQLite mode (health, subjects, mock-tests endpoints)

## Pending
- [ ] Root .env is stale (old MongoDB config) — sync with backend/.env
- [ ] Test PostgreSQL mode (requires running instance)
- [ ] Test MongoDB mode (requires running instance)
- [ ] Docker build verification
