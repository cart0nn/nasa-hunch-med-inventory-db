import sqlite3 as sqlite

# define valid types
types = ["medicine", "supplement"]


def initTable():
    try:
        global sqliteConnection; sqliteConnection = sqlite.connect('inventory.db')
        global cursor; cursor = sqliteConnection.cursor()
        
    except sqlite.Error as error:
        print('Error while initializing, ',error)
        
    finally:
        if sqliteConnection:
            print('SQLite connected successfully')
        else:
            print('Error while connecting to SQLite')

def setupTable():
    try:
        initTable()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            date_added DATETIME NOT NULL,
                            lifetime integer,
                            type TEXT NOT NULL,
                            
                        );
                        IF EXISTS
                            RAISEERROR('Table already exists');
                            ROLLBACK TRANSACTION;''')
        sqliteConnection.commit()
        print('Table created successfully')
        
    except sqlite.Error as error:
        print('Error during sqlite setup ',error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('The SQLite connection is closed')

def dumpTable():
    try:
        sqliteConnection = sqlite.connect('inventory.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('SELECT * FROM inventory')
        sqliteConnection.commit()
        print(cursor.fetchall())
        
    except sqlite.Error as error:
        print('Error while dumping table, ',error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('The SQLite connection is closed')
            
def insertToTable():
    name = input('Enter item name: ')
    lifetime = input('Enter item lifetime: ')
    if sqliteConnection:
        try:
            cursor.execute('INSERT INTO inventory (',name,', date_added,', lifetime, 'type) VALUES (?, ?, ?)')
            sqliteConnection.commit()
            print('Record inserted successfully')
            
        except sqlite.Error as error:
            print('Error while inserting to table, ',error)
            
        finally:
            if sqliteConnection:
                sqliteConnection.close()
                print('The SQLite connection is closed')
                
def cli():
# dictionary of commands
    commands = {
        'setup': setupTable,
        'dump': dumpTable,
        'insert' : insertToTable,
        'help': lambda: print('setup, dump, insert, help, exit'),
    }
# interface
    while True:
        cmd = input('Enter command: ')
        if cmd == 'exit':
            break
        elif cmd in commands:
            commands[cmd]()
        else:
            print('Invalid command')            

if __name__ == '__main__':
    initTable()
    cli()


