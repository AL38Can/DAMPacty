from src.utils.database import Database
from datetime import datetime

def update_activity_dates():
    """Update activity dates in the database to ensure consistent format."""
    try:
        db = Database()
        cursor = db.conn.cursor()
        
        # Todas  las actividades
        cursor.execute("SELECT id, fecha FROM actividades")
        activities = cursor.fetchall()
        
        # Actualiza cada fecha de actividad
        for activity in activities:
            activity_id = activity['id']
            old_date = activity['fecha']
            
            # Convert date to standard format (YYYY-MM-DD)
            try:
                if '/' in old_date:
                    # Convert from DD/MM/YYYY to YYYY-MM-DD
                    date_obj = datetime.strptime(old_date, '%d/%m/%Y')
                else:
                    # Already in YYYY-MM-DD format
                    date_obj = datetime.strptime(old_date, '%Y-%m-%d')
                
                new_date = date_obj.strftime('%Y-%m-%d')
                
                # Actualiza la fecha en la base de datos
                cursor.execute("""
                    UPDATE actividades 
                    SET fecha = ? 
                    WHERE id = ?
                """, (new_date, activity_id))
                
                print(f"Updated activity {activity_id}: {old_date} -> {new_date}")
                
            except ValueError as e:
                print(f"Error processing date for activity {activity_id}: {old_date}")
                print(f"Error: {e}")
        
        db.conn.commit()
        print("Date updates completed successfully!")
        
    except Exception as e:
        print(f"Error during date update: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_activity_dates() 