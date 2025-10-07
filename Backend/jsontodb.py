import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values, Json
from dotenv import load_dotenv
import os

load_dotenv()

def create_database_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id SERIAL PRIMARY KEY,
                cuisine VARCHAR(255),
                title VARCHAR(255),
                rating FLOAT,
                prep_time INTEGER,
                cook_time INTEGER,
                total_time INTEGER,
                description TEXT,
                nutrients JSONB,
                serves VARCHAR(255),
                content_hash TEXT
            )
        """)
    conn.commit() 

def clean_data(df):
    return df.replace({pd.NA: None, pd.NaT: None})

def insert_data(conn, recipes):
    with conn.cursor() as cur:
        data = []
        for recipe in recipes:
            try:
                nutrients = recipe.get('nutrients', {})
                if pd.isna(nutrients) or nutrients is None:
                    nutrients = {}
                elif isinstance(nutrients, str):
                    try:
                        nutrients = json.loads(nutrients)
                    except json.JSONDecodeError:
                        nutrients = {}
                elif not isinstance(nutrients, dict):
                    nutrients = {}
                
                data.append((
                    recipe.get('cuisine'),
                    recipe.get('title'),
                    recipe.get('rating'),
                    recipe.get('prep_time'),
                    recipe.get('cook_time'),
                    recipe.get('total_time'),
                    recipe.get('description'),
                    Json(nutrients),
                    recipe.get('serves')
                ))
            except Exception as e:
                print(f"Error processing recipe: {str(e)}")
                continue
        
        if not data:
            raise Exception("No valid data to insert")
       
        execute_values(
            cur,
            """
            INSERT INTO recipes 
            (cuisine, title, rating, prep_time, cook_time, total_time, description, nutrients, serves)
            VALUES %s
            """,
            data
        )
    conn.commit()

def main():
    try:
        print("Reading JSON file...")
        with open('US_recipes_null.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        recipes = list(data.values())
        print(f"Found {len(recipes)} recipes")
        
        print("Connecting to database...")
        conn = create_database_connection()
        
        try:
            print("Creating table...")
            create_table(conn)
        
            print("Inserting data...")
            insert_data(conn, recipes)
            
            print("Data import completed successfully!")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()