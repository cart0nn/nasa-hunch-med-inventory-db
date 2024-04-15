import os
from RPi import GPIO
from scipy.integrate import quad
import sympy
import board
import math
import time
from time import sleep
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import sqlite3 as sqlite



clk = 6
dt = 5
sw = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sw, GPIO.IN)

global length_used
length_used = 0
global volume_total
volume_total = 0
global volume_used
volume_used = 0
global radius
radius = 0
global length
length = 0
global offset
offset = 0
#variable saving code below
i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
ads
channel = AnalogIn(ads, ADS.P0)

numreadings = 15
readings = [0] * numreadings
readindex = 0
total = 0
average = 0
global light_inventory
light_inventory = 0
global light_max
light_max = 0
global light_transmission
light_transmission = 0
calibrated = False

#
# DB FUNCTIONS -----------------------------------------------------------------------------------
#
def initSQLLite():
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
        initSQLLite()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            date_added DATETIME NOT NULL,
                            lifetime integer,
                            type TEXT NOT NULL,
                            package_inventory REAL
                            volume_used REAL,
                            volume_remaining REAL
                        );
                        IF EXISTS
                            RAISEERROR('Table already exists');
                            ROLLBACK TRANSACTION;
        
                        CREATE TABLE IF NOT EXISTS calibration (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            volume_total REAL,
                            radius REAL,
                            length REAL,
                            offset REAL,
                            light_max REAL,
                            passthrough_pct REAL,
                            length_used REAL,
                        );
                        IF EXISTS
                            RAISEERROR('Table already exists');
                            ROLLBACK TRANSACTION;
                       ''')
        sqliteConnection.commit()
        print('Table created successfully')
        
    except sqlite.Error as error:
        print('Error during sqlite setup ',error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('The SQLite connection is closed')

# commented out b/c idk what to do with this yet            
# def insertToTable():
#     name = input('Enter item name: ')
#     lifetime = input('Enter item lifetime: ')
#     if sqliteConnection:
#         try:
#             cursor.execute('INSERT INTO inventory (',name,', date_added,', lifetime, 'type) VALUES (?, ?, ?)')
#             sqliteConnection.commit()
#             print('Record inserted successfully')
            
#         except sqlite.Error as error:
#             print('Error while inserting to table, ',error)
            
#         finally:
#             if sqliteConnection:
#                 sqliteConnection.close()
#                 print('The SQLite connection is closed')
                
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
# NOT DONE
def save_values_to_file(length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory):
    cursor.execute('''
                    INSERT INTO calibration (volume_total, radius, length, offset, light_max, passthrough_pct, length_used)
                    VALUES ({volume_total}, {radius}, {length}, {offset}, {light_max}, {light_transmission}, {length_used})
                    '''.format(volume_total, radius, length, offset, light_max, light_transmission, length_used)

                    ```INSERT INTO inventory (package_inventory)
                    VALUES ({light_inventory})````
                    .format(light_inventory))
# NOT DONE  

def load_values_from_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3]), float(lines[4]), float(lines[5]), float(lines[6]), float(lines[7]), float(lines[8])

def check_and_load(filename):
    if os.path.exists(filename):
        length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory = load_values_from_file(filename)
        print("Values loaded from file:")
        print(f"length used: {length_used} mm")
        print(f"total volume: {volume_total} mL")
        print(f"volume used: {volume_used} mL")
        print(f"radius: {radius} mm")
        print(f"length: {length} mm")
        print(f"offset: {offset}")
        print(f"max light: {light_max}")
        print(f"passthrough pct: {light_transmission}")
        print(f"package inventory retrieved: {light_inventory}")
        if light_max > 0:
            if light_transmission > 0:
                calibrated = True
        print(calibrated)
        selectionLoop(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory, calibrated)
    else:
        print("Values not found in file. Reverting to selection menu for calibration.")
        # Call ROLLER to define variable values
        length_used = 0
        volume_total = 0
        volume_used = 0
        radius = 0
        length = 0
        offset = 0
        light_max = 0
        light_transmission = 0
        light_inventory = 0
        sleep(2.5)
        save_values_to_file(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
        selectionLoop(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory, calibrated)

#
# CONTROLLER FUNCTIONS ---------------------------------------------------------------------------
#

def ROLLER(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory):
    print("begin turning now")
    counter = 0 + offset
    length_used = 0
    volume_used = 0
    print("Values loaded from file:")
    print(f"length used: {length_used} mm")
    print(f"total volume: {volume_total} mL")
    print(f"volume used: {volume_used} mL")
    print(f"radius: {radius} mm")
    print(f"length: {length} mm")
    print(f"offset: {offset}")
    print(f"max light: {light_max}")
    print(f"passthrough pct: {light_transmission}")
    print(f"package inventory retrieved: {light_inventory}")
    clkLastState = GPIO.input(clk)
    while GPIO.input(13) == GPIO.HIGH:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        if clkState != clkLastState:
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
            length = (counter/15)*math.pi*24 +17
            print (f"{length} mm")
            clkLastState = clkState
            sleep(0.02)
    length_used = (counter/15)*math.pi*24 +17
    offset = counter
    y = sympy.symbols ('y')
    volume_used = (math.pi*radius/10)*sympy.integrate(sympy.sqrt(-y+length/10)*(radius/10)/(sympy.sqrt(length/10)), (y, (length/10-length_used/10), length/10))
    return length_used, volume_used, offset

def ROLLERCAL(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory):
    print("begin turning now until the length shown = the circumfrence of your tube at the crown")
    counter = 0

    clkLastState = GPIO.input(clk)
    while GPIO.input(13) == GPIO.HIGH:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        if clkState != clkLastState:
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
            length = (counter/15)*math.pi*24
            print (f"{length} mm")
            clkLastState = clkState
            sleep(0.02)
    radius = ((counter/15)*12)
    print("now turn until the length shown = your tube's length from the crow to before the crimped end")
    counter = 0
    sleep(1)
    while GPIO.input(13) == GPIO.HIGH:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        if clkState != clkLastState:
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
            length = (counter/15)*math.pi*12
            print (f"{length} mm")
            clkLastState = clkState
            sleep(0.02)
    length = length   
    print("the total volume of your tube will now be calculated")
    x = sympy.symbols ('x')
    volume_total = (math.pi*radius/10)*sympy.integrate(sympy.sqrt(-x+length/10)*(radius/10)/(sympy.sqrt(length/10)), (x, 0, length/10))
    return volume_total, radius, length

def call_ROLLER(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory):
    print("Calling Roller...")
    length_used, volume_used, offset = ROLLER(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
    save_values_to_file(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
    print("Values loaded from file:")
    print(f"length used: {length_used} mm")
    print(f"total volume: {volume_total} mL")
    print(f"volume used: {volume_used} mL")
    print(f"radius: {radius} mm")
    print(f"length: {length} mm")
    print(f"offset: {offset}")
    print(f"max light: {light_max}")
    print(f"passthrough pct: {light_transmission}")
    print(f"package inventory retrieved: {light_inventory}")
    selectionLoop(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory, calibrated)

def call_ROLLERCAL(filename, volume_total, radius, length, offset, calibrated, light_max, light_transmission, light_inventory):
    print("Calling Roller calibration wizard...")
    volume_total, radius, length = ROLLERCAL(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
    save_values_to_file(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
    print("Values loaded from file:")
    print(f"length used: {length_used} mm")
    print(f"total volume: {volume_total} mL")
    print(f"volume used: {volume_used} mL")
    print(f"radius: {radius} mm")
    print(f"length: {length} mm")
    print(f"offset: {offset}")
    print(f"max light: {light_max}")
    print(f"passthrough pct: {light_transmission}")
    print(f"package inventory retrieved: {light_inventory}")
    selectionLoop(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory, calibrated)

# Option to call ROLLER or enter calibration loop (prompted in terminal)
def insertNew(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory):
    command = input("Do you want to insert a new tube, or use again? (insert/again): ").lower()
    if command == "insert":
        offset = 0
        offset = 0
        call_ROLLER(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
    elif command == "again":
        call_ROLLER(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
    else:
        print("Invalid command. Exiting...")
    return offset
        
def readSensor(total, average, readindex, readings, numreadings, calibrated, light_max, light_transmission):
    total = 0
    average = 0
    readings = [0]*numreadings
    for readindex in range(0, numreadings):
        total = total - readings[readindex]
        readings[readindex] = channel.value
        total = total + readings[readindex]
        readindex = readindex+1
        average = total / numreadings
        time.sleep(.2)
    print(f'reading = {average}')
    if calibrated == False:
        light_max = average
        input('place one package into the case and then fully zip it shut, then press enter').lower()
        for readindex in range(0, numreadings):
            total = total - readings[readindex]
            readings[readindex] = channel.value
            total = total + readings[readindex]
            readindex = readindex+1
            average = total / numreadings
            time.sleep(.2)
        print(f'average = {average}')
        light_transmission = min(((average/light_max)), 1)
        print(light_transmission)
        calibrated = True
    return light_max, light_transmission, calibrated

def lightInv(total, average, readindex, readings, numreadings, light_max, light_transmission, calibrated):
    for i in range(0, len(readings)):
        readings[i] = 0
    if calibrated == True:
        for readindex in range(0, numreadings):
            total = total - readings[readindex]
            readings[readindex] = channel.value
            total = total + readings[readindex]
            print(total)
            readindex = readindex+1
            average = total / numreadings
            time.sleep(.2)
        current = average
        print(f'current = {current}')
        global light_inventory
        light_inventory = round((math.log(current)-math.log(light_max))/math.log((light_transmission)))
        print(light_inventory)
        total = 0
        average = 0
        return light_inventory

def auto_Inventory(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory, calibrated):
    startTime = time.time()
    print(startTime)
    Flag = True
    loop = 0
    print('to exit auto mode, simply press enter in console')
    while Flag == True:
        loop = loop+1
        if loop >= 50:
            command = input('continue with auto? (y/n): ')
            if command == 'y':
                sleep(.2)
                loop = 0
            elif command == 'n':
                break
        clkLastState = GPIO.input(clk)
        for i in range (0,2):
            print('checking roller')
            clkState = GPIO.input(clk)
            dtState = GPIO.input(dt)
            if clkState != clkLastState:
                print('movement detected, starting roller inventory')
                length_used, volume_used, offset = ROLLER(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
                save_values_to_file(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
            clkLastState = clkState
        sleep(.1)
        print(time.time())
        if (time.time() - startTime) >= 5:
            light_inventory = lightInv(total, average, readindex, readings, numreadings, light_max, light_transmission, calibrated)
            save_values_to_file(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
            print(f'light inventory = {light_inventory}')
            startTime = time.time()
    print("final values from auto session:")
    print(f"length used: {length_used} mm")
    print(f"total volume: {volume_total} mL")
    print(f"volume used: {volume_used} mL")
    print(f"radius: {radius} mm")
    print(f"length: {length} mm")
    print(f"offset: {offset}")
    print(f"max light: {light_max}")
    print(f"passthrough pct: {light_transmission}")
    print(f"package inventory retrieved: {light_inventory}")
    selectionLoop(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory, calibrated)
    
#
# MAIN ------------------------------------------------------------------------------------------
#
def selectionLoop(filename, volume_total, radius, length, offset, calibrated, light_max, light_transmission, light_inventory):
    print('test')
    command = input('select one of the following options (package inv, light calibration, roller inv, roller calibration, inv setup): ').lower()
    if command == 'pi':
        light_inventory = lightInv(total, average, readindex, readings, numreadings, light_max, light_transmission, calibrated)
        print(f'inventory calculated: {light_inventory}')
        print("Values loaded from file:")
        sleep(3)
        print(f"length used: {length_used} mm")
        print(f"total volume: {volume_total} mL")
        print(f"volume used: {volume_used} mL")
        print(f"radius: {radius} mm")
        print(f"length: {length} mm")
        print(f"offset: {offset}")
        print(f"max light: {light_max}")
        print(f"passthrough pct: {light_transmission}")
        print(f"package inventory retrieved: {light_inventory}")
        selectionLoop(filename, volume_total, radius, length, offset, calibrated, light_max, light_transmission, light_inventory)
    elif command == 'lc':
        calibrated = False
        light_max = 0
        light_transmission = 0
        light_max, light_transmission, calibrated = readSensor(total, average, readindex, readings, numreadings, calibrated, light_max, light_transmission)
        print(light_transmission)
        save_values_to_file(filename, length_used, volume_total, volume_used, radius, length, offset, light_max, light_transmission, light_inventory)
        print("Values saved to file:")
        print(f"length used: {length_used} mm")
        print(f"total volume: {volume_total} mL")
        print(f"volume used: {volume_used} mL")
        print(f"radius: {radius} mm")
        print(f"length: {length} mm")
        print(f"offset: {offset}")
        print(f"max light: {light_max}")
        print(f"passthrough pct: {light_transmission}")
        print(f"package inventory retrieved: {light_inventory}")
        selectionLoop(filename, volume_total, radius, length, offset, calibrated, light_max, light_transmission, light_inventory)
    elif command == "rc":
        call_ROLLERCAL(filename)
    elif command == "ri":
        insertNew(filename, volume_total, radius, length, offset)
    elif command == "is":
        setupTable()

if __name__ == '__main__':
    check_and_load(filename)
    initSQLLite()      
    selectionLoop()

