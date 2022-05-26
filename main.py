import requests
import urllib.request
import os
import matplotlib.pyplot as plt
from matplotlib import image
import random
import time
import sys


name = input("Enter your name: ").split("#")


def generate_color():
    color = '#{:02x}{:02x}{:02x}'.format(*map(lambda x: random.randint(0, 255), range(3)))
    return color


mapJSON = ""
xScalarToAdd = ""
yScalarToAdd = ""
xMultiplier = ""
yMultiplier = ""


def downloadMaps():
    global mapJSON
    os.makedirs(r"Maps", exist_ok=True)
    URL = "https://valorant-api.com/v1/maps"
    data = requests.get(URL).json()["data"]
    mapJSON = data
    number = 0
    for i in range(len(data)):
        name = data[i]["displayName"]
        if name != "The Range":
            filePath = r"Maps\{}.png".format(name)
            number += 1
            # check if file exists
            if not os.path.isfile(filePath):
                try:
                    urllib.request.urlretrieve(data[i]["displayIcon"], filePath)
                    print("\rDownloaded " + name + " successfully")
                except:
                    print("Error downloading " + name)
    print(f"Counted {number - 1} maps")
    print("All maps up to date!")


def showPlotsMinimap(name, tag):
    try:
        # please dont do what im doing with these global variables, horrible practise :')
        global mapJSON, xMultiplier, yMultiplier, xScalarToAdd, yScalarToAdd
        print("Getting recent matches of " + name+"\n\n")
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{name}/{tag}?size=10" # just using Henriks cuz I cba parsing thru Ritos lol
        data = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"}).json()["data"]
        for i in range(len(data)):
            print(data[i]["metadata"]["map"] + " " + data[i]["metadata"]["mode"])
        
        for index in range(len(data)):
            try:
                print("\n\nGetting " + data[index]["metadata"]["map"] + " " + data[index]["metadata"]["mode"])
                for i in range(len(mapJSON)):
                    if mapJSON[i]["displayName"] == data[index]["metadata"]["map"]:
                        xScalarToAdd = mapJSON[i]["xScalarToAdd"]
                        yScalarToAdd = mapJSON[i]["yScalarToAdd"]
                        xMultiplier = mapJSON[i]["xMultiplier"]
                        yMultiplier = mapJSON[i]["yMultiplier"]
                        # Found scalar and multiplier!
                        break

                mapImage = image.imread(r"Maps\{}.png".format(data[index]["metadata"]["map"]))
                number = 0
                plt.imshow(mapImage)
                plt.title(data[index]["metadata"]["map"] + " " + data[index]["metadata"]["mode"])
                # print("Getting match coordinates...")
                for i in range(len(data[index]["rounds"])):
                    rounds = data[index]["rounds"][i]
                    for j in range(len(rounds["player_stats"])):
                        playerStats = rounds["player_stats"][j]
                        for k in range(len(playerStats["kill_events"])):
                            victimLocationXBefore = playerStats["kill_events"][k]["victim_death_location"]["x"]
                            victimLocationYBefore = playerStats["kill_events"][k]["victim_death_location"]["y"]
                            victimLocationX = int(((victimLocationYBefore * xMultiplier) + xScalarToAdd) * 1024)
                            victimLocationY = int(((victimLocationXBefore * yMultiplier) + yScalarToAdd) * 1024)
                            killer_puuid = playerStats["kill_events"][k]["killer_puuid"]
                            for l in range(len(playerStats["kill_events"][k]["player_locations_on_kill"])):
                                if playerStats["kill_events"][k]["player_locations_on_kill"][l]["player_puuid"] == killer_puuid:
                                    killerLocationXBefore = playerStats["kill_events"][k]["player_locations_on_kill"][l]["location"]["x"]
                                    killerLocationYBefore = playerStats["kill_events"][k]["player_locations_on_kill"][l]["location"]["y"]
                                    killerLocationX = int(((killerLocationYBefore * xMultiplier) + xScalarToAdd) * 1024)
                                    killerLocationY = int(((killerLocationXBefore * yMultiplier) + yScalarToAdd) * 1024)
                                    plt.plot(killerLocationX, killerLocationY, marker='o', color="red", markersize=4)
                                    plt.plot(victimLocationX, victimLocationY, marker='o', color="blue", markersize=4)
                                    number += 1
                                    plt.title(data[index]["metadata"]["map"] + " " + data[index]["metadata"]["mode"]+ ", plotted " + str(number) + " dots")
                                    plt.pause(0.001)
                            # print(str(victimLocationX) + " " + str(victimLocationY))
                plt.show()
            except Exception as e:
                print("Error getting " + data[index]["metadata"]["map"] + " " + data[index]["metadata"]["mode"])
                print(f"Due to {e}")
    except Exception as e:
        print("Error getting matches of " + name+ ", probably because the user has no matches or doesnt exist")
        print(f"Due to {e}")


