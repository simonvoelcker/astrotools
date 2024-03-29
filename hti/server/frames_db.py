from typing import List, Dict

import os
import sqlite3

FRAMES_DB_FILEPATH = "./frames_db.sqlite"


class FramesDB:
    def __init__(self, reset_db=False):
        if reset_db:
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
                calibration_result TEXT,
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
                -- user-provided quality score
                user_frame_quality INTEGER,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(reference_frame_id) REFERENCES Frame(id) ON DELETE SET NULL
            );
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS Frame (
                id INTEGER PRIMARY KEY ASC,
                filename TEXT NOT NULL UNIQUE,
                sequence_id INTEGER NOT NULL,
                analysis_id INTEGER DEFAULT NULL,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(sequence_id) REFERENCES Sequence(id) ON DELETE CASCADE,
                FOREIGN KEY(analysis_id) REFERENCES Analysis(id) ON DELETE SET NULL
            );
        """)
        self.connection.commit()

    def add_sequence(
        self, name: str, camera_name: str, exposure: float, gain: float,
    ) -> int:
        result = self.connection.execute(f'''
            INSERT INTO Sequence(
                name,
                camera_name,
                exposure,
                gain
            ) VALUES(
                "{name}",
                "{camera_name}",
                {exposure},
                {gain}
            );
        ''')
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

    def add_analysis(
        self,
        frame_id: int,
        calibration_data=None,
        brightness: float = None,
        hfd: float = None,
        alignment_error: float = None,
        frame_offset_x: float = None,
        frame_offset_y: float = None,
        reference_frame_id: int = None,
        user_frame_quality: int = None,
    ) -> int:
        data = dict(
            brightness=brightness,
            hfd=hfd,
            alignment_error=alignment_error,
            frame_offset_x=frame_offset_x,
            frame_offset_y=frame_offset_y,
            reference_frame_id=reference_frame_id,
            user_frame_quality=user_frame_quality,
        )
        if calibration_data:
            data.update(
                pixel_scale=calibration_data.pixel_scale,
                pixel_scale_unit=calibration_data.pixel_scale_unit,
                center_ra=calibration_data.center_deg.ra,
                center_dec=calibration_data.center_deg.dec,
                rotation_angle=calibration_data.rotation_angle,
                rotation_direction=calibration_data.rotation_direction,
                parity=calibration_data.parity,
            )

        # Wrap strings in "", numbers in strings, filter Nones
        data = {
            key: f'"{value}"' if isinstance(value, str) else str(value)
            for key, value in data.items()
            if value is not None
        }
        if not data:
            print("No analysis data was provided")
            return 0

        try:
            result = self.connection.execute(f'''
                INSERT INTO Analysis(
                    {",".join(data.keys())}
                ) VALUES(
                    {",".join(data.values())}
                );
            ''')
            analysis_id = result.lastrowid

            self.connection.execute(f'''
                UPDATE Frame
                SET analysis_id = {analysis_id}
                WHERE id = {frame_id};
            ''')
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print(f"Failed to add analysis data or update frame: {e}")
            return 0

        return result.lastrowid

    def list_sequences(self) -> List[Dict]:
        columns = ["id", "name", "camera_name", "exposure", "gain", "created"]
        result = self.connection.execute(
            f'SELECT {",".join(columns)} FROM Sequence ORDER BY id DESC;'
        )
        return [
            {column: value for column, value in zip(columns, row)}
            for row in result.fetchall()
        ]

    def delete_sequence(self, sequence_id):
        self.connection.execute(
            f'DELETE FROM Sequence WHERE id = {sequence_id};'
        )
        self.connection.commit()

    def list_frames(self, sequence_id: int) -> List[Dict]:
        columns = ["id", "filename", "analysis_id", "created"]
        result = self.connection.execute(f'''
            SELECT {",".join(columns)}
            FROM Frame
            WHERE sequence_id = {sequence_id}
            ORDER BY id ASC;
        ''')
        return [
            {column: value for column, value in zip(columns, row)}
            for row in result.fetchall()
        ]

    def list_analyzed_frames(self, sequence_id: int) -> List[Dict]:
        result = self.connection.execute(f'''
            SELECT
                Frame.filename, 
                Analysis.pixel_scale,
                Analysis.pixel_scale_unit,
                Analysis.center_ra,
                Analysis.center_dec,
                Analysis.rotation_angle,
                Analysis.rotation_direction,
                Analysis.parity
            FROM Frame
            JOIN Analysis
                ON Frame.analysis_id = Analysis.id
            WHERE Frame.sequence_id = {sequence_id}
                AND Analysis.parity IS NOT NULL
            ORDER BY Frame.id ASC;
        ''')
        return [
            {
                "filename": row[0],
                "pixel_scale": row[1],
                "pixel_scale_unit": row[2],
                "center_ra": row[3],
                "center_dec": row[4],
                "rotation_angle": row[5],
                "rotation_direction": row[6],
                "parity": row[7],
            }
            for row in result.fetchall()
        ]

    def get_frame_filename(self, frame_id: int) -> str:
        result = self.connection.execute(f'''
            SELECT filename FROM Frame WHERE id = {frame_id};
        ''')
        return [row[0] for row in result.fetchall()][0]

    def delete_frame(self, frame_id: int):
        self.connection.execute(
            f'DELETE FROM Frame WHERE id = {frame_id};'
        )
        self.connection.commit()

    # Util

    def print_all_data(self):
        print("Listing all recorded sequences and their frames")

        sequences_result = self.connection.execute('''
            SELECT id, name, camera_name, exposure, gain, created
            FROM Sequence
            ORDER BY id;
        ''')

        for sequence_row in sequences_result:
            sequence_id, name, camera_name, exposure, gain, sequence_created = sequence_row
            print(f'\nSequence {sequence_id}: {name}, camera {camera_name}, exposure {exposure}, gain {gain}, created {sequence_created}')

            frames_result = self.connection.execute(f'''
                SELECT id, filename, analysis_id, created
                FROM Frame
                WHERE sequence_id = {sequence_id}
                ORDER BY id;
            ''')

            for frame_row in frames_result:
                frame_id, filename, analysis_id, created = frame_row
                print(f'\tFrame {frame_id}: {filename}, analysis {analysis_id}, created {created}')


if __name__ == '__main__':
    db = FramesDB()
    db.print_all_data()
