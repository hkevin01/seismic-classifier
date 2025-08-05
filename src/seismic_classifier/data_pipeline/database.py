"""Database Layer for Seismic Data Storage.

This module provides database abstraction for storing earthquake metadata,
waveform data, and analysis results with SQLite and file-based storage.
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from obspy import Stream

from ..config.settings import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseError(Exception):
    """Base exception for database operations."""

    pass


class SeismicDatabase:
    """
    Database manager for seismic data storage and retrieval.

    This class manages earthquake metadata, waveform data, and analysis
    results using SQLite for metadata and file storage for waveforms.
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize database connection and structure."""
        self.config = config or Config()
        self.db_path = self.config.data_dir / "seismic_data.db"
        self.waveform_dir = self.config.data_dir / "waveforms"
        self.metadata_dir = self.config.data_dir / "metadata"

        # Create directories
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        self.waveform_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(f"Database initialized at {self.db_path}")

    def _init_database(self) -> None:
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Events table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    event_time REAL NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    depth REAL,
                    magnitude REAL,
                    magnitude_type TEXT,
                    location TEXT,
                    source TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    metadata TEXT
                )
            """
            )

            # Stations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stations (
                    network TEXT NOT NULL,
                    station TEXT NOT NULL,
                    location TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    elevation REAL,
                    start_date REAL,
                    end_date REAL,
                    created_at REAL NOT NULL,
                    metadata TEXT,
                    PRIMARY KEY (network, station, location, channel)
                )
            """
            )

            # Waveforms table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS waveforms (
                    id TEXT PRIMARY KEY,
                    event_id TEXT,
                    network TEXT NOT NULL,
                    station TEXT NOT NULL,
                    location TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    sampling_rate REAL NOT NULL,
                    npts INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    file_format TEXT DEFAULT 'MSEED',
                    quality_score REAL,
                    created_at REAL NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            """
            )

            # Analysis results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id TEXT PRIMARY KEY,
                    waveform_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    result_data TEXT NOT NULL,
                    quality_metrics TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (waveform_id) REFERENCES waveforms (id)
                )
            """
            )

            # Create indexes for better performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_events_time
                ON events (event_time)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_events_location
                ON events (latitude, longitude)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_waveforms_time
                ON waveforms (start_time, end_time)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_waveforms_station
                ON waveforms (network, station)
            """
            )

            conn.commit()

    def _generate_id(self, data: str) -> str:
        """Generate unique ID from data string."""
        return hashlib.md5(data.encode()).hexdigest()

    def store_event(self, event_data: Dict[str, Any], source: str = "USGS") -> str:
        """
        Store earthquake event in database.

        Args:
            event_data: Event data dictionary
            source: Data source ('USGS', 'IRIS', etc.)

        Returns:
            Event ID
        """
        # Extract event information
        event_id = event_data.get("id")
        if not event_id:
            # Generate ID from coordinates and time
            coord_time = f"{event_data['latitude']}{event_data['longitude']}{event_data['event_time']}"
            event_id = self._generate_id(coord_time)

        now = datetime.now().timestamp()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert or update event
            cursor.execute(
                """
                INSERT OR REPLACE INTO events (
                    id, event_time, latitude, longitude, depth,
                    magnitude, magnitude_type, location, source,
                    created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event_id,
                    event_data.get("event_time"),
                    event_data.get("latitude"),
                    event_data.get("longitude"),
                    event_data.get("depth"),
                    event_data.get("magnitude"),
                    event_data.get("magnitude_type"),
                    event_data.get("location"),
                    source,
                    now,
                    now,
                    json.dumps(event_data),
                ),
            )

            conn.commit()

        logger.info(f"Stored event {event_id} from {source}")
        return event_id

    def store_waveform(
        self,
        stream: Stream,
        event_id: Optional[str] = None,
        quality_score: Optional[float] = None,
    ) -> List[str]:
        """
        Store waveform data and metadata.

        Args:
            stream: ObsPy Stream object
            event_id: Associated event ID
            quality_score: Data quality score

        Returns:
            List of waveform IDs
        """
        waveform_ids = []
        now = datetime.now().timestamp()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for trace in stream:
                # Generate waveform ID
                trace_info = f"{trace.id}{trace.stats.starttime}{trace.stats.npts}"
                waveform_id = self._generate_id(trace_info)

                # Create file path for waveform data
                file_path = self.waveform_dir / f"{waveform_id}.mseed"

                # Save waveform data to file
                trace.write(str(file_path), format="MSEED")

                # Store metadata in database
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO waveforms (
                        id, event_id, network, station, location, channel,
                        start_time, end_time, sampling_rate, npts,
                        file_path, file_format, quality_score,
                        created_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        waveform_id,
                        event_id,
                        trace.stats.network,
                        trace.stats.station,
                        trace.stats.location,
                        trace.stats.channel,
                        trace.stats.starttime.timestamp,
                        trace.stats.endtime.timestamp,
                        trace.stats.sampling_rate,
                        trace.stats.npts,
                        str(file_path),
                        "MSEED",
                        quality_score,
                        now,
                        json.dumps(dict(trace.stats)),
                    ),
                )

                waveform_ids.append(waveform_id)

            conn.commit()

        logger.info(f"Stored {len(waveform_ids)} waveforms")
        return waveform_ids

    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_magnitude: Optional[float] = None,
        max_magnitude: Optional[float] = None,
        bounding_box: Optional[Tuple[float, float, float, float]] = None,
        source: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Retrieve events from database.

        Args:
            start_time: Start time filter
            end_time: End time filter
            min_magnitude: Minimum magnitude
            max_magnitude: Maximum magnitude
            bounding_box: (min_lat, max_lat, min_lon, max_lon)
            source: Data source filter
            limit: Maximum number of results

        Returns:
            Pandas DataFrame with event data
        """
        query = "SELECT * FROM events WHERE 1=1"
        params = []

        if start_time:
            query += " AND event_time >= ?"
            params.append(start_time.timestamp())

        if end_time:
            query += " AND event_time <= ?"
            params.append(end_time.timestamp())

        if min_magnitude is not None:
            query += " AND magnitude >= ?"
            params.append(min_magnitude)

        if max_magnitude is not None:
            query += " AND magnitude <= ?"
            params.append(max_magnitude)

        if bounding_box:
            min_lat, max_lat, min_lon, max_lon = bounding_box
            query += " AND latitude >= ? AND latitude <= ?"
            query += " AND longitude >= ? AND longitude <= ?"
            params.extend([min_lat, max_lat, min_lon, max_lon])

        if source:
            query += " AND source = ?"
            params.append(source)

        query += " ORDER BY event_time DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)

        logger.info(f"Retrieved {len(df)} events from database")
        return df

    def get_waveforms(
        self,
        event_id: Optional[str] = None,
        network: Optional[str] = None,
        station: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_quality: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Retrieve waveform metadata from database.

        Args:
            event_id: Event ID filter
            network: Network code filter
            station: Station code filter
            start_time: Start time filter
            end_time: End time filter
            min_quality: Minimum quality score

        Returns:
            Pandas DataFrame with waveform metadata
        """
        query = "SELECT * FROM waveforms WHERE 1=1"
        params = []

        if event_id:
            query += " AND event_id = ?"
            params.append(event_id)

        if network:
            query += " AND network = ?"
            params.append(network)

        if station:
            query += " AND station = ?"
            params.append(station)

        if start_time:
            query += " AND start_time >= ?"
            params.append(start_time.timestamp())

        if end_time:
            query += " AND end_time <= ?"
            params.append(end_time.timestamp())

        if min_quality is not None:
            query += " AND quality_score >= ?"
            params.append(min_quality)

        query += " ORDER BY start_time DESC"

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)

        logger.info(f"Retrieved {len(df)} waveform records")
        return df

    def load_waveform_data(self, waveform_id: str) -> Stream:
        """
        Load waveform data from file.

        Args:
            waveform_id: Waveform ID

        Returns:
            ObsPy Stream object
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT file_path FROM waveforms WHERE id = ?", (waveform_id,)
            )
            result = cursor.fetchone()

        if not result:
            raise DatabaseError(f"Waveform {waveform_id} not found")

        file_path = Path(result[0])
        if not file_path.exists():
            raise DatabaseError(f"Waveform file not found: {file_path}")

        from obspy import read

        stream = read(str(file_path))

        logger.debug(f"Loaded waveform data from {file_path}")
        return stream

    def store_analysis_result(
        self,
        waveform_id: str,
        analysis_type: str,
        result_data: Dict[str, Any],
        quality_metrics: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store analysis results.

        Args:
            waveform_id: Associated waveform ID
            analysis_type: Type of analysis performed
            result_data: Analysis results
            quality_metrics: Quality metrics for the analysis

        Returns:
            Analysis result ID
        """
        # Generate result ID
        result_info = f"{waveform_id}{analysis_type}{datetime.now().isoformat()}"
        result_id = self._generate_id(result_info)

        now = datetime.now().timestamp()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_results (
                    id, waveform_id, analysis_type, result_data,
                    quality_metrics, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    result_id,
                    waveform_id,
                    analysis_type,
                    json.dumps(result_data),
                    json.dumps(quality_metrics) if quality_metrics else None,
                    now,
                ),
            )
            conn.commit()

        logger.info(f"Stored {analysis_type} analysis result for {waveform_id}")
        return result_id

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with database statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Count events
            cursor.execute("SELECT COUNT(*) FROM events")
            event_count = cursor.fetchone()[0]

            # Count waveforms
            cursor.execute("SELECT COUNT(*) FROM waveforms")
            waveform_count = cursor.fetchone()[0]

            # Count analysis results
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            analysis_count = cursor.fetchone()[0]

            # Get date range
            cursor.execute(
                """
                SELECT MIN(event_time), MAX(event_time)
                FROM events WHERE event_time IS NOT NULL
            """
            )
            time_range = cursor.fetchone()

            # Get data sources
            cursor.execute("SELECT source, COUNT(*) FROM events GROUP BY source")
            sources = dict(cursor.fetchall())

        stats = {
            "events": event_count,
            "waveforms": waveform_count,
            "analysis_results": analysis_count,
            "time_range": {
                "start": (
                    datetime.fromtimestamp(time_range[0]) if time_range[0] else None
                ),
                "end": datetime.fromtimestamp(time_range[1]) if time_range[1] else None,
            },
            "sources": sources,
            "database_size": (
                self.db_path.stat().st_size if self.db_path.exists() else 0
            ),
        }

        logger.info(f"Database stats: {stats}")
        return stats

    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        Clean up old data from database and file system.

        Args:
            days_to_keep: Number of days of data to keep

        Returns:
            Number of records deleted
        """
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 86400)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get file paths of old waveforms
            cursor.execute(
                """
                SELECT file_path FROM waveforms
                WHERE created_at < ?
            """,
                (cutoff_time,),
            )

            old_files = [row[0] for row in cursor.fetchall()]

            # Delete old records
            cursor.execute(
                "DELETE FROM analysis_results WHERE created_at < ?", (cutoff_time,)
            )
            analysis_deleted = cursor.rowcount

            cursor.execute("DELETE FROM waveforms WHERE created_at < ?", (cutoff_time,))
            waveforms_deleted = cursor.rowcount

            cursor.execute("DELETE FROM events WHERE created_at < ?", (cutoff_time,))
            events_deleted = cursor.rowcount

            conn.commit()

        # Remove old waveform files
        files_removed = 0
        for file_path in old_files:
            try:
                Path(file_path).unlink()
                files_removed += 1
            except FileNotFoundError:
                pass

        total_deleted = events_deleted + waveforms_deleted + analysis_deleted

        logger.info(
            f"Cleanup complete: {total_deleted} records and {files_removed} files removed"
        )
        return total_deleted
