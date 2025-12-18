-- ================================
-- TABELLA GIOCATORI
-- ================================
CREATE TABLE players (
    player_tag TEXT PRIMARY KEY,

    player_name TEXT,
    clan_name TEXT,

    trophies INTEGER,
    arena TEXT,
    rank TEXT,

    wins INTEGER,
    losses INTEGER,
    three_crown_wins INTEGER,
    total_games INTEGER,

    account_age_seconds INTEGER,
    time_spent_seconds INTEGER,
    games_per_day REAL,

    last_updated DATETIME
);


-- ================================
-- TABELLA CARTE
-- ================================
CREATE TABLE IF NOT EXISTS cards (
    card_name TEXT PRIMARY KEY,
    rarity TEXT CHECK(rarity IN ('Common', 'Rare', 'Epic', 'Legendary', 'Champion')) NOT NULL DEFAULT 'Common',
    type TEXT CHECK(type IN ('Normal', 'Champion', 'Tower')) NOT NULL DEFAULT 'Normal',
    elixir_cost INTEGER DEFAULT 0,
    is_hero INTEGER DEFAULT 0 CHECK(is_hero IN (0,1)),
    is_evolved INTEGER DEFAULT 0 CHECK(is_evolved IN (0,1))
);

-- Trigger per impedire che una carta di tipo tower sia eroe o evoluta
CREATE TRIGGER IF NOT EXISTS trg_tower_no_hero_evolved
BEFORE INSERT ON cards
FOR EACH ROW
WHEN NEW.type = 'tower'
BEGIN
    SELECT
    CASE
        WHEN NEW.is_hero = 1 OR NEW.is_evolved = 1 THEN
            RAISE(ABORT, 'Una carta tower non può essere eroe né evoluta')
    END;
END;

CREATE TRIGGER IF NOT EXISTS trg_tower_no_hero_evolved_update
BEFORE UPDATE ON cards
FOR EACH ROW
WHEN NEW.type = 'tower'
BEGIN
    SELECT
    CASE
        WHEN NEW.is_hero = 1 OR NEW.is_evolved = 1 THEN
            RAISE(ABORT, 'Una carta tower non può essere eroe né evoluta')
    END;
END;

-- Trigger per impedire che una carta di tipo champion sia eroe o evoluta
CREATE TRIGGER IF NOT EXISTS trg_champion_no_hero_evolved
BEFORE INSERT ON cards
FOR EACH ROW
WHEN NEW.type = 'champion'
BEGIN
    SELECT
    CASE
        WHEN NEW.is_hero = 1 OR NEW.is_evolved = 1 THEN
            RAISE(ABORT, 'Una carta champion non può essere eroe né evoluta')
    END;
END;

CREATE TRIGGER IF NOT EXISTS trg_champion_no_hero_evolved_update
BEFORE UPDATE ON cards
FOR EACH ROW
WHEN NEW.type = 'champion'
BEGIN
    SELECT
    CASE
        WHEN NEW.is_hero = 1 OR NEW.is_evolved = 1 THEN
            RAISE(ABORT, 'Una carta champion non può essere eroe né evoluta')
    END;
END;

-- Trigger per assicurarsi che le torri abbiano elixir_cost = 0
CREATE TRIGGER IF NOT EXISTS trg_tower_elixir_zero
BEFORE INSERT ON cards
FOR EACH ROW
WHEN NEW.type = 'tower'
BEGIN
    SELECT
    CASE
        WHEN NEW.elixir_cost != 0 THEN
            RAISE(ABORT, 'Una carta tower deve avere elixir_cost = 0')
    END;
END;

CREATE TRIGGER IF NOT EXISTS trg_tower_elixir_zero_update
BEFORE UPDATE ON cards
FOR EACH ROW
WHEN NEW.type = 'tower'
BEGIN
    SELECT
    CASE
        WHEN NEW.elixir_cost != 0 THEN
            RAISE(ABORT, 'Una carta tower deve avere elixir_cost = 0')
    END;
END;



-- ================================
-- LIVELLI CARTE DEL GIOCATORE
-- ================================
CREATE TABLE player_card (
    player_tag     INTEGER NOT NULL,
    card_name       TEXT NOT NULL,

    level         INTEGER,           -- livello carta (NULL se non applicabile)
    found         INTEGER,   -- 0/1 → il player possiede la carta
    has_evolution INTEGER NOT NULL DEFAULT 0, -- il player ha sbloccato l’evo
    has_hero INTEGER NOT NULL DEFAULT 0, -- il player ha sbloccato l’eroe

    PRIMARY KEY (player_tag, card_name),

    FOREIGN KEY (player_tag) REFERENCES players(player_tag) ON DELETE CASCADE,
    FOREIGN KEY (card_name)   REFERENCES cards(card_name)   ON DELETE CASCADE,

    CHECK (found IN (0,1)),
    CHECK (has_evolution IN (0,1))
);


