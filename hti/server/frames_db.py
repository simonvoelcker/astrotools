import os
import sqlite3

FRAMES_DB_FILEPATH = "./frames_db.sqlite"


class FramesDB:
    def __init__(self):

        os.remove(FRAMES_DB_FILEPATH)

        self.connection = sqlite3.connect(FRAMES_DB_FILEPATH)
        self.create_db()

    def create_db(self):
        self.connection.execute("PRAGMA foreign_keys = ON;")
        # potentially add: binning, region, width, height, type (name for now)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS Sequence (
                id INTEGER PRIMARY KEY ASC,
                name TEXT NOT NULL,
                camera_name TEXT NOT NULL,
                exposure REAL NOT NULL,
                gain INTEGER NOT NULL,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS Analysis (
                id INTEGER PRIMARY KEY ASC,
                -- astrometry calibration data
                pixel_scale REAL,
                pixel_scale_unit TEXT,
                center_ra REAL,
                center_dec REAL,
                rotation_angle REAL,
                rotation_direction TEXT,
                parity TEXT,
                -- average pixel brightness across the frame
                brightness REAL,
                -- calculated half-flux diameter from brightest star
                hfd REAL,
                -- alignment error observed by guiding cam during exposure
                alignment_error REAL,
                -- x/y alignment error to a reference frame
                frame_offset_x REAL,
                frame_offset_y REAL,
                reference_frame_id INTEGER,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(reference_frame_id) REFERENCES Frame(id)
            );
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS Frame (
                id INTEGER PRIMARY KEY ASC,
                filename TEXT NOT NULL UNIQUE,
                sequence_id INTEGER NOT NULL,
                analysis_id INTEGER DEFAULT NULL,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(sequence_id) REFERENCES Sequence(id),
                FOREIGN KEY(analysis_id) REFERENCES Analysis(id)
            );
        """)
        self.connection.commit()

    def add_sequence(self, name: str) -> int:
        result = self.connection.execute(
            f'INSERT INTO Sequence(name) VALUES("{name}");'
        )
        self.connection.commit()
        return result.lastrowid

    def add_frame(self, sequence_id: int, filename: str) -> int:
        try:
            result = self.connection.execute(
                f'INSERT INTO Frame(filename, sequence_id) VALUES("{filename}", {sequence_id});'
            )
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print(f"Failed to add frame: {e}")
            return 0
        return result.lastrowid

    # Util

    def count_sequences(self):
        result = self.connection.execute(
            'SELECT COUNT(*) FROM Sequence;'
        )
        return [row[0] for row in result][0]

    def get_frames(self, sequence_id: int):
        result = self.connection.execute(f"""
            SELECT id, filename
            FROM Frame
            WHERE sequence_id = {sequence_id};
        """)
        return [
            {
                'id': row[0],
                'filename': row[1],
            }
            for row in result
        ]


db = FramesDB()
s_id = db.add_sequence("Darkest frames")
f_id = db.add_frame(s_id, "frame uno")
print(db.get_frames(s_id))
