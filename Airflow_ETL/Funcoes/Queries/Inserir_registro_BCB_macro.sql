INSERT INTO bcb_macro ({colunas})
VALUES ({placeholders})
ON CONFLICT (data) DO UPDATE
SET {update_sql}