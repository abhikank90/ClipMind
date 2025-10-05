# ClipMind Database

## Schema Overview

### Tables

1. **users** - User accounts
2. **projects** - Video organization
3. **videos** - Uploaded videos
4. **clips** - Video segments with AI metadata
5. **compilations** - Video compilations
6. **compilation_clips** - Junction table

## Relationships

```
User (1) ─── (N) Videos
User (1) ─── (N) Projects
User (1) ─── (N) Compilations
Project (1) ─── (N) Videos
Video (1) ─── (N) Clips
Compilation (N) ─── (N) Clips (via compilation_clips)
```

## Running Migrations

### Create a new migration
```bash
./scripts/create_migration.sh "add new column"
```

### Run pending migrations
```bash
./scripts/run_migrations.sh
```

### View migration status
```bash
cd backend
poetry run alembic current
poetry run alembic history
```

## Database Initialization

### First time setup
```bash
cd backend
poetry run alembic upgrade head
```

### Reset database (WARNING: deletes all data)
```bash
./scripts/reset_db.sh
```

## Models

All SQLAlchemy models are in `app/models/`:
- `user.py` - User model
- `video.py` - Video model
- `clip.py` - Clip model
- `project.py` - Project model
- `compilation.py` - Compilation and CompilationClip models
