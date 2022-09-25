# HUN-CR-Bot
A Clash Royale Discord bot - originally forked from garamlee500 -A BIG KUDOS TO YOU!

# Features 
- A clash royale data cruncher, accessing player profiles, clan wars and more!
- An auto clash royale bot checker, to see if that player you just played against was a bot!
- An auto clash royale deck link decoder, to see what decks your friends are uploading!
- And more (sort of)! 

# Instructions for use
To run this from your own computer, you will need a [discord bot](https://discord.com/developers/applications/) and a [clash royale api key](https://developer.clashroyale.com/#/) .
Download this repository and create a file called 'config.json' in the same folder. 'keys.csv' should have 2 values: {DiscordApiKey},{ClashRoyaleApiKey}
You must install discord.py using pip on your computer.

Now run main.py to run the bot.

# Commands
- '!hello' - returns a 'nice' and 'friendly' greeting 
- '!playerinfo <playertag>' - returns basic player info
- '!claninfo <clantag>' - returns basic clan info
- '!clanwar <clantag>' - return info about current clan river race
- '!clanmembers <clantag>' - returns *very* detailed info on clan members
- '!help' - returns basic help (which I think you've figured out)
- '!botcheck <playertag>' - check if a player is a supercell created bot - Note: We do not take responsibility for the accuracy of this tool
- Post a clashroyale deck link to be decoded by the bot
