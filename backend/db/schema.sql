create extension if not exists pg_trgm;
create extension if not exists "uuid-ossp";

create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  plan_status text not null default 'internal' check (plan_status in ('internal','trial','active','suspended')),
  created_at timestamptz default now()
);

create table user_profiles (
  id uuid primary key references auth.users(id),
  organization_id uuid not null references organizations(id),
  role text not null check (role in ('super_admin','org_admin','viewer')),
  full_name text,
  created_at timestamptz default now()
);

create table industries (
  id uuid primary key default gen_random_uuid(),
  name_ar text,
  name_en text,
  slug text unique
);

create table companies (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id),
  name text not null,
  industry_id uuid references industries(id) on delete set null,
  duplicate_of uuid references companies(id) on delete set null,
  source_document text,
  source_page int,
  status text not null default 'pending_review' check (status in ('pending_review','verified','rejected')),
  confidence_score numeric,
  created_by uuid references auth.users(id),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table phone_numbers (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references companies(id) on delete cascade,
  number text not null,
  number_type text check (number_type in ('mobile','landline','unspecified')),
  is_primary boolean default false
);

create table addresses (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references companies(id) on delete cascade,
  address_text text,
  city text,
  governorate text
);

create table ingestion_jobs (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id),
  file_name text,
  file_type text check (file_type in ('pdf_scanned','pdf_text','excel','word')),
  extraction_tier text check (extraction_tier in ('tier_a','tier_b')),
  status text default 'queued' check (status in ('queued','processing','completed','failed')),
  total_pages int,
  entries_extracted int,
  entries_needing_review int,
  uploaded_by uuid references auth.users(id),
  uploaded_at timestamptz default now()
);

create table audit_log (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id),
  actor_id uuid references auth.users(id),
  action text not null,
  target_table text not null,
  target_id uuid not null,
  diff jsonb,
  created_at timestamptz default now()
);

create index idx_companies_name_trgm on companies using gin (name gin_trgm_ops);
create index idx_companies_org on companies (organization_id);
create index idx_companies_status on companies (status);
create index idx_companies_industry on companies (industry_id);
create index idx_companies_duplicate_of on companies (duplicate_of) where duplicate_of is not null;
create index idx_phone_company on phone_numbers (company_id);
create index idx_ingestion_jobs_org_status on ingestion_jobs (organization_id, status);
create index idx_audit_log_org on audit_log (organization_id, created_at desc);

alter table companies enable row level security;
create policy org_isolation_companies on companies
  using (organization_id = (select organization_id from user_profiles where id = auth.uid()));

alter table phone_numbers enable row level security;
create policy org_isolation_phones on phone_numbers
  using (company_id in (
    select id from companies
    where organization_id = (select organization_id from user_profiles where id = auth.uid())
  ));

alter table addresses enable row level security;
create policy org_isolation_addresses on addresses
  using (company_id in (
    select id from companies
    where organization_id = (select organization_id from user_profiles where id = auth.uid())
  ));

alter table ingestion_jobs enable row level security;
create policy org_isolation_jobs on ingestion_jobs
  using (organization_id = (select organization_id from user_profiles where id = auth.uid()));

alter table audit_log enable row level security;
create policy org_isolation_audit on audit_log
  using (organization_id = (select organization_id from user_profiles where id = auth.uid()));