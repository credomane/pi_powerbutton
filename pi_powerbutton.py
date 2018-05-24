#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import subprocess
import os

#---------------------------------------
#load config file
#---------------------------------------
config = {}
with open("./pi_powerbutton.cfg") as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        config[name.strip()] = var.strip()
config = type("Config", (object,), config)

#---------------------------------------
#test that each config value exists and is valid or set a sane default.
#---------------------------------------
localefile = "./locale/" + config.locale + ".cfg"
if not os.path.isfile(localefile):
    config.locale = "en-us"
    localefile = "./locale/" + config.locale + ".cfg"

try:
    config.delay_between_switching_actions = int(config.delay_between_switching_actions)
except ValueError:
    config.delay_between_switching_actions = 2

try:
    config.delay_before_performing_action = int(config.delay_before_performing_action)
except ValueError:
    config.delay_before_performing_action = 5

try:
    config.rpi_gpio_pin = int(config.rpi_gpio_pin)
except ValueError:
    config.rpi_gpio_pin = 5

#---------------------------------------
#load locale file
#---------------------------------------
locale = {}
if os.path.isfile(localefile):
    with open(localefile) as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            locale[name.strip()] = var.strip()
locale = type("Locale", (object,), locale)

#---------------------------------------
#test that each locale value exists and is valid or set an US English default.
#---------------------------------------
try:
    locale.choice_cancel
except AttributeError:
    locale.choice_cancel = "C1ancel"

try:
    locale.choice_restart
except AttributeError:
    locale.choice_restart = "Reboot"

try:
    locale.choice_shutdown
except AttributeError:
    locale.choice_shutdown = "Shutdown"

try:
    locale.action_canceled
except AttributeError:
    locale.action_canceled = "Action canceled"

try:
    locale.action_restart
except AttributeError:
    locale.action_restart = "Restarting in %1 seconds"

try:
    locale.action_shutdown
except AttributeError:
    locale.action_shutdown = "Shutting down in %1 seconds"

try:
    locale.nothing_to_cancel
except AttributeError:
    locale.nothing_to_cancel = "Nothing to cancel"

#---------------------------------------
#replace substitution value in certain locale.
#---------------------------------------
locale.action_restart = locale.action_restart.replace("%", str(config.delay_before_performing_action))
locale.action_shutdown = locale.action_shutdown.replace("%1", str(config.delay_before_performing_action))

#---------------------------------------
#setup RPi GPIO
#---------------------------------------
GPIO.setmode(GPIO.BOARD)
GPIO.setup(config.rpi_gpio_pin, GPIO.IN)


#---------------------------------------
#Enter main program loop
#---------------------------------------

#Special vars
buttonWasPressed = False
sleepTimer = 0.5

#Used to decide if we should reboot or shutdown
actionEnabled = False
actionAction = 0 #0 = cancel, 1 = restart, 2 = shutdown
actionTimeStart = config.delay_before_performing_action * (1 / sleepTimer)
actionTimeLeft = 0 #Time in seconds before we perform the action

choiceSpoken = False
choiceAction = 0 #0 = cancel, 1 = restart, 2 = shutdown
choiceTimeStart = config.delay_between_switching_actions * (1 / sleepTimer)
choiceTimeLeft = 0

while True:
    #Button is true when NOT pressed so we flip it to be true when pressed.
    buttonPressed = not bool(GPIO.input(config.rpi_gpio_pin))

    #If button is currently pressed read through the options...
    if buttonPressed:
        if not buttonWasPressed:
            buttonWasPressed = True
            choiceSpoken = False
            choiceAction = 0

        if not choiceSpoken:
            choiceSpoken = True
            choiceTimeLeft = choiceTimeStart
            if choiceAction == 0:
                subprocess.Popen("espeak -v " + config.locale + " --stdout '"+ locale.choice_cancel + "' | aplay", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
            elif choiceAction == 1:
                subprocess.Popen("espeak -v " + config.locale + " --stdout '"+ locale.choice_restart + "' | aplay", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
            elif choiceAction == 2:
                subprocess.Popen("espeak -v " + config.locale + " --stdout '"+ locale.choice_shutdown + "' | aplay", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

    #If the button was released perform an action.
    elif buttonWasPressed:
        buttonWasPressed = False
        if choiceAction == 0:
            if actionEnabled:
                subprocess.Popen("espeak -v " + config.locale + " --stdout '"+ locale.action_canceled + "' | aplay", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
            else:
                subprocess.Popen("espeak -v " + config.locale + " --stdout '"+ locale.nothing_to_cancel + "' | aplay", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
            actionEnabled = False
            actionAction = "cancel"
            actionTimeLeft = 0
        elif choiceAction == 1:
            subprocess.call("espeak -v " + config.locale + " --stdout '"+ locale.action_restart + "' | aplay", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
            actionEnabled = True
            actionAction = "restart"
            actionTimeLeft = actionTimeStart
        elif choiceAction == 2:
            subprocess.call("espeak -v " + config.locale + " --stdout '"+ locale.action_shutdown + "' | aplay", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
            actionEnabled = True
            actionAction = "shutdown"
            actionTimeLeft = actionTimeStart

    if choiceTimeLeft <= 0:
        choiceTimeLeft = 0
        choiceSpoken = False
        choiceAction += 1
        if choiceAction > 2:
            choiceAction = 0

    if actionTimeLeft <= 0:
        actionTimeLeft = 0
        if actionEnabled:
            if actionAction == "restart":
                print "Restarting now..."
            elif actionAction == "shutdown":
                print "Shutting down now..."
            sys.exit(0)

    time.sleep(sleepTimer)
    if choiceTimeLeft > 0:
        choiceTimeLeft -= sleepTimer
    if actionTimeLeft > 0:
        actionTimeLeft -= sleepTimer
















