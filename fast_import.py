# Import modules
import pandas as pd
from io import StringIO
import psycopg2

# Database connection parameters
host     = 'localhost'
port     = '5432'
dbname   = 'hydro'
user     = 'postgres'
password = 'postgres'

# Import csv into dataframe
df_insert = pd.read_csv('data\H12046_1m_MLLW_1of1.xyz', columns = ['x' , 'y', 'z' ])

# Build connect string
db_connect = "user=" + user + " host=" + host + " dbname ="  + dbname + " port=" + port + " password=" + password + '"'

# Open database connection and get cursor
conn = psycopg2.connect(db_connect)
cur = conn.cursor()


# Insert into database with str IO buffer
log_message(sysdate() + 'Insert ' + str(insert_index)  + " rows into database", log_file)
insert_string = StringIO()
df_insert.to_csv(insert_string, sep='\t', index=False, header=False)
insert_rows = insert_string.getvalue()
cur.copy_from(StringIO(insert_rows), table_name)


# Fast selection
#    # Define SQL
#    sql = 'select koenummer, to_char(tijdslot,\'yyyyddmmhh24miss\') datumtijd, eettijd from public.eatingdata where koenummer = 1'
#
#    # Use the COPY function on the SQL we created above.
#    SQL_for_file_output = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(sql)
#
#    # Set up a variable to store our file path and name.
#    t_path_n_file = "c:/temp/eatingdata_koenummer_1.csv"
#    f_output = open(t_path_n_file, 'w')
#    db_cursor.copy_expert(SQL_for_file_output, f_output)
#    f_output.close()


# Close database
cur.commit()
conn.close()
print('Database connection closed')