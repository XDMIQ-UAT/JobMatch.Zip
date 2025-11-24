-- Migration: Add longevity prediction fields to matches table
-- Date: 2025-11-23
-- Description: Adds fields to track longevity predictions for job matches

-- Add longevity tracking columns to matches table
ALTER TABLE matches
ADD COLUMN IF NOT EXISTS compatibility_score INTEGER,
ADD COLUMN IF NOT EXISTS longevity_score INTEGER,
ADD COLUMN IF NOT EXISTS predicted_months INTEGER,
ADD COLUMN IF NOT EXISTS longevity_factors JSONB;

-- Add comments for documentation
COMMENT ON COLUMN matches.compatibility_score IS 'Immediate skill compatibility score (0-100)';
COMMENT ON COLUMN matches.longevity_score IS 'Predicted engagement longevity score (0-100)';
COMMENT ON COLUMN matches.predicted_months IS 'Predicted engagement duration in months';
COMMENT ON COLUMN matches.longevity_factors IS 'Contributing factors to longevity prediction';
COMMENT ON COLUMN matches.match_score IS 'Final combined score: compatibility (40%) + longevity (60%)';

-- Create index for sorting by longevity
CREATE INDEX IF NOT EXISTS idx_matches_longevity ON matches(longevity_score DESC, predicted_months DESC);

-- Update existing matches to have compatibility_score equal to match_score
-- (for backward compatibility with existing data)
UPDATE matches 
SET compatibility_score = match_score,
    longevity_score = match_score,
    predicted_months = CASE 
        WHEN match_score >= 90 THEN 36
        WHEN match_score >= 75 THEN 24
        WHEN match_score >= 60 THEN 18
        WHEN match_score >= 45 THEN 12
        WHEN match_score >= 30 THEN 6
        ELSE 3
    END
WHERE compatibility_score IS NULL;
