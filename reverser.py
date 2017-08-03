import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

_session = {'altitude' : '', 'ascent' : '', 'descent' : '', 'burst' : '', 'day' : '', 'hour' : '', 'minute' : '', 'latitude' : '', 'longitude' : ''}
_target = {'latitude' : '', 'longitude' : ''}
_presets = {'Mercer Meadows' : ['40.319','-74.75'], 'Cranbury' : ['40.3023', '-74.5412'], 'Hopewell' : ['40.3377', '-74.8105']}
_ids = {'initial_alt' : '', 'ascent' : '', 'drag' : '', 'burst' : '', 'day' : '', 'hour' : '', 'min' : '', 'lat' : '', 'lon' : ''}
_link = {'initial_alt' : 'altitude', 'ascent' : 'ascent', 'drag' : 'descent', 'burst' : 'burst', 'day' : 'day', 'hour' : 'hour', 'min' : 'minute', 'lat' : 'latitude', 'lon' : 'longitude'}
_address = 'flight_path.csv'


def _getChoice(choices):
    # helper function if you need user input that must be in list choices
    selection = input('')
    while selection not in choices:
        print('Sorry, not a valid choice. Please try again.')
        selection = input('')
    return selection

def _last_line(sheet):
    with open(sheet, 'rt') as f:
        reader = csv.reader(f)
        output = ''
        for row in reader:
            output = row
    os.remove(sheet)
    return output[1:3]   

def initBalloon():
    print('We will start by getting some data about the balloon.')
    print('You will be able to adjust these entries later.')
    print('')
    
    print('In meters, what altitude will you launch from?')
    _session['altitude'] = input('')
    print('')
    
    print('In meters per second, what is the ascent speed?')
    _session['ascent'] = input('')
    print('')
    
    print('In meters per second, what is the descent speed?')
    _session['descent'] = input('')
    print('')
    
    print('In meters, what is the burst height?')
    _session['burst'] = input('')
    print('')
    
    print('What day of the month will you launch?')
    print('(assumes same month as now)')
    _session['day'] = input('')
    print('')
    
    print('In Z time hh:mm, what time will you launch?')
    _fulltime = input('')
    _session['hour'] = _fulltime[:2]
    _session['minute'] = _fulltime[3:]
    print('')    
    
def setTarget():
    print('We will set a target site.')
    print('Type preset to choose a preset target, or new to input latitude and longitude.')
    choice = _getChoice(['preset','new'])
    if choice == 'preset':
        print('')
        print('Type one of the following preset names:')
        for key in _presets.keys():
            print(key)
        user_target = _getChoice(_presets.keys())
        _session['latitude'] = _presets[user_target][0]
        _session['longitude'] = _presets[user_target][1]
        _target['latitude'] = _presets[user_target][0]
        _target['longitude'] = _presets[user_target][1]        
    else:
        print('Type the target latitude.')
        _session['latitude'] = input('')
        _target['latitude'] = _session['latitude']
        print('Type the target longitude.')
        _session['longitude'] = input('')
        _target['longitude'] = _session['longitude']
        
def printBalloon():
    print('')
    print('Printing all current data entries.')
    for key in list(_session):
        if key not in ['latitude', 'longitude']:
            print(key + ' : ' + _session[key])
    print('target : ' + _target['latitude'] + ', ' + _target['longitude'])
    print('')    
      
def reviewBalloon():
    printBalloon()
    print('Type the name of a datapoint to change it.')
    print('Or, type ok to run the prediction.')
    options = list(_session)
    options = ['altitude', 'ascent', 'descent', 'burst', 'day', 'hour', 'minute', 'target', 'ok']
    choice = _getChoice(options)
    while choice != 'ok':
        if choice != 'target':
            print('Enter the new ' + choice + '.')
            newval = input('')
            _session[choice] = newval
        else:
            setTarget()
        printBalloon()
        print('Type the name of another datapoint to change it.')
        print('Or, type ok to run the prediction.')
        choice = _getChoice(options)
    print('')
    print('Datapoints set, proceeding to prediction.')
    
def runOnce(dri):
    for i in _ids.keys():
        _ids[i].clear()
        _ids[i].send_keys(_session[_link[i]])
    run = dri.find_element_by_id('run_pred_btn') 
    run.click()
    
    download = dri.find_element_by_id('dlcsv')
    while not download.is_displayed():
        pass
    download.click()
    while not os.path.exists(_address):
        pass
    time.sleep(2)
    
    landing = _last_line(_address)
    lat_adj = float(landing[0]) - float(_target['latitude'])
    lon_adj = float(landing[1]) - float(_target['longitude'])
    _session['latitude'] = str(float(_session['latitude']) - lat_adj)
    _session['longitude'] = str(float(_session['longitude']) - lon_adj)
      
def modelRun():
    reviewBalloon()
    
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : os.path.dirname(os.path.realpath(__file__))}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options = options)        
    driver.get('http://predict.habhub.org/')
    
    for i in _ids.keys():
        _ids[i] = driver.find_element_by_id(i)
        
    for c in range(0,5):
        runOnce(driver)
    
    driver.close()
    
    print('')
    print('Model run complete. Printing results:')
    print('Launch latitude: ' + _session['latitude'][:7])
    print('Launch longitude: ' + _session['longitude'][:8])
    
def main():
    print('Welcome to the TCNJ balloon launch site tool.')
    print('This application requires the internet and uses')
    print('the CUSF landing site tool at predict.habhub.org')
    print('')
    initBalloon()
    setTarget()
    
    go = 'redo'
    while go != 'stop':
        modelRun()
        print('')
        print('Type redo to change datapoints and run another test.')
        print('Or, type stop to end the program.')
        go = _getChoice(['redo','stop'])
    
    print('')
    print('Thank you for using this application.')
    print('Quitting now.')
    
if __name__ == '__main__':
    main()
    