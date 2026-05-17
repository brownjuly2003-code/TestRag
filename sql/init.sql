create extension if not exists vector;
create extension if not exists pgcrypto;

create schema if not exists n8n;

create table if not exists documents (
    id uuid primary key default gen_random_uuid(),
    file_name text not null,
    source_url text,
    document_type text,
    document_date date,
    created_at timestamptz not null default now()
);

create table if not exists document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid references documents(id) on delete cascade,
    chunk_index integer not null,
    content text not null,
    section text,
    metadata jsonb not null default '{}'::jsonb,
    embedding vector(1024),
    search_vector tsvector generated always as (to_tsvector('russian', content)) stored,
    created_at timestamptz not null default now()
);

create index if not exists document_chunks_embedding_idx
    on document_chunks using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

create index if not exists document_chunks_search_vector_idx
    on document_chunks using gin (search_vector);

create table if not exists request_logs (
    id uuid primary key default gen_random_uuid(),
    telegram_user_id text,
    question text not null,
    request_type text,
    confidence numeric,
    refused boolean not null default false,
    answer text,
    sources jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists answer_feedback (
    id uuid primary key default gen_random_uuid(),
    request_log_id uuid references request_logs(id) on delete set null,
    telegram_user_id text,
    rating text not null,
    comment text,
    created_at timestamptz not null default now()
);

alter table answer_feedback add column if not exists category text;
alter table answer_feedback add column if not exists free_text text;
alter table answer_feedback add column if not exists chunk_ids jsonb not null default '[]'::jsonb;

create table if not exists review_queue (
    id uuid primary key default gen_random_uuid(),
    request_log_id uuid references request_logs(id) on delete cascade,
    reason text not null,
    status text not null default 'new',
    created_at timestamptz not null default now()
);

alter table review_queue add column if not exists context jsonb not null default '[]'::jsonb;

-- Sprint 4 prep (2026-05-17): versioning metadata для документов (HR/legal требование актуальности нормы).
alter table documents add column if not exists version text not null default 'v1';
alter table documents add column if not exists effective_from date;
alter table documents add column if not exists effective_to date;
alter table documents add column if not exists status text not null default 'active'
    check (status in ('active', 'superseded', 'draft'));

-- Observability: latency, tokens, model для каждого /ask запроса.
alter table request_logs add column if not exists latency_ms integer;
alter table request_logs add column if not exists llm_model text;
alter table request_logs add column if not exists prompt_tokens integer;
alter table request_logs add column if not exists completion_tokens integer;
