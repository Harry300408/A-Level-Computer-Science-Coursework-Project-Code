import sys, os, pygame, json, configparser

def window_configs_setup():
    global XRES
    global YRES 
    global ISFULLSCREEN
    global FPS
    
    try:
        
        config = configparser.ConfigParser()
        config.read("settings.ini")
        
        XRES = int(config['RESOLUTION']['xres'])
        YRES = int(config['RESOLUTION']['yres'])
        
        ISFULLSCREEN    = str(config['SCREEN']['fullscreen'])
        FPS             = int(config['SCREEN']['fps'])

        return [XRES, YRES, ISFULLSCREEN, FPS]
        
    except:
        print("Error with the settings file, reverting to defaults...")
        set_window_configs_to_default()
        

def set_window_configs_to_default():
    global XRES
    global YRES 
    global ISFULLSCREEN
    global FPS    
    
    try:
        with open("defaults.json", "r") as default:
            SDefaults = json.load(default)
        
        XRES            = SDefaults["window_setup_defaults"]["xresolution"]
        YRES            = SDefaults["window_setup_defaults"]["yresolution"]
        ISFULLSCREEN    = SDefaults["window_setup_defaults"]["fullscreen"]
        FPS             = SDefaults["window_setup_defaults"]["fps"]
       
        with open("settings.ini", "w") as config_file:
            config = configparser.ConfigParser()
            
            config['RESOLUTION']                = {}
            config['RESOLUTION']['XRES']        = str(XRES)
            config['RESOLUTION']['YRES']        = str(YRES)
            
            config['SCREEN']                    = {}
            config['SCREEN']['FULLSCREEN']      = str(ISFULLSCREEN)
            config['SCREEN']['FPS']             = str(FPS)
            
            config.write(config_file)

        return [XRES, YRES, ISFULLSCREEN, FPS]
    
    except:
        raise SystemError("'defaults.json' file not found or doesn't have the right values, please either repair the game or redownload from source.")

def game_lang_load():
    global LANG
    
    try:
        config = configparser.ConfigParser()
        config.read("settings.ini")
        
        LANG = str(config['LANGUAGE']['locale'])
    
    except:
        
        try:
            
            with open("defaults.json", "r") as default:
                LDefaults = json.load(default)
                
                LANG = LDefaults['language']
            
            with open("settings.ini", "a+") as config_file:
                config = configparser.ConfigParser()
                
                config['LANGUAGE']                  = {}
                config['LANGUAGE']['locale']        = str(LANG)
                
                config.write(config_file)

            return LANG
             
        except:
            raise SystemError("'defaults.json' file not found or doesn't have the right values, please either repair the game or redownload from source.")
 