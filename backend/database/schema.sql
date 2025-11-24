-- Database schema for AI-Enabled LLC Matching Platform
-- Supports sharding, partitioning, and state recovery

-- Anonymous Users (shardable by user_id)
CREATE TABLE IF NOT EXISTS anonymous_users (
    id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_anonymous_users_created ON anonymous_users(created_at);
CREATE INDEX idx_anonymous_users_active ON anonymous_users(last_active);

-- LLC Profiles (shardable by user_id)
CREATE TABLE IF NOT EXISTS llc_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    skills JSONB NOT NULL,
    projects JSONB,
    experience_summary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_llc_profiles_user ON llc_profiles(user_id);
CREATE INDEX idx_llc_profiles_skills ON llc_profiles USING GIN(skills);

-- Capability Assessments (with checkpoints)
CREATE TABLE IF NOT EXISTS capability_assessments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL,
    results JSONB NOT NULL,
    checkpoint_id INTEGER,
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    human_reviewer_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessments_user ON capability_assessments(user_id);
CREATE INDEX idx_assessments_type ON capability_assessments(assessment_type);
CREATE INDEX idx_assessments_checkpoint ON capability_assessments(checkpoint_id);

-- Job Postings
CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills JSONB NOT NULL,
    preferred_skills JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_job_postings_active ON job_postings(active);
CREATE INDEX idx_job_postings_skills ON job_postings USING GIN(required_skills);

-- Matches (with human review flags and checkpoints)
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    job_posting_id INTEGER NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    match_score INTEGER NOT NULL,
    match_reasons JSONB,
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    human_reviewer_id VARCHAR(255),
    human_feedback TEXT,
    checkpoint_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_matches_user ON matches(user_id);
CREATE INDEX idx_matches_job ON matches(job_posting_id);
CREATE INDEX idx_matches_user_job ON matches(user_id, job_posting_id);
CREATE INDEX idx_matches_score ON matches(match_score DESC);
CREATE INDEX idx_matches_checkpoint ON matches(checkpoint_id);

-- State Snapshots (for recovery)
CREATE TABLE IF NOT EXISTS state_snapshots (
    id SERIAL PRIMARY KEY,
    checkpoint_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    state_data JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

CREATE INDEX idx_snapshots_type ON state_snapshots(checkpoint_type);
CREATE INDEX idx_snapshots_entity ON state_snapshots(entity_id);
CREATE INDEX idx_snapshots_created ON state_snapshots(created_at DESC);

-- Human Reviews
CREATE TABLE IF NOT EXISTS human_reviews (
    id SERIAL PRIMARY KEY,
    review_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    reviewer_id VARCHAR(255) NOT NULL,
    decision VARCHAR(50) NOT NULL,
    feedback TEXT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_type ON human_reviews(review_type);
CREATE INDEX idx_reviews_entity ON human_reviews(entity_id);
CREATE INDEX idx_reviews_reviewer ON human_reviews(reviewer_id);

-- Articulation Suggestions (versioned)
CREATE TABLE IF NOT EXISTS articulation_suggestions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    suggested_text TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    checkpoint_id INTEGER,
    human_refined BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_articulation_user ON articulation_suggestions(user_id);
CREATE INDEX idx_articulation_checkpoint ON articulation_suggestions(checkpoint_id);

-- Forum Posts (partitioned by date for scalability)
CREATE TABLE IF NOT EXISTS forum_posts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    forum_topic VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    parent_post_id INTEGER REFERENCES forum_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forum_topic ON forum_posts(forum_topic);
CREATE INDEX idx_forum_user ON forum_posts(user_id);
CREATE INDEX idx_forum_created ON forum_posts(created_at DESC);
CREATE INDEX idx_forum_parent ON forum_posts(parent_post_id);

-- Referrals (for viral growth)
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    referrer_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    referred_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    referral_code VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX idx_referrals_referred ON referrals(referred_id);
CREATE INDEX idx_referrals_code ON referrals(referral_code);

-- Applications (anonymous job applications)
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    job_posting_id INTEGER NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    match_id INTEGER REFERENCES matches(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_job ON applications(job_posting_id);
CREATE INDEX idx_applications_match ON applications(match_id);

-- AI Moderation Log (time-series optimized)
CREATE TABLE IF NOT EXISTS ai_moderation_log (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    flagged_reasons JSONB,
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    decision VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_moderation_type ON ai_moderation_log(content_type);
CREATE INDEX idx_moderation_content ON ai_moderation_log(content_id);
CREATE INDEX idx_moderation_created ON ai_moderation_log(created_at DESC);

-- Bias Reports (community-reported bias incidents)
CREATE TABLE IF NOT EXISTS bias_reports (
    id SERIAL PRIMARY KEY,
    reporter_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    bias_type VARCHAR(50) NOT NULL,
    description TEXT,
    checkpoint_id INTEGER,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bias_reports_type ON bias_reports(content_type);
CREATE INDEX idx_bias_reports_resolved ON bias_reports(resolved);

-- Conversations (for storing assessment and other chat flows)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) REFERENCES anonymous_users(id) ON DELETE SET NULL,
    conversation_type VARCHAR(50) NOT NULL DEFAULT 'assessment',
    messages JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);


