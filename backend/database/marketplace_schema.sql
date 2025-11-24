-- Marketplace Infrastructure Database Schema
-- Supports both asset-based ("what we have") and capability-based ("what we can do") listings

-- Product/Service Listings
CREATE TABLE IF NOT EXISTS marketplace_listings (
    id SERIAL PRIMARY KEY,
    listing_id VARCHAR(255) UNIQUE NOT NULL,
    seller_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    listing_type VARCHAR(50) NOT NULL,  -- asset, capability, combined
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    asset_details JSONB,
    capability_details JSONB,
    pricing JSONB NOT NULL,
    valuation JSONB,  -- Calculated value breakdown
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    checkpoint_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_listings_seller ON marketplace_listings(seller_id);
CREATE INDEX idx_listings_type ON marketplace_listings(listing_type);
CREATE INDEX idx_listings_status ON marketplace_listings(status);
CREATE INDEX idx_listings_created ON marketplace_listings(created_at DESC);

-- Transactions
CREATE TABLE IF NOT EXISTS marketplace_transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    buyer_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    seller_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    listing_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    platform_fee DECIMAL(10, 2) NOT NULL,
    seller_payout DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_provider_transaction_id VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewer_id VARCHAR(255),
    checkpoint_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_transactions_buyer ON marketplace_transactions(buyer_id);
CREATE INDEX idx_transactions_seller ON marketplace_transactions(seller_id);
CREATE INDEX idx_transactions_status ON marketplace_transactions(status);
CREATE INDEX idx_transactions_created ON marketplace_transactions(created_at DESC);

-- Escrow Accounts
CREATE TABLE IF NOT EXISTS escrow_accounts (
    id SERIAL PRIMARY KEY,
    escrow_id VARCHAR(255) UNIQUE NOT NULL,
    buyer_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    seller_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    transaction_id VARCHAR(255) REFERENCES marketplace_transactions(transaction_id),
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'held',
    release_conditions JSONB NOT NULL,
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewer_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP
);

CREATE INDEX idx_escrow_buyer ON escrow_accounts(buyer_id);
CREATE INDEX idx_escrow_seller ON escrow_accounts(seller_id);
CREATE INDEX idx_escrow_status ON escrow_accounts(status);

-- Orders
CREATE TABLE IF NOT EXISTS marketplace_orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(255) UNIQUE NOT NULL,
    transaction_id VARCHAR(255) NOT NULL REFERENCES marketplace_transactions(transaction_id),
    buyer_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    seller_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    listing_id VARCHAR(255) NOT NULL,
    order_details JSONB NOT NULL,
    delivery_type VARCHAR(50) NOT NULL,  -- digital, physical, service
    delivery_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    tracking_info JSONB,
    human_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP
);

CREATE INDEX idx_orders_buyer ON marketplace_orders(buyer_id);
CREATE INDEX idx_orders_seller ON marketplace_orders(seller_id);
CREATE INDEX idx_orders_status ON marketplace_orders(delivery_status);

-- Disputes
CREATE TABLE IF NOT EXISTS marketplace_disputes (
    id SERIAL PRIMARY KEY,
    dispute_id VARCHAR(255) UNIQUE NOT NULL,
    transaction_id VARCHAR(255) NOT NULL REFERENCES marketplace_transactions(transaction_id),
    order_id VARCHAR(255) REFERENCES marketplace_orders(order_id),
    initiator_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    human_reviewer_id VARCHAR(255),
    resolution TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disputes_transaction ON marketplace_disputes(transaction_id);
CREATE INDEX idx_disputes_status ON marketplace_disputes(status);

-- Seller Profiles (Marketplace-specific)
CREATE TABLE IF NOT EXISTS seller_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES anonymous_users(id) ON DELETE CASCADE,
    business_name VARCHAR(255),
    business_type VARCHAR(50),  -- llc, sole_proprietor
    verification_status VARCHAR(50) NOT NULL DEFAULT 'unverified',
    total_sales DECIMAL(10, 2) NOT NULL DEFAULT 0,
    total_transactions INTEGER NOT NULL DEFAULT 0,
    rating DECIMAL(3, 2),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_seller_profiles_user ON seller_profiles(user_id);
CREATE INDEX idx_seller_profiles_verification ON seller_profiles(verification_status);

