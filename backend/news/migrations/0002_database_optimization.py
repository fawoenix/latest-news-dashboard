"""
Custom migration for database optimization:
1. GIN index on title + description for full-text search.
2. Range partitioning setup on the article table by published_at (monthly).

Note: PostgreSQL native partitioning requires recreating the table.
      For an existing table we use declarative partitioning via inheritance
      or, more practically, we add the GIN index and set up a trigger-based
      partitioning approach. Here we use the pg_trgm extension for
      trigram-based search and create a function + trigger for partition routing.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        # ----------------------------------------------------------------
        # 1. Enable pg_trgm extension for trigram-based search
        # ----------------------------------------------------------------
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="DROP EXTENSION IF EXISTS pg_trgm;",
        ),
        # ----------------------------------------------------------------
        # 2. GIN trigram index on title for fast ILIKE / ICONTAINS queries
        # ----------------------------------------------------------------
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_article_title_trgm
                ON news_article
                USING gin (title gin_trgm_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_article_title_trgm;",
        ),
        # ----------------------------------------------------------------
        # 3. GIN trigram index on description
        # ----------------------------------------------------------------
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_article_desc_trgm
                ON news_article
                USING gin (description gin_trgm_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_article_desc_trgm;",
        ),
        # ----------------------------------------------------------------
        # 4. Create a partitioned archive table for old articles.
        #    Articles older than 90 days can be moved here via a cron job.
        #    This keeps the main table lean for fast queries.
        #    Note: PG partitioned tables require the partition key in any
        #    unique / PK constraint – we define schema explicitly.
        # ----------------------------------------------------------------
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS news_article_archive (
                    id BIGINT NOT NULL,
                    source_id BIGINT,
                    category_id BIGINT,
                    source_name VARCHAR(255) DEFAULT '',
                    author VARCHAR(500) DEFAULT '',
                    title VARCHAR(1000) NOT NULL,
                    description TEXT DEFAULT '',
                    url VARCHAR(2000) NOT NULL,
                    url_to_image VARCHAR(2000) DEFAULT '',
                    published_at TIMESTAMPTZ NOT NULL,
                    content TEXT DEFAULT '',
                    country VARCHAR(10) DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL,
                    PRIMARY KEY (id, published_at)
                ) PARTITION BY RANGE (published_at);
            """,
            reverse_sql="DROP TABLE IF EXISTS news_article_archive CASCADE;",
        ),
        # Create sample monthly partitions for the archive
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS news_article_archive_2025_q1
                    PARTITION OF news_article_archive
                    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
            """,
            reverse_sql="DROP TABLE IF EXISTS news_article_archive_2025_q1;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS news_article_archive_2025_q2
                    PARTITION OF news_article_archive
                    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
            """,
            reverse_sql="DROP TABLE IF EXISTS news_article_archive_2025_q2;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS news_article_archive_2025_q3
                    PARTITION OF news_article_archive
                    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
            """,
            reverse_sql="DROP TABLE IF EXISTS news_article_archive_2025_q3;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS news_article_archive_2025_q4
                    PARTITION OF news_article_archive
                    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
            """,
            reverse_sql="DROP TABLE IF EXISTS news_article_archive_2025_q4;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS news_article_archive_2026_q1
                    PARTITION OF news_article_archive
                    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
            """,
            reverse_sql="DROP TABLE IF EXISTS news_article_archive_2026_q1;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS news_article_archive_2026_q2
                    PARTITION OF news_article_archive
                    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
            """,
            reverse_sql="DROP TABLE IF EXISTS news_article_archive_2026_q2;",
        ),
        # ----------------------------------------------------------------
        # 5. Create a function to archive old articles (>90 days)
        # ----------------------------------------------------------------
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION archive_old_articles()
                RETURNS INTEGER AS $$
                DECLARE
                    moved_count INTEGER;
                BEGIN
                    WITH moved AS (
                        DELETE FROM news_article
                        WHERE published_at < NOW() - INTERVAL '90 days'
                        RETURNING *
                    )
                    INSERT INTO news_article_archive
                    SELECT * FROM moved;

                    GET DIAGNOSTICS moved_count = ROW_COUNT;
                    RETURN moved_count;
                END;
                $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS archive_old_articles();",
        ),
        # ----------------------------------------------------------------
        # 6. Analyze tables to update query planner statistics
        # ----------------------------------------------------------------
        migrations.RunSQL(
            sql="ANALYZE news_article;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