def findComomonMap(name, tag):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{name}/{tag}?size=10" # just using Henriks cuz I cba parsing thru Ritos lol
    data = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"}).json()["data"]
    mapCount = {}
    for i in range(len(data)):
        map = data[i]["metadata"]["map"]
        if map in mapCount:
            mapCount[map] += 1
        else:
            mapCount[map] = 1
    sortedMapCount = sorted(mapCount.items(), key=lambda x: x[1], reverse=True)
    print("\nMost common map: " + sortedMapCount[0][0])
    # print the mapCount
    print("\n")
    for i in range(len(sortedMapCount)):
        print(sortedMapCount[i][0] + ": " + str(sortedMapCount[i][1]))
    plotCommonMap(name, tag, sortedMapCount[0][0], data)


def plotCommonMap(name, tag, map, json):
    global mapJSON, xMultiplier, yMultiplier, xScalarToAdd, yScalarToAdd
    print("Plotting kills and deaths of " + map)
    mapImage = image.imread(r"Maps\{}.png".format(map))
    number = 0
    for index in range(len(json)):
        for i in range(len(mapJSON)):
            if mapJSON[i]["displayName"] == json[index]["metadata"]["map"]:
                xScalarToAdd = mapJSON[i]["xScalarToAdd"]
                yScalarToAdd = mapJSON[i]["yScalarToAdd"]
                xMultiplier = mapJSON[i]["xMultiplier"]
                yMultiplier = mapJSON[i]["yMultiplier"]
                # Found scalar and multiplier!
                break
        plt.imshow(mapImage)
        plt.title("Kills and deaths of "+ map)
        
        if json[index]["metadata"]["map"] == map:
            for i in range(len(json[index]["rounds"])):
                rounds = json[index]["rounds"][i]
                for j in range(len(rounds["player_stats"])):
                    playerStats = rounds["player_stats"][j]
                    for k in range(len(playerStats["kill_events"])):
                        victimLocationXBefore = playerStats["kill_events"][k]["victim_death_location"]["x"]
                        victimLocationYBefore = playerStats["kill_events"][k]["victim_death_location"]["y"]
                        victimLocationX = int(((victimLocationYBefore * xMultiplier) + xScalarToAdd) * 1024)
                        victimLocationY = int(((victimLocationXBefore * yMultiplier) + yScalarToAdd) * 1024)
                        
                        killer_puuid = playerStats["kill_events"][k]["killer_puuid"]
                        for l in range(len(playerStats["kill_events"][k]["player_locations_on_kill"])):
                            if playerStats["kill_events"][k]["player_locations_on_kill"][l]["player_puuid"] == killer_puuid:
                                killerLocationXBefore = playerStats["kill_events"][k]["player_locations_on_kill"][l]["location"]["x"]
                                killerLocationYBefore = playerStats["kill_events"][k]["player_locations_on_kill"][l]["location"]["y"]
                                killerLocationX = int(((killerLocationYBefore * xMultiplier) + xScalarToAdd) * 1024)
                                killerLocationY = int(((killerLocationXBefore * yMultiplier) + yScalarToAdd) * 1024)
                                plt.plot(killerLocationX, killerLocationY, marker='o', color='red', markersize=2)
                                plt.plot(victimLocationX, victimLocationY, marker='o', color='blue', markersize=2)
                                plt.title("Plotted " + str(number) + " dots")
                                number +=1
                                plt.pause(0.001)
    print("Number of dots: " + str(number))
    plt.show()
   


def downloadWeapons():
    try:
        URL = "https://valorant-api.com/v1/weapons"
        data = requests.get(URL).json()["data"]
        number = 0

        for i in range(len(data)):
            name = data[i]["displayName"]
            skins = data[i]["skins"]
            os.makedirs(r"Weapons\{}".format(name), exist_ok=True)
            for j in range(len(skins)):
                chromas = skins[j]["chromas"]
                for k in range(len(chromas)):
                    number += 1
                    filePath = r"Weapons\{}\{}.png".format(name, number)
                    # check if file exists
                    if not os.path.isfile(filePath):
                        urllib.request.urlretrieve(chromas[k]["fullRender"], filePath)
                        # print number of skins downloaded on the  same line
                        print("\rDownloaded " + str(number) + " skins", end="")
                        #print("Downloaded " + chromas[k]["displayName"] + " successfully")
        print(f"Counted {number} skins")
        print("All skins up to date!")
    except:
        print("Error in downloading file, retrying in 3 seconds...")
        time.sleep(3)
        downloadWeapons()


def downloadBuddies():
    try:
        URL = "https://valorant-api.com/v1/buddies"
        data = requests.get(URL).json()["data"]
        number = 0
        os.makedirs(r"Buddies", exist_ok=True)
        for i in range(len(data)):
            name = data[i]["displayName"]
            name = name.replace("/", "")
            filePath = r"Buddies\{}.png".format(name)
            number += 1
            # check if file exists
            if not os.path.isfile(filePath):
                try:
                    urllib.request.urlretrieve(data[i]["displayIcon"], filePath)
                    print("\rDownloaded " + name + " successfully")
                except:
                    print("Error downloading " + name)
        print(f"Counted {number - 1} buddies")
        print("All buddies up to date!")
    except:
        print("Error downloading buddies... retrying in 3 seconds...")
        time.sleep(3)


