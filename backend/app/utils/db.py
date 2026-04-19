import os
import sqlite3


DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(DATA_DIR, "database.db")


def get_db():
	"""Return a database connection."""
	conn = sqlite3.connect(DB_PATH, check_same_thread=False)
	conn.row_factory = sqlite3.Row
	return conn


def init_db():
	"""Create all tables if they don't exist."""
	conn = get_db()
	cursor = conn.cursor()

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS chat_history (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			session_id TEXT NOT NULL,
			role TEXT NOT NULL,
			content TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS app_stats (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			event_type TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS farm_profiles (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			location TEXT,
			soil_type TEXT,
			acreage REAL,
			crops_grown TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS chat_sessions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			session_id TEXT NOT NULL UNIQUE,
			name TEXT,
			language TEXT DEFAULT 'en',
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	# Add language column if it doesn't exist (for existing databases)
	cursor.execute("PRAGMA table_info(chat_sessions)")
	columns = [col[1] for col in cursor.fetchall()]
	if "language" not in columns:
		cursor.execute("ALTER TABLE chat_sessions ADD COLUMN language TEXT DEFAULT 'en'")

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS market_prices (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			crop TEXT NOT NULL,
			price_per_kg REAL NOT NULL,
			market TEXT,
			date TEXT
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS irrigation_logs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			farm_id INTEGER,
			crop TEXT NOT NULL,
			moisture_level REAL NOT NULL,
			recommended_action TEXT NOT NULL,
			urgency TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS yield_records (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			farm_id INTEGER,
			crop TEXT NOT NULL,
			year INTEGER NOT NULL,
			yield_kg_per_ha REAL NOT NULL,
			area_ha REAL,
			notes TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS sensor_readings (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			farm_id INTEGER,
			sensor_type TEXT NOT NULL,
			value REAL NOT NULL,
			unit TEXT,
			timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS user_profiles (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			device_id TEXT NOT NULL UNIQUE,
			preferred_language TEXT DEFAULT 'en',
			voice_enabled INTEGER DEFAULT 0,
			interests TEXT DEFAULT '[]',
			location TEXT,
			soil_types TEXT DEFAULT '[]',
			grown_crops TEXT DEFAULT '[]',
			interaction_count INTEGER DEFAULT 0,
			last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS message_feedback (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			session_id TEXT NOT NULL,
			message_index INTEGER,
			user_rating INTEGER,
			helpful INTEGER DEFAULT 0,
			not_helpful INTEGER DEFAULT 0,
			correction TEXT,
			preferred_response TEXT,
			topic TEXT,
			language TEXT DEFAULT 'en',
			device_id TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS user_preferences (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			device_id TEXT NOT NULL,
			pref_key TEXT NOT NULL,
			pref_value TEXT,
			confidence REAL DEFAULT 0.5,
			sample_count INTEGER DEFAULT 1,
			last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(device_id, pref_key)
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS topic_interactions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			device_id TEXT NOT NULL,
			topic TEXT NOT NULL,
			interaction_count INTEGER DEFAULT 1,
			success_count INTEGER DEFAULT 0,
			last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(device_id, topic)
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS learned_contexts (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			device_id TEXT NOT NULL,
			context_key TEXT NOT NULL,
			context_value TEXT NOT NULL,
			usage_count INTEGER DEFAULT 1,
			last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(device_id, context_key)
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS crop_outcomes (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			device_id TEXT NOT NULL,
			crop TEXT NOT NULL,
			soil_type TEXT,
			season TEXT,
			yield_achieved REAL,
			yield_expected REAL,
			success INTEGER DEFAULT 0,
			notes TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS correction_log (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			device_id TEXT NOT NULL,
			session_id TEXT NOT NULL,
			original_response TEXT,
			corrected_response TEXT,
			correction_type TEXT,
			topic TEXT,
			language TEXT DEFAULT 'en',
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)

	conn.commit()
	conn.close()
