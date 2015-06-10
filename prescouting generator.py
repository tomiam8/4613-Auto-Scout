#!/usr/bin/env python

import urllib.request
import json
import pprint
import time

URL = 'http://www.thebluealliance.com/api/v2/'
HEADER_KEY = 'X-TBA-App-Id'
HEADER_VAL = 'frc4613:prescouting-generator:1'

#returns the dictionary for a request for a team
def get_team(team_num):
    request = urllib.request.Request(URL + 'team/frc' + str(team_num))
    request.add_header(HEADER_KEY, HEADER_VAL)
    response = urllib.request.urlopen(request)
    jsonified = json.loads(response.read().decode("utf-8"))
    return jsonified

#gets all the competitions played in by a team
def get_teamEventHistory(team_num):
    request = urllib.request.Request(URL + 'team/frc' + str(team_num) + '/events')
    request.add_header(HEADER_KEY, HEADER_VAL)
    response = urllib.request.urlopen(request)
    jsonified = json.loads(response.read().decode("utf-8"))
    return jsonified

#returns the json for the teams most recent event
def get_teamRecentEvent(team_num):
    teamEventHistory = get_teamEventHistory(team_num)
    mostRecent = 0
    mostRecentDate = 20000101 #this is the date taken from the TBA API, with the "-" removed. so '2000-01-01' becomes 20000101.20000101 has been chosen becasue it is earlier then any event history necessary 
    for i in range(len(teamEventHistory)):
        endDate = int((teamEventHistory[i]['end_date']).replace("-", ""))
        if endDate > mostRecentDate:
                      mostRecent = i
                      mostRecentDate = endDate
    return teamEventHistory[mostRecent]

#returns the json of the most Recent events' matches
def get_teamRecentEventMatches(team_num):
    teamRecentEvent = get_teamRecentEvent(team_num)
    eventcode = teamRecentEvent['key']

    #make the request
    request = urllib.request.Request(URL + 'team/frc' + str(team_num) +'/event/' + eventcode + '/matches')
    request.add_header(HEADER_KEY, HEADER_VAL)
    response = urllib.request.urlopen(request)
    jsonified = json.loads(response.read().decode("utf-8"))
    return jsonified


#returns the five most recent videos from the most recent event
def get_teamRecentVideos(team_num):
    teamRecentEventMatches = get_teamRecentEventMatches(team_num)
    videos = []
    for i in range(len(teamRecentEventMatches)):
        for x in range(len(teamRecentEventMatches[i]['videos'])):
            if teamRecentEventMatches[i]['videos'][x]['type'] == "youtube" and len(videos) < 5:
                videos.append('youtube.com/watch?v=' + teamRecentEventMatches[i]['videos'][x]['key'])
    videos = list(reversed(videos))
    return videos



#gets all the useful info for a team and returns it as a dictionary
def usefulInfo(team_num):
    #run all the other definitions once
    team = get_team(team_num)
    print("    Getting", team_num, "Event History")
    teamEventHistory = get_teamEventHistory(team_num)
    print("    Getting", team_num, "Recent Event")
    teamRecentEvent = get_teamRecentEvent(team_num)
    print("    Getting", team_num, "Recent Event Matches")
    teamRecentEventMatches = get_teamRecentEventMatches(team_num)
    print("    Getting", team_num, "Recent Videos")
    teamRecentVideos = get_teamRecentVideos(team_num)
    
    print("    Compiling Info for team", team_num)
    localUsefulInfo = {} #empty dictionary that will have everything added to it
    localUsefulInfo['team_number'] = team_num
    localUsefulInfo['name'] = team['nickname']
    
    #compute the average of their finales and quaterfinals games
    aveg = []
    avegTotal = 0
    for i in range(len(teamRecentEventMatches)):
        if teamRecentEventMatches[i]['comp_level'] == 'f' or teamRecentEventMatches[i]['comp_level'] == 'qf' or teamRecentEventMatches[i]['comp_level'] == 'sf' or teamRecentEventMatches[i]['comp_level'] == 'of':
            if ('frc' + str(team_num)) in teamRecentEventMatches[i]['alliances']['red']['teams']:
                aveg.append(teamRecentEventMatches[i]['alliances']['red']['score'])
                avegTotal += teamRecentEventMatches[i]['alliances']['red']['score']
            elif ('frc' + str(team_num)) in teamRecentEventMatches[i]['alliances']['blue']['teams']:
                aveg.append(teamRecentEventMatches[i]['alliances']['blue']['score'])
                avegTotal += teamRecentEventMatches[i]['alliances']['blue']['score']
    if avegTotal != 0:
        localUsefulInfo['avegF&QF'] = int(avegTotal/len(aveg))
    else:
        localUsefulInfo['avegF&QF'] = 0
    localUsefulInfo['videos'] = teamRecentVideos
    return localUsefulInfo

#used to be main(). reads all teams from 'prescout teams.txt' and generates the useful info for them
def teamsUsefulInfo():
    file = open('prescout teams.txt', 'r')
    teams = []
    for line in file:
        teams.append(int(line.strip()))
    info = []
    for team in teams:
        print("Getting info for ", str(team))
        try:
            info.append(usefulInfo(team))
        except urllib.error.HTTPError:
            print("ERROR: team dosen't exist, please remove team", str(team), "from file")
            print("ingoring team, and continuing on to next team")
    file.close()
    return info

def main():
    #opens and starts writing to 'prescout csv.csv'
    try:
        file = open('prescout csv.csv', 'w')
    except Exception:
        print("please close prescout csv, and start prescouting generator again")
        time.sleep(10)
    file.write(str('team num, name, avegF&QF, video1, video2, video3, video4, video5\n'))
    
    localteamsUsefulInfo = teamsUsefulInfo()

    try:
        for i in range(len(localteamsUsefulInfo)):
            print("Writing team " + str(localteamsUsefulInfo[i]['team_number']))

            file.write(str(str(localteamsUsefulInfo[i]['team_number']) + ', '))
            file.write(str(str(localteamsUsefulInfo[i]['name']) + ', '))
            file.write(str(localteamsUsefulInfo[i]['avegF&QF']))
            for x in range(len(localteamsUsefulInfo[i]['videos'])-1):
                file.write(str(', ' + str(localteamsUsefulInfo[i]['videos'][x])))
            file.writelines(str('\n'))
    except Exception:
        file.close
        raise

    print("Done!!!!")
    file.close

main() #runs program