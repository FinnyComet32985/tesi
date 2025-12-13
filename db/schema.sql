-- ================================
-- TABELLA GIOCATORI
-- ================================
CREATE TABLE IF NOT EXISTS players (
    player_tag TEXT PRIMARY KEY,
    name TEXT,
    clan TEXT,
    trophies INTEGER,
    arena TEXT,
    rank TEXT,
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
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_tag TEXT,
    timestamp DATETIME,
    result INTEGER,                   -- 1 vittoria, 0 sconfitta, 2 pareggio
    trophy_before INTEGER,
    trophy_after INTEGER,
    streak_before INTEGER,
    opponent_tag TEXT,
    opponent_king_level INTEGER,
    opponent_card_levels JSON,
    opponent_deck JSON,
    matchup_score REAL,               -- da -1 (full counter) a +1 (super favorevole)
    raw_match_json JSON,
    FOREIGN KEY (player_tag) REFERENCES players(player_tag)
);

-- ================================
-- INDICI (per ricerche più veloci)
-- ================================
CREATE INDEX IF NOT EXISTS idx_matches_timestamp
    ON matches(timestamp);

CREATE INDEX IF NOT EXISTS idx_matches_streak
    ON matches(streak_before);

CREATE INDEX IF NOT EXISTS idx_player_cards_player
    ON player_card(player_tag);