CREATE TRIGGER trg_player_card_check_evolution_insert
BEFORE INSERT ON player_card
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN NEW.has_evolution = 1
             AND (
                SELECT is_evolved
                FROM cards
                WHERE card_name = NEW.card_name
             ) = 0
            THEN
                RAISE(ABORT, 'Card has no evolution in game')
        END;
END;

CREATE TRIGGER trg_player_card_check_hero_insert
BEFORE INSERT ON player_card
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN NEW.has_hero = 1
             AND (
                SELECT is_hero
                FROM cards
                WHERE card_name = NEW.card_name
             ) = 0
            THEN
                RAISE(ABORT, 'Card has no hero in game')
        END;
END;

CREATE TRIGGER trg_player_card_check_evolution_update
BEFORE UPDATE OF has_evolution ON player_card
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN NEW.has_evolution = 1
             AND (
                SELECT is_evolved
                FROM cards
                WHERE card_name = NEW.card_name
             ) = 0
            THEN
                RAISE(ABORT, 'Card has no evolution in game')
        END;
END;

CREATE TRIGGER trg_player_card_check_hero_update
BEFORE UPDATE OF has_hero ON player_card
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN NEW.has_hero = 1
             AND (
                SELECT is_hero
                FROM cards
                WHERE card_name = NEW.card_name
             ) = 0
            THEN
                RAISE(ABORT, 'Card has no hero in game')
        END;
END;


-- ================================
-- MATCHES / PARTITE
-- ================================
CREATE TABLE IF NOT EXISTS battles (
    battle_id TEXT PRIMARY KEY,          -- es: 1765577323.0
    battle_type TEXT,                    -- PvP, Challenge, ecc
    game_mode TEXT,                      -- Ladder
    timestamp INTEGER,                   -- unix timestamp
    player_tag TEXT,
    player_deck_id TEXT,                 -- FK to decks.deck_hash
    opponent_tag TEXT,
    opponent_deck_id TEXT,               -- FK to decks.deck_hash
    player_crowns INTEGER,
    opponent_crowns INTEGER,
    win INTEGER,                          -- 1 win, 0 loss
    trophy_change INTEGER,
    elixir_leaked_player REAL,
    elixir_leaked_opponent REAL,
    level_diff REAL,
    matchup_win_rate REAL,
    matchup_probabilities TEXT
);

-- ================================
-- TABELLA MAZZI UNICI
-- ================================
CREATE TABLE IF NOT EXISTS decks (
    deck_hash TEXT PRIMARY KEY, -- Hash SHA256 della composizione del mazzo
    archetype_hash TEXT,        -- Hash SHA256 della composizione del mazzo (senza livelli)
    avg_elixir REAL,
);

-- ================================
-- CARTE CONTENUTE IN UN MAZZO
-- ================================
CREATE TABLE IF NOT EXISTS deck_cards (
    deck_hash TEXT,
    card_name TEXT,
    card_level INTEGER,
    has_evolution INTEGER,
    has_hero INTEGER,
    PRIMARY KEY (deck_hash, card_name),
    FOREIGN KEY (deck_hash) REFERENCES decks(deck_hash) ON DELETE CASCADE
);

-- ================================
-- STATISTICHE DI UTILIZZO MAZZO-GIOCATORE
-- ================================
CREATE TABLE IF NOT EXISTS player_deck_stats (
    player_tag TEXT NOT NULL,
    deck_hash TEXT NOT NULL,

    battles_last_30d INTEGER,
    wins_last_30d INTEGER,
    confidence REAL, -- Es. win_rate (wins / battles)

    last_updated DATETIME,

    PRIMARY KEY (player_tag, deck_hash),
    FOREIGN KEY (player_tag) REFERENCES players(player_tag) ON DELETE CASCADE,
    FOREIGN KEY (deck_hash) REFERENCES decks(deck_hash) ON DELETE CASCADE
);



-- -- ================================
-- -- INDICI (per ricerche più veloci)
-- -- ================================
-- CREATE INDEX IF NOT EXISTS idx_matches_timestamp
--     ON matches(timestamp);

-- CREATE INDEX IF NOT EXISTS idx_matches_streak
--     ON matches(streak_before);

-- CREATE INDEX IF NOT EXISTS idx_player_cards_player
--     ON player_card(player_tag);
