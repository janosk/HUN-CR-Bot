# import all 


import discord
import requests
import json
import os
from datetime import datetime

#%% 
# info for bot
help_string= '''
Implemented features:
    - '!hello' - returns a 'nice' and 'friendly' greeting 
    - '!playerinfo <playertag>' - returns basic player info
    - '!claninfo <clantag>' - returns basic clan info
    - '!clanwar <clantag>' - return info about current clan river race
    - '!clanmembers <clantag>' - returns *very* detailed info on clan members
    - '!help' - returns basic help (which I think you've figured out)
    - '!botcheck <playertag>' - check if a player is a supercell created bot - Note: We do not take responsibility for the accuracy of this tool
    
Known Issues:
'''

#%% 

# Get all api keys from 'keys.csv'
# 'keys.csv' should have 5 values: {DiscordApiKey},{ClashRoyaleApiKey},{RedditBotId},{RedditBotSecret},{RedditUsername}. 
file = open('keys.csv','r')

# Read only the first line of 'keys.csv' (just incase there are more than 1 line)
all_keys = file.readlines()[0].split(',')


# Get Discord Api key from 'keys.csv'
TOKEN = all_keys[0]

# Get Clash Royale Api key from 'keys.csv'
clashroyale_TOKEN = all_keys[1]

# get basic card info from clash royale api and deserialize using json
clash_royale_cards = json.loads(requests.get('https://api.clashroyale.com/v1/cards/', headers={'Authorization':'Bearer '+clashroyale_TOKEN}).text)['items']

# launch discord client
client = discord.Client()