def downloadCards():
    try:
        URL = "https://valorant-api.com/v1/playercards"
        data = requests.get(URL).json()["data"]
        number = 0
        os.makedirs(r"Player Cards", exist_ok=True)
        os.makedirs(r"Player Cards\Wide", exist_ok=True)
        os.makedirs(r"Player Cards\Large", exist_ok=True)
        os.makedirs(r"Player Cards\Small", exist_ok=True)
        for i in range(len(data)):
            name = data[i]["displayName"]

            # there has to be a way to make this more efficient
            name = name.replace("/", "")
            name = name.replace("?", "")
            # ill fix it later 

            filePathWide = r"Player Cards\Wide\{}.png".format(name)
            filePathLarge = r"Player Cards\Large\{}.png".format(name)
            filePathSmall = r"Player Cards\Small\{}.png".format(name)
            number = number + 1
            # check if file exists
            if not os.path.isfile(filePathWide):
                try:
                    urllib.request.urlretrieve(data[i]["wideArt"], filePathWide)
                    print("\rDownloaded " + name + " successfully")
                except:
                    print("Error downloading " + name)
            if not os.path.isfile(filePathLarge):
                try:
                    urllib.request.urlretrieve(data[i]["largeArt"], filePathLarge)
                    print("\rDownloaded " + name + " successfully")
                except:
                    print("Error downloading " + name)
            if not os.path.isfile(filePathSmall):
                try:
                    urllib.request.urlretrieve(data[i]["smallArt"], filePathSmall)
                    print("\rDownloaded " + name + " successfully")
                except:
                    print("Error downloading " + name)
    except:
        print("Error downloading cards... retrying in 3 seconds...")
        time.sleep(3)
        downloadCards()
    print(f"Counted {number - 1} player cards")
    print("All player cards up to date!")


def downloadSprays():
    try:
        URL= "https://valorant-api.com/v1/sprays"
        data = requests.get(URL).json()["data"]
        number = 0
        os.makedirs(r"Sprays\Icons", exist_ok=True)
        os.makedirs(r"Sprays\Animation", exist_ok=True)
        for i in range(len(data)):
            name = data[i]["displayName"]
            name = name.replace("/", "")
            filePathIcon = r"Sprays\Icons\{}.png".format(name)
            filePathAnimation = r"Sprays\Animation\{}.gif".format(name)
            number = number + 1
            # check if file exists
            if not os.path.isfile(filePathIcon):
                try:
                    urllib.request.urlretrieve(data[i]["fullTransparentIcon"], filePathIcon)
                    print("\rDownloaded " + name + " successfully")
                except:
                    pass
                    #print("Error downloading " + name)
            if not os.path.isfile(filePathAnimation):
                try:
                    urllib.request.urlretrieve(data[i]["animationGif"], filePathAnimation)
                    print("\rDownloaded " + name + " animation successfully")
                except:
                    pass
                    #print("Error downloading Animation " + name)
        print(f"Counted {number - 1} sprays")
        print("All sprays up to date!")
    except:
        print("Error downloading sprays... retrying in 3 seconds...")
        time.sleep(3)
        downloadSprays()

QUIT = 9
EVERYTHING = 8

def menu():
    while True:
        print("\nChoose your option:")
        print("1. Download Weapon Skins")
        print("2. Download Maps")
        print("3. Download Buddies")
        print("4. Download Player cards")
        print("5. Download Sprays")
        print("6. Show minimap plots")
        print("7. Find common map")
        print(f"{EVERYTHING}. Download all O_o")
        print(f"{QUIT}. Quit Console")
        ans = int(input("Answer: "))
        if ans == 1:
            downloadWeapons()
        elif ans == 2:
            downloadMaps()
        elif ans == 3:
            downloadBuddies()
        elif ans == 4:
            downloadCards()
        elif ans == 5:
            downloadSprays()
        elif ans == 6:
            downloadMaps()
            input("Press enter to continue...")
            showPlotsMinimap(name[0], name[1])
        elif ans == 7:
            downloadMaps()
            try:
                input("Press enter to continue...")
                findComomonMap(name[0], name[1])
            except:
                print("Error finding common map")
        elif ans == EVERYTHING:
            print("\nDownloading everything...\n")
            downloadWeapons()
            downloadMaps()
            downloadBuddies()
            downloadCards()
            downloadSprays()
            print("\nAll files are up to date!")
        elif ans == QUIT:
            break
        else:
            print("Invalid answer")

    print("Thank you for using the console! Enter to exit")
    input()


print("Welcome to the Valorant Console. It is reccomended you put this file in a new folder as all assets will be downloaded into the same place!")
print("More assets to come soon.")
menu()