import pandas as pd
import os
from pyscript import window
from pyscript import document

def check_user(event):
    username = document.getElementById("username").value
    password = document.getElementById("password").value

    df = pd.read_csv("username_password.csv", index_col=0)
    try:
        df.loc[username]
        if(df.at[username, "PASSWORD"] == password):
            window.open("page2.html")
        else:
            window.alert("Wrong password")
    except:
        window.alert("No user named " + username)

def make_user(event):
    window.console.log("Making user")
    username = document.getElementById("username").value
    password = document.getElementById("password").value
    df = pd.read_csv("username_password.csv", index_col=0)
    try:
        df.loc[username]
        window.alert("Username already taken")
    except:
        with open("username_password.csv", "w+") as file:
            window.console.log("Writing to file")
            file.write("\n" + username + "," + password)
        window.open("page2.html")
        