#%%
@client.event
# When the bot is ready, print out that it is ready with datetime it was logged in on 
async def on_ready():
    print(f'We have logged in as {client.user} on {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

@client.event
async def on_message(message):
    # if the message sender is the bot, just return
    if message.author == client.user:
        return
    
    # If the message starts with !hello or !Hello:
    if message.content.startswith('!hello') or message.content.startswith('!Hello'):
        
        # Send this nice greeting back:
        await message.channel.send('Hello! It\'s nice to meet you! I like to help you with your various tasks. It\'s refreshing to help other people!')
    
    # This function gives info about a Clash Royale player
    if message.content.startswith('!playerinfo'):
        # [11:] removes !playerinfo from string (it does this by removing the first 11 characters)
        # .strip() removes leading/trailing spaces
        # .title() capitalises each word
        temp_message = message.content[11:].strip()

        # This bit adds %23 to front of player tag (the proper encoding for #)
        if temp_message[0] == '#':
            # remove # if present
            temp_message = temp_message[1:]
        # add %23
        temp_message = '%23' + temp_message
        
        # Get player info using Clash royale api
        player = json.loads(requests.get('https://api.clashroyale.com/v1/players/'+temp_message, headers={'Authorization':'Bearer '+clashroyale_TOKEN}).text)

        current_deck = ''

        
        # This efficient bit of code here goes through each stat and sees if present, and then adds it to string to send to person
        
        try:
            # Find player's username, trophies and arena
            player_info = f'{player["name"]} is on {player["trophies"]} trophies in {player["arena"]["name"]}'
            
            try:
                # Find league statistics if present (account must've been above 4000 trophies the previous season)
                player_info += f', with a record of {player["leagueStatistics"]["currentSeason"]["bestTrophies"]} trophies this season and {player["bestTrophies"]} overall.\n'
            
            # if league statistics not available, skip it
            except KeyError:
                player_info +='.\n'
                
            try:
                # Get this season's league statistics (if present like above)
                player_info += f'Their best season so far was {player["leagueStatistics"]["bestSeason"]["id"]}, finishing with {player["leagueStatistics"]["bestSeason"]["trophies"]} trophies!\n'
            except KeyError:
                pass
            
            # Get player's username, king tower level, wins and losses
            player_info += f'{player["name"]} is currently King Tower {player["expLevel"]} with {player["wins"]} wins and {player["losses"]} losses, so far donating a generous {player["totalDonations"]} cards!\n'
            
            try:
                # Go through cards in each deck of last used deck
                for card_dict in player['currentDeck']:
                    # Add each card in deck to string
                    current_deck += ' level ' + str(card_dict['level'] - card_dict['maxLevel'] + 13) + ' ' + card_dict["name"] + ','
                    
                # Format all deck info in (doesn't add data if not found, just skips it(Key error))
                player_info += f'The last deck they used consists of{current_deck[:-1]} with {player["currentFavouriteCard"]["name"]} being their favourite card.\n'
            except KeyError:
                pass
            
            # Add link to profile at end of string
            player_info += f'Open profile in Clash Royale: https://link.clashroyale.com/?playerInfo?id={temp_message[3:]}'
            
            # Send full profile info to channel
            await message.channel.send(player_info)
        except KeyError:
            # Send error message to channel if player's arena/trophies/username isn't found
            await message.channel.send("Warning, player not found, you mortal")
        

    # Find a player's chest cycle
    if message.content.startswith('!chest'):
        # [6:] removes !chest from string (it does this by removing the first 6 characters)
        # .strip() removes leading/trailing spaces
        # .title() capitalises each word
        temp_message = message.content[6:].strip()
        
        # This bit adds %23 to front of player tag (the proper encoding for #)
        if temp_message[0] == '#':
            # removes # if present
            temp_message = temp_message[1:]
        # add '%23' in
        temp_message = '%23' + temp_message
        
        # Fetch player's chest cycle from Clash royale api
        player_chests = json.loads(requests.get('https://api.clashroyale.com/v1/players/'+temp_message + '/upcomingchests', headers={'Authorization':'Bearer '+clashroyale_TOKEN}).text)
        
        chest_list = []
            
        try:
            # For each chest in chest cycle
            for chest in player_chests['items']:
                # If there are less than 6 chests or the chest isn't silver/gold
                # This limits silver/gold chests to the first 6 chests (extra chests are better chests)
                if len(chest_list) < 6 or (chest["name"] != 'Silver Chest' and chest["name"]!= 'Golden Chest'):
                    # Add chest to list
                    chest_list.append(chest)
                    
            # Process first 6 chests into a string, removing them from the list each time
            chest_info = f'''
Your chests:
Next chest - {chest_list.pop(0)["name"]}
1 - {chest_list.pop(0)["name"]}
2 - {chest_list.pop(0)["name"]}
3 - {chest_list.pop(0)["name"]}
4 - {chest_list.pop(0)["name"]}
5 - {chest_list.pop(0)["name"]}
 '''
        
            # Cycle through remaining chests and add to chest_info string
            for chest in chest_list:
                # add chest
                chest_info += str(chest["index"]) + ' - ' + chest["name"] + "\n"
            
            # Send chest cycle info into channel
            await message.channel.send(chest_info)
       
        # Catch missing information
        except KeyError:
            await message.channel.send("Warning. Player not found")

    # Display help
    if message.content.startswith('!help'):
        # Sends help_string which is defined earlier in file
        await message.channel.send(help_string)

    # Get basic clan info 
    if message.content.startswith('!claninfo'):
        
        # [9:] removes !claninfo from string (it does this by removing the first 9 characters)
        # .strip() removes leading/trailing spaces
        # .title() capitalises each word
        temp_message = message.content[9:].strip()
        
        # This bit adds %23 to front of player tag (the proper encoding for #)
        if temp_message[0] == '#':
            # removes # if present
            temp_message = temp_message[1:]
        # adds '%23' in
        temp_message = '%23' + temp_message
        
        # Get clan info from clash royale api
        clan= json.loads(requests.get('https://api.clashroyale.com/v1/clans/'+temp_message, headers={'Authorization':'Bearer '+clashroyale_TOKEN}).text)
        
        try:
            # Format all clan info
            clan_info = f"""
{clan["name"]} is a clan with {clan["clanWarTrophies"]} war trophies, a clan score of {clan["clanScore"]} and {clan["donationsPerWeek"]} donations per week.
{clan["name"]} is a {clan["type"]} clan, requiring {clan["requiredTrophies"]} trophies to join.
There are currently {clan["members"]} members.
*{clan["description"]}*
Open clan in Clash Royale: {'https://link.clashroyale.com/?clanInfo?id='+temp_message[3:]}
"""
            # Send clan info into channel
            await message.channel.send(clan_info)   
            
        # Detect key errors - missing information
        except KeyError:
            await message.channel.send("Clan not found, there seems to be something wrong with the clan tag.")
        

       

    if message.content.startswith('!clanmembers'):
        temp_message = message.content[12:].strip()
        # format special # in
        if temp_message[0] == '#':
            # remove #
            temp_message = temp_message[1:]
        # add formatted # in
        temp_message = '%23' + temp_message
        
        # get clan info
        clan= json.loads(requests.get('https://api.clashroyale.com/v1/clans/'+temp_message +'/members', headers={'Authorization':'Bearer '+clashroyale_TOKEN}).text)
        
        # string has to be split due to 2000 character limit
        clan_member_info = ['']
        
        try:
            for member in clan['items']:
                # make sure each message doesn't exceed 2000 characters
                if len(clan_member_info[-1]) > 1500:
                       clan_member_info.append('')
                clan_member_info[-1] += f"{member['clanRank']}, {member['name']}, {member['role']}, {member['trophies']} trophies, {str(member['donations'] - member['donationsReceived'])} net donations, King Tower {member['expLevel']}, {member['tag']}\n"
                
            # add link to it
            clan_member_info.append('Open clan in Clash Royale: https://link.clashroyale.com/?clanInfo?id='+temp_message[3:])
    
            for clan_member_info_string in clan_member_info:
                await message.channel.send(clan_member_info_string)
                
            
        # Catch clans with missing data
        except KeyError:
            await message.channel.send("This clan doesn't exist")            
            
    if message.content.startswith('!clanwar'):
        temp_message = message.content[8:].strip()
        # format special # in
        if temp_message[0] == '#':
            # remove #
            temp_message = temp_message[1:]
        # add formatted # in
        temp_message = '%23' + temp_message
        
        # get clan war info
        clan= json.loads(requests.get('https://api.clashroyale.com/v1/clans/'+temp_message +'/currentriverrace', headers={'Authorization':'Bearer '+clashroyale_TOKEN}).text)

        # string has to be split due to 2000 character limit
        clan_war_info = ['']
        
        try:
            # add current war standings
            clan_war_standings = sorted(clan["clans"], key = lambda i: i['fame'])
            clan_war_standings.reverse()
            clan_war_info[0] += f'''
Current war standings:
    1st: {clan_war_standings[0]["name"]} - {clan_war_standings[0]["fame"]} fame - {clan_war_standings[0]["tag"]}
    2nd: {clan_war_standings[1]["name"]} - {clan_war_standings[1]["fame"]} fame - {clan_war_standings[1]["tag"]}
    3rd: {clan_war_standings[2]["name"]} - {clan_war_standings[2]["fame"]} fame - {clan_war_standings[2]["tag"]}
    4th: {clan_war_standings[3]["name"]} - {clan_war_standings[3]["fame"]} fame - {clan_war_standings[3]["tag"]}
    5th: {clan_war_standings[4]["name"]} - {clan_war_standings[4]["fame"]} fame - {clan_war_standings[4]["tag"]}                           

Current war participants in clan:
'''
            clan_war_participants = clan["clan"]["participants"]
            clan_war_participants.reverse()
            i = 1
            for member in clan_war_participants:
                # make sure each message doesn't exceed 2000 characters
                if len(clan_war_info[-1]) > 1500:
                       clan_war_info.append('')
                clan_war_info[-1] += f"{i}. {member['name']} - {member['fame']} fame - {member['repairPoints']} repair points - {member['tag']}\n"
                i+=1   
                
            clan_war_info.append('Note: Fame is currently counted past the 36000 finish line, which may create misleading results - view more info here at RoyaleApi\'s website: https://royaleapi.com/blog/clan-wars-2-tools#known-issues')
            for string in clan_war_info:
                await message.channel.send(string)
                
        # Catch missing information
        except KeyError:
            await message.channel.send("This clan either doesn't exist or doesn't do clan war.")
            
    # Check if player is bot - using method from Bailey OP's video
    if message.content.startswith('!botcheck'):
        # format message (see above somewhere)
        temp_message = message.content[9:].strip()

        if temp_message[0] == '#':
            # remove #
            temp_message = temp_message[1:]
        # add formatted # in
        temp_message = '%23' + temp_message
        # find player
        player = json.loads(requests.get('https://api.clashroyale.com/v1/players/'+temp_message, headers={'Authorization':'Bearer '+clashroyale_TOKEN}).text)

        try:
            # check if player has donations but have never joined a clan
            if player["totalDonations"] > 0 and next(item for item in player["achievements"] if item["name"] == "Team Player")["value"] ==0:
                
                await message.channel.send(player["name"] + ' seems to be a bot. They have ' + str(player["totalDonations"]) + ' donations, yet they have never joined a clan.')
            
            else:
                await message.channel.send(player["name"] + ' doesn\'t seem to be a Supercell created bot.')
                
        
        except KeyError:
            await message.channel.send("Warning, Player tag not found!!!!!!!!")
            
client.run(TOKEN)
    
    
