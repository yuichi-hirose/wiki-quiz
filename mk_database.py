import sqlite3

if(__name__=="__main__"):
    con = sqlite3.connect('cache.db')
    cur = con.cursor()

    # Create table
    cur.execute('''CREATE TABLE cache
                (userid text primary key, ans text, hint1 text, hint2 text, hint3 text, hint4 text, hint5 text)''')

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()