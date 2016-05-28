import urllib.request
import json

def makeRequest(extension):
    URL = "http://www.thebluealliance.com/api/v2/"
    request = urllib.request.Request(URL + extension)
    request.add_header('X-TBA-App-Id', 'frc4613:prescouting-generator:2')
    request.add_header('User-Agent', "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11)Gecko/20071127 Firefox/2.0.0.11")
    try:
        response = urllib.request.urlopen(request)
    except Exception as e:
        print(e.fp.read())
    jsonified = json.loads(response.read().decode("utf-8"))
    return jsonified

def main():
    teamList = open('prescout teams.txt', 'r')
    outputFile = open('prescout results.csv', 'w')
    outputFile.write(str('number, name, avegF&QF, avegQ, videos\n'))
    teams = []
    teamsInfo = []
    for line in teamList:
        teams.append(int(line.strip()))
    for team in teams:
        print("Getting info for ", str(team))

        #Nickname
        teamInfo = makeRequest(str("team/frc" + str(team)))
        teamNickname = teamInfo['nickname']

        #Make list of events attended ordered by date
        events = makeRequest(str("team/frc" + str(team) + "/2016/events"))
        eventList = []
        for event in events:
            endDate = int((event['end_date'].replace("-", "")))
            eventList.append([event['key'], endDate])
        eventList.sort(key = lambda x: int(x[1]), reverse=True)

        #Loop over events, and return the aveg quals & elims score as well as video links to all matches
        qualsScores = []
        elimsScores = []
        videos = []
        for event in eventList:
            matches = makeRequest(str("team/frc" + str(team) + "/event/" + str(event[0]) + "/matches"))
            for match in matches:
                if match["videos"] != [] and match["videos"][0]["type"] == 'youtube':
                    videoKey = match["videos"][0]["key"]
                    videoKey = videoKey.replace("?", "&")
                    videos.append([match["key"], ("www.youtube.com/watch?v=" + videoKey)])
                if match["comp_level"] in ["f", "sf", "qf", "ef"]:
                    if str("frc" + str(team)) in match["alliances"]["blue"]["teams"]:
                        elimsScores.append(match["alliances"]["blue"]["score"])
                    else:
                        elimsScores.append(match["alliances"]["red"]["score"])
                else:
                    if str("frc" + str(team)) in match["alliances"]["blue"]["teams"]:
                        qualsScores.append(match["alliances"]["blue"]["score"])
                    else:
                        qualsScores.append(match["alliances"]["red"]["score"])
        try:
            qualsAveg = sum(qualsScores)/float(len(qualsScores))
        except ZeroDivisionError:
            qualsAveg = ""
        try:
            elimsAveg = sum(elimsScores)/float(len(elimsScores))
        except ZeroDivisionError:
            elimsAveg = ""

        #write to file! yay!
        outputFile.write(str(str(team) + ', ' + teamNickname + ', ' + str(elimsAveg) + ', ' + str(qualsAveg)))
        for video in videos:
            outputFile.write(str(', ' + video[0] + ', ' + video[1]))
        outputFile.write('\n')
    outputFile.close()
    print("Done!")

def makeEventTeamList(event):
    print("Getting list")
    teams = makeRequest(str("event/" + event + "/teams"))
    print("Got list")
    outputFile = open('prescout teams.txt', 'w')
    print("Writing down teams")
    for team in teams:
        outputFile.write(str(str(team["team_number"]) + "\n"))
    print("Done!, shutting down...")
    outputFile.close()
    print("Finished")

#makeEventTeamList("2016cmp")
main()